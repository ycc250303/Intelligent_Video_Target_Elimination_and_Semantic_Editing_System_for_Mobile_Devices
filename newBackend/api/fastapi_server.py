import os
import re
import socket
import logging
import time
from typing import Optional, Tuple, List

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

# 第三方网络接口枚举（获取本机网卡IP列表）
try:
    import netifaces
except Exception:  # 兼容无 netifaces 场景
    netifaces = None


# 导入本地模块
from core.qwen_nlp_parser import DialogueManager
from config.config import OPERATIONS
from VideoEditor.ffmpeg_editor import FFmpegVideoEditor
from persona.executor import PersonaAwareVideoOperationExecutor
from core.multimodal_processor import MultimodalProcessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_ip_addresses() -> list:
    ip_list = []
    if netifaces is None:
        # 回退：仅返回本机主机名解析的地址
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if not ip.startswith("127."):
                ip_list.append((hostname, ip))
        except Exception:
            pass
        return ip_list

    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr.get('addr')
                if ip and not ip.startswith('127.'):
                    ip_list.append((interface, ip))
    return ip_list


class FileManager:
    def __init__(self):
        self.file_counter = 0
        self.filename_map = {}  # 原始文件名 -> 简化文件名
        self.reverse_map = {}   # 简化文件名 -> 原始文件名

    def get_simplified_name(self, original_filename: str) -> str:
        if original_filename in self.filename_map:
            return self.filename_map[original_filename]
        self.file_counter += 1
        simplified_name = f"{self.file_counter:03d}.mp4"
        self.filename_map[original_filename] = simplified_name
        self.reverse_map[simplified_name] = original_filename
        return simplified_name

    def get_original_name(self, simplified_name: str) -> Optional[str]:
        return self.reverse_map.get(simplified_name)

    def has_file(self, original_filename: str) -> bool:
        return original_filename in self.filename_map

# 文件管理器实例
file_manager = FileManager()
# 对话管理器实例
dialogue_manager = DialogueManager()
# 视频操作执行器实例（使用项目根目录的data/results目录）
from pathlib import Path
_project_root = Path(__file__).parent.parent.parent
_data_results_dir = _project_root / "data" / "results"
video_executor = PersonaAwareVideoOperationExecutor(output_dir=str(_data_results_dir))
# 多模态处理器实例
multimodal_processor = MultimodalProcessor()


app = FastAPI(title="ClipPersona API Server (FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {
        "message": "ClipPersona API Server (FastAPI)",
        "endpoints": {
            "health_check": "/health-check",
            "upload_video": "/upload-video",
            "process_video": "/process-video",
            "check_file": "/check-file",
            "serve_video": "/uploads/{filename}"
        }
    }


@app.get("/health-check")
def health_check(request: Request):
    client_ip = request.client.host if request.client else None
    logger.info(f"收到健康检查请求，来自: {client_ip}")
    return {"status": "ok", "message": "服务器运行正常", "client_ip": client_ip}


def _ensure_upload_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"创建上传目录: {path}")


@app.post("/upload-video")
async def upload_video(video: UploadFile = File(...)):
    try:
        logger.info("收到视频上传请求")
        if not video.filename:
            raise HTTPException(status_code=400, detail="未选择文件")

        original_filename = video.filename
        if not original_filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".wmv")):
            raise HTTPException(status_code=400, detail="不支持的文件类型，请上传视频文件")

        simplified_name = file_manager.get_simplified_name(original_filename)
        upload_folder = 'uploads'
        _ensure_upload_dir(upload_folder)
        file_path = os.path.join(upload_folder, simplified_name)

        # 保存文件
        logger.info(f"开始保存文件: {file_path}")
        with open(file_path, 'wb') as f:
            while True:
                chunk = await video.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="文件保存失败")

        return {
            "status": "success",
            "message": "视频上传成功",
            "file_path": file_path,
            "simplified_name": simplified_name,
            "file_size": os.path.getsize(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("上传视频时出错")
        raise HTTPException(status_code=500, detail=str(e))


def _parse_range(range_header: str, file_size: int) -> Tuple[int, int]:
    byte1, byte2 = 0, None
    match = re.search(r'bytes=(\d+)-(\d*)', range_header)
    if match:
        g1, g2 = match.groups()
        if g1:
            byte1 = int(g1)
        if g2:
            byte2 = int(g2)
    if byte2 is None:
        byte2 = file_size - 1
    if byte1 > byte2 or byte2 >= file_size:
        raise HTTPException(status_code=416, detail="无效的Range请求")
    return byte1, byte2


@app.get("/uploads/{filename}")
def serve_video(filename: str, request: Request):
    try:
        video_path = os.path.join('uploads', filename)
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        file_size = os.path.getsize(video_path)
        range_header = request.headers.get('range') or request.headers.get('Range')

        if range_header:
            byte1, byte2 = _parse_range(range_header, file_size)
            length = byte2 - byte1 + 1

            def iter_file(path: str, start: int, length: int):
                with open(path, 'rb') as f:
                    f.seek(start)
                    remaining = length
                    chunk_size = 1024 * 1024
                    while remaining > 0:
                        read_size = min(chunk_size, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Range"
            }
            return StreamingResponse(iter_file(video_path, byte1, length), status_code=206, headers=headers)

        # 无 Range，返回完整
        def iter_full(path: str):
            with open(path, 'rb') as f:
                while True:
                    data = f.read(1024 * 1024)
                    if not data:
                        break
                    yield data

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Range"
        }
        return StreamingResponse(iter_full(video_path), media_type="video/mp4", headers=headers)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("访问视频文件失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-video")
async def process_video(video: UploadFile = File(...), instruction: str = Form(...)):
    try:
        if not video.filename:
            raise HTTPException(status_code=400, detail="未选择文件")

        original_filename = video.filename
        simplified_name = file_manager.get_simplified_name(original_filename)

        upload_folder = 'uploads'
        _ensure_upload_dir(upload_folder)
        video_path = os.path.join(upload_folder, simplified_name)

        # 若文件不存在则保存
        if not os.path.exists(video_path):
            with open(video_path, 'wb') as f:
                while True:
                    chunk = await video.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            logger.info(f"视频保存成功: {video_path} (原始文件名: {original_filename})")

        # 执行指令
        dialogue_manager.set_current_video(video_path)
        action, confirmation, _ = process_instruction(instruction)

        if not action:
            raise HTTPException(status_code=400, detail="未解析到可执行操作")

        clean_action = action.replace("assistant:", "").strip() if action.startswith("assistant:") else action

        # 解析操作类型与编辑器
        action_parts = clean_action.strip().split()
        if len(action_parts) < 2:
            raise HTTPException(status_code=400, detail="操作指令格式错误")

        operation_name = action_parts[1]
        editor_type = None
        for part in action_parts:
            if part.startswith('editor='):
                editor_type = part.split('=')[1]
                break

        # 使用FFmpeg编辑器（目前仅支持FFmpeg）
        editor = FFmpegVideoEditor(video_path)
        logger.info(f"使用FFmpeg编辑器处理操作: {operation_name}")

        try:
            success = editor.execute_action(clean_action, OPERATIONS)
            if not success:
                raise HTTPException(status_code=400, detail="操作执行失败，请检查参数是否正确")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"执行操作时发生异常: {e}")
            raise HTTPException(status_code=400, detail=f"操作执行失败: {str(e)}")

        # 保存输出
        output_simplified_name = f"output_{simplified_name}"
        output_path = os.path.join(upload_folder, output_simplified_name)
        editor.output_path = output_path
        editor.save()
        editor.close()

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="处理后的视频文件未生成")

        video_url = f"/uploads/{output_simplified_name}"
        logger.info(f"视频处理完成，输出URL: {video_url}")
        logger.info("所有处理都在电脑端完成，避免了手机端字体兼容性问题")

        return {
            "status": "success",
            "message": "视频处理完成，已在电脑端生成目标视频",
            "output_path": video_url,
            "simplified_name": output_simplified_name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("处理请求时出错")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-file")
async def check_file(payload: dict):
    try:
        filename = payload.get('filename') if payload else None
        if not filename:
            raise HTTPException(status_code=400, detail="未提供文件名")

        is_uploaded = file_manager.has_file(filename)
        if is_uploaded:
            simplified_name = file_manager.get_simplified_name(filename)
            return {"status": "success", "exists": True, "simplified_name": simplified_name}
        else:
            return {"status": "success", "exists": False}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _print_startup_help(port: int = 8000) -> None:
    print("\n" + "=" * 50)
    print("服务器启动配置:")
    print("=" * 50)
    ip_addresses = get_all_ip_addresses()
    print("\n可用的网络接口和IP地址:")
    for interface, ip in ip_addresses:
        print(f"接口: {interface}")
        print(f"IP地址: {ip}")
        print("-" * 30)
    print("\n请尝试使用以上任一IP地址访问服务器")
    print(f"端口: {port}")
    print("\n提示:")
    print("1. 请确保手机和电脑在同一网络下")
    print("2. 依次尝试使用上述每个IP地址")
    print("3. 在手机浏览器中访问 http://[IP地址]:8000/health-check")
    print("4. 如果仍然无法访问，请检查防火墙设置")
    print("=" * 50 + "\n")


@app.post("/generate-video-from-image")
async def generate_video_from_image(
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    """
    从图片生成视频的API端点
    Args:
        image: 上传的图片文件
        prompt: 视频生成提示词
    """
    try:
        logger.info("收到图片转视频请求")
        
        if not image.filename:
            raise HTTPException(status_code=400, detail="未选择图片文件")
        
        # 检查文件类型
        if not image.filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif")):
            raise HTTPException(status_code=400, detail="不支持的文件类型，请上传图片文件")
        
        # 读取图片内容并转换为Base64
        image_content = await image.read()
        import base64
        import mimetypes
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(image.filename)
        if not mime_type or not mime_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="无法识别的图片格式")
        
        # 转换为Base64
        base64_data = base64.b64encode(image_content).decode('utf-8')
        img_url = f"data:{mime_type};base64,{base64_data}"
        
        logger.info(f"开始生成视频，提示词: {prompt}")
        
        # 调用视频生成函数
        video_path = video_executor.qwen_editor.make_video_by_first_frame(
            img_url=img_url, 
            prompt=prompt
        )
        
        if video_path:
            return {
                "status": "success",
                "message": "视频生成成功",
                "video_path": video_path,
                "prompt": prompt
            }
        else:
            raise HTTPException(status_code=500, detail="视频生成失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("生成视频时出错")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-multimodal")
async def process_multimodal(
    text: str = Form(...),
    video: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    execute_operation: bool = Form(False)
):
    """
    处理多模态输入（文本+图片+视频）
    
    Args:
        text: 文本指令
        video: 视频文件（可选）
        images: 图片文件列表（可选）
        execute_operation: 是否执行操作（默认False，仅解析）
        
    Returns:
        JSON响应包含解析结果和（可选）执行结果
    """
    try:
        logger.info(f"收到多模态处理请求: text={text}, video={video.filename if video else None}, images={len(images) if images else 0}")
        
        # 保存上传的文件
        video_path = None
        image_paths = []
        upload_folder = 'uploads/multimodal'
        _ensure_upload_dir(upload_folder)
        
        # 保存视频
        if video and video.filename:
            video_filename = f"video_{int(time.time())}_{video.filename}"
            video_path = os.path.join(upload_folder, video_filename)
            with open(video_path, 'wb') as f:
                content = await video.read()
                f.write(content)
            logger.info(f"视频已保存: {video_path}")
        
        # 保存图片
        if images:
            for idx, img in enumerate(images):
                if img and img.filename:
                    img_filename = f"image_{int(time.time())}_{idx}_{img.filename}"
                    img_path = os.path.join(upload_folder, img_filename)
                    with open(img_path, 'wb') as f:
                        content = await img.read()
                        f.write(content)
                    image_paths.append(img_path)
                    logger.info(f"图片已保存: {img_path}")
        
        # 处理多模态输入
        result = dialogue_manager.process_multimodal_input(
            text=text,
            image_paths=image_paths if image_paths else None,
            video_paths=[video_path] if video_path else None
        )
        
        response_data = {
            "status": "success",
            "modal_type": result.get("modal_type", "text"),
            "response": result.get("response", ""),
            "success": result.get("success", False),
            "action": result.get("action")
        }
        
        # 如果需要执行操作且解析成功
        if execute_operation and result.get("success") and result.get("action"):
            try:
                # 提取JSON并执行
                import json
                action_content = result.get("action", "")
                
                # 解析操作JSON
                if action_content.startswith("action:"):
                    action_content = action_content[7:].strip()
                
                operation_json = json.loads(action_content)
                
                # 执行操作
                if video_path:
                    exec_result = video_executor.execute_from_json(
                        operation_json,
                        input_video=video_path
                    )
                    
                    response_data["execution"] = {
                        "success": exec_result.success,
                        "output_path": exec_result.output_path,
                        "error_message": exec_result.error_message,
                        "operation_name": exec_result.operation_name,
                        "execution_time": exec_result.execution_time
                    }
                else:
                    response_data["execution"] = {
                        "success": False,
                        "error_message": "没有视频文件，无法执行操作"
                    }
                    
            except Exception as e:
                logger.error(f"执行操作失败: {e}")
                response_data["execution"] = {
                    "success": False,
                    "error_message": f"执行操作失败: {str(e)}"
                }
        
        return response_data
        
    except Exception as e:
        logger.exception("处理多模态输入时出错")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-operation-json")
async def execute_operation_json(
    operation_json: str = Form(...),
    video: UploadFile = File(...)
):
    """
    根据JSON执行视频操作
    
    Args:
        operation_json: 操作JSON字符串
        video: 输入视频文件
        
    Returns:
        执行结果
    """
    try:
        logger.info("收到JSON操作执行请求")
        
        # 保存视频
        upload_folder = 'uploads/operations'
        _ensure_upload_dir(upload_folder)
        
        video_filename = f"input_{int(time.time())}_{video.filename}"
        video_path = os.path.join(upload_folder, video_filename)
        
        with open(video_path, 'wb') as f:
            content = await video.read()
            f.write(content)
        
        logger.info(f"输入视频已保存: {video_path}")
        
        # 执行操作
        import json
        operation_data = json.loads(operation_json)
        
        result = video_executor.execute_from_json(
            operation_data,
            input_video=video_path
        )
        
        return {
            "status": "success" if result.success else "error",
            "success": result.success,
            "output_path": result.output_path,
            "error_message": result.error_message,
            "operation_name": result.operation_name,
            "execution_time": result.execution_time,
            "metadata": result.metadata
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise HTTPException(status_code=400, detail=f"JSON格式错误: {str(e)}")
    except Exception as e:
        logger.exception("执行操作时出错")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/operation-history")
def get_operation_history():
    """获取操作历史"""
    try:
        history = video_executor.operation_history
        return {
            "status": "success",
            "count": len(history),
            "history": [
                {
                    "success": r.success,
                    "operation_name": r.operation_name,
                    "output_path": r.output_path,
                    "execution_time": r.execution_time,
                    "error_message": r.error_message
                }
                for r in history
            ]
        }
    except Exception as e:
        logger.exception("获取操作历史时出错")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    _print_startup_help(port=8000)
    try:
        import uvicorn
        uvicorn.run(
            "fastapi_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"\n启动服务器时出错: {e}")
        print("请检查端口 8000 是否被占用")

