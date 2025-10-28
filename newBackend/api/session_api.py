#!/usr/bin/env python3
"""
会话管理 API
提供多会话、多任务支持的REST接口
"""

import os
import time
import logging
import re
from typing import Optional, List, Tuple
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from core.session_manager import (
    session_manager, 
    SessionStatus, 
    MessageType, 
    MessageSender
)
from core.concurrent_task_executor import task_executor, TaskStatus
from core.qwen_nlp_parser import DialogueManager
from persona.executor import PersonaAwareVideoOperationExecutor

logger = logging.getLogger(__name__)

# 创建视频操作执行器实例（输出到项目根目录的data/results目录）
# 计算项目根目录的绝对路径
from pathlib import Path
_project_root = Path(__file__).parent.parent.parent
_data_results_dir = _project_root / "data" / "results"
video_executor = PersonaAwareVideoOperationExecutor(output_dir=str(_data_results_dir))


# Pydantic 模型用于请求验证
class CreateSessionRequest(BaseModel):
    title: Optional[str] = None
    icon: str = "🎬"
    
    class Config:
        extra = "forbid"  # 禁止额外字段


class UpdateSessionRequest(BaseModel):
    session_id: str
    title: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        extra = "forbid"  # 禁止额外字段


class AddMessageRequest(BaseModel):
    session_id: str
    content: str
    message_type: str = "text"
    sender: str = "user"
    media_path: Optional[str] = None


class ProcessTaskRequest(BaseModel):
    session_id: str
    text: str
    execute_now: bool = True


# 创建 FastAPI 应用
session_app = FastAPI(title="会话管理 API")


@session_app.get("/")
async def root():
    """根路径 - API状态检查"""
    return {
        "status": "ok",
        "message": "CoEdit 后端服务运行中",
        "api_docs": "/docs",
        "version": "1.0.0"
    }


@session_app.post("/sessions/create")
async def create_session(request: CreateSessionRequest):
    """
    创建新会话（单用户模式）
    
    Args:
        title: 会话标题（可选）
        icon: 会话图标
        
    Returns:
        创建的会话信息
    """
    try:
        session = session_manager.create_session(
            title=request.title,
            icon=request.icon
        )
        
        session_dict = session.to_dict()
        return {
            "status": "success",
            "message": "会话创建成功",
            "session_id": session_dict["id"],  # 添加顶层 session_id 方便访问
            "session": session_dict             # 保留完整对象用于详细信息
        }
    except Exception as e:
        logger.exception("创建会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    获取会话详情
    
    Args:
        session_id: 会话ID
        
    Returns:
        会话信息
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "status": "success",
            "session": session.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/sessions")
async def get_all_sessions():
    """
    获取所有会话（单用户模式）
    
    Returns:
        会话列表
    """
    try:
        sessions = session_manager.get_all_sessions()
        
        return {
            "status": "success",
            "count": len(sessions),
            "sessions": [s.to_dict() for s in sessions]
        }
    except Exception as e:
        logger.exception("获取会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.put("/sessions/update")
async def update_session(request: UpdateSessionRequest):
    """
    更新会话信息
    
    Args:
        session_id: 会话ID
        title: 新标题
        status: 新状态
        
    Returns:
        更新结果
    """
    try:
        # 验证status值（如果提供）
        status_enum = None
        if request.status:
            try:
                status_enum = SessionStatus(request.status)
            except ValueError:
                raise HTTPException(
                    status_code=422, 
                    detail=f"无效的状态值: {request.status}. 有效值: active, idle, processing, completed, error"
                )
        
        success = session_manager.update_session(
            session_id=request.session_id,
            title=request.title,
            status=status_enum
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "status": "success",
            "message": "会话更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("更新会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.delete("/sessions/all")
async def delete_all_sessions():
    """
    删除所有会话（单用户模式）
        
    Returns:
        删除数量
    """
    try:
        count = session_manager.delete_all_sessions()
        
        return {
            "status": "success",
            "message": f"已删除 {count} 个会话",
            "count": count
        }
    except Exception as e:
        logger.exception("删除所有会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        删除结果
    """
    try:
        success = session_manager.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 同时清理该会话的所有任务
        task_executor.clear_completed_tasks(session_id)
        
        return {
            "status": "success",
            "message": "会话删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("删除会话失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.post("/sessions/add_message")
async def add_message(request: AddMessageRequest):
    """
    向会话添加消息
    
    Args:
        session_id: 会话ID
        content: 消息内容
        message_type: 消息类型
        sender: 发送者
        media_path: 媒体路径
        
    Returns:
        添加的消息
    """
    try:
        message = session_manager.add_message_to_session(
            session_id=request.session_id,
            content=request.content,
            message_type=MessageType(request.message_type),
            sender=MessageSender(request.sender),
            media_path=request.media_path
        )
        
        if not message:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "status": "success",
            "message": message.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("添加消息失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.post("/sessions/process-multimodal")
async def process_multimodal_in_session(
    session_id: str = Form(...),
    text: str = Form(...),
    video: Optional[UploadFile] = File(None),
    images: List[UploadFile] = File(default=[]),  # 修改：使用默认空列表而不是None
    execute_async: str = Form("false")  # 修改为字符串类型，前端发送的是 "true"/"false"
):
    """
    在会话中处理多模态输入
    
    Args:
        session_id: 会话ID
        text: 文本指令
        video: 视频文件
        images: 图片文件列表
        execute_async: 是否异步执行
        
    Returns:
        处理结果
    """
    try:
        # 验证会话存在
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 保存上传的文件（统一存储到项目根目录的data目录）
        video_path = None
        image_paths = []
        # 使用项目根目录的data文件夹
        _base_data_dir = Path(__file__).parent.parent.parent / "data"
        upload_folder = _base_data_dir / "sessions" / session_id / "uploads"
        upload_folder.mkdir(parents=True, exist_ok=True)
        upload_folder_str = str(upload_folder)
        
        # 保存视频
        if video and video.filename:
            video_filename = f"video_{int(time.time())}_{video.filename}"
            video_path = str(upload_folder / video_filename)
            with open(video_path, 'wb') as f:
                content = await video.read()
                f.write(content)
            logger.info(f"视频已保存: {video_path}")
        
        # 保存图片
        if images:
            for idx, img in enumerate(images):
                if img and img.filename:
                    img_filename = f"image_{int(time.time())}_{idx}_{img.filename}"
                    img_path = str(upload_folder / img_filename)
                    with open(img_path, 'wb') as f:
                        content = await img.read()
                        f.write(content)
                    image_paths.append(img_path)
        
        # 添加用户消息到会话
        user_msg = session_manager.add_message_to_session(
            session_id=session_id,
            content=text,
            message_type=MessageType.MULTIMODAL if (video_path or image_paths) else MessageType.TEXT,
            sender=MessageSender.USER,
            media_path=video_path,
            metadata={"image_paths": image_paths}
        )
        
        # 更新会话状态
        session_manager.update_session(
            session_id=session_id,
            status=SessionStatus.PROCESSING,
            current_video=video_path
        )
        
        # 创建DialogueManager实例处理输入
        dialogue_manager = DialogueManager()
        
        # 定义任务函数
        def process_task():
            # 1. 先使用 DialogueManager 解析用户指令
            # 注意：对于大视频(>20MB)，只传递文本指令给千问，避免API错误
            # 视频文件路径会在后续视频编辑时使用
            result = dialogue_manager.process_multimodal_input(
                text=text,
                image_paths=image_paths if image_paths else None,
                video_paths=None  # 不传递视频路径给千问API，只解析文本指令
            )
            
            output_path = None
            media_url = None
            output_type = None  # 'video' 或 'image'
            
            # 2. 如果解析成功，执行操作（视频编辑或AI生成）
            # 注意：文生视频/文生图等操作不需要input_video
            if result.get("success") and result.get("action"):
                try:
                    import json
                    action_content = result.get("action", "")
                    
                    # 移除可能的 "action:" 前缀
                    if action_content.startswith("action:"):
                        action_content = action_content[7:].strip()
                    
                    # 解析JSON操作指令
                    operation_json = json.loads(action_content)
                    operation_name = operation_json.get("operations", {}).get("operation", "")
                    logger.info(f"🎬 执行操作: {operation_name}")
                    logger.info(f"   操作详情: {operation_json}")
                    
                    # 执行操作（video_path可能为None，对于文生视频/文生图操作）
                    exec_result = video_executor.execute_from_json(
                        operation_json,
                        input_video=video_path  # 文生视频时为None也没问题
                    )
                    
                    logger.info(f"执行结果: success={exec_result.success}, output_path={exec_result.output_path}, error={exec_result.error_message}")
                    
                    if exec_result.success and exec_result.output_path:
                        output_path = exec_result.output_path
                        
                        # 判断输出类型（图片还是视频）
                        file_ext = os.path.splitext(output_path)[1].lower()
                        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                            output_type = 'image'
                            logger.info(f"✅ 图片生成成功: {output_path}")
                        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                            output_type = 'video'
                            logger.info(f"✅ 视频处理成功: {output_path}")
                        else:
                            output_type = 'video'  # 默认为视频
                            logger.info(f"✅ 文件生成成功: {output_path}")
                        
                        # 生成可访问的URL（相对于项目根目录data文件夹的路径）
                        _project_root = Path(__file__).parent.parent.parent
                        _data_dir = _project_root / "data"
                        relative_path = os.path.relpath(output_path, str(_data_dir))
                        media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                        
                        logger.info(f"✅ 可访问URL: {media_url}")
                    else:
                        logger.error(f"❌ 操作失败: {exec_result.error_message}")
                    
                    # 更新结果
                    result["execution"] = {
                        "success": exec_result.success,
                        "output_path": output_path,
                        "media_url": media_url,
                        "video_url": media_url,  # 保持向后兼容
                        "output_type": output_type,
                        "error_message": exec_result.error_message,
                        "operation_name": exec_result.operation_name,
                        "execution_time": exec_result.execution_time
                    }
                    
                except Exception as e:
                    logger.error(f"❌ 执行视频操作异常: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    result["execution"] = {
                        "success": False,
                        "error_message": f"执行操作失败: {str(e)}"
                    }
            
            # 3. 添加助手回复到会话
            assistant_content = result.get("response", "")
            
            # 检查是否实际执行了操作
            if not result.get("action") or result.get("action") == "None":
                # 千问无法理解/不支持该操作
                logger.warning(f"⚠️ 千问无法解析操作，action为空或None")
                assistant_content = (
                    "抱歉，我还不太理解这个操作。\n\n"
                    "您可以尝试：\n"
                    "• 裁剪视频（如\"裁剪前5秒\"）\n"
                    "• 调整速度（如\"加速2倍\"）\n"
                    "• 生成视频（如\"生成一个小猫奔跑的视频\"）\n"
                    "• 生成图片（如\"画一朵玉兰花\"）\n"
                    "• 或者换一种表述方式"
                )
            elif output_path and output_type:
                if output_type == 'image':
                    assistant_content += f"\n\n✨ 图片已生成完成！"
                else:
                    assistant_content += f"\n\n🎬 视频已处理完成！"
            
            # 根据输出类型选择消息类型
            message_type = MessageType.SYSTEM
            if output_path:
                if output_type == 'image':
                    message_type = MessageType.IMAGE
                else:
                    message_type = MessageType.VIDEO
            
            session_manager.add_message_to_session(
                session_id=session_id,
                content=assistant_content,
                message_type=message_type,
                sender=MessageSender.ASSISTANT,
                media_path=output_path,
                metadata={
                    "action": result.get("action"),
                    "media_url": media_url,
                    "video_url": media_url,  # 保持向后兼容
                    "output_type": output_type
                }
            )
            
            # 4. 更新会话状态
            session_manager.update_session(
                session_id=session_id,
                status=SessionStatus.ACTIVE
            )
            
            # 5. 确保返回值包含output_path和media_url（用于任务执行器提取）
            if result.get("execution"):
                result["output_path"] = result["execution"].get("output_path")
                result["media_url"] = result["execution"].get("media_url")
                result["video_url"] = result["execution"].get("video_url")  # 保持向后兼容
                result["output_type"] = result["execution"].get("output_type")
            
            return result
        
        # 如果是异步执行（将字符串转换为布尔值）
        is_async = execute_async.lower() in ('true', '1', 'yes')
        logger.info(f"处理多模态输入: {'text' if text else 'no-text'}")
        
        if is_async:
            task_id = task_executor.submit_task(
                session_id=session_id,
                task_func=process_task,
                metadata={
                    "text": text,
                    "video_path": video_path,
                    "image_count": len(image_paths)
                }
            )
            
            return {
                "status": "success",
                "message": "任务已提交，请轮询任务状态获取结果",
                "task_id": task_id,
                "session_id": session_id,
                "async": True
            }
        else:
            # 同步执行
            result = process_task()
            
            # 提取执行结果
            execution = result.get("execution", {})
            
            return {
                "status": "success",
                "message": "处理完成",
                "modal_type": result.get("modal_type", "text"),
                "response": result.get("response", ""),
                "action": result.get("action"),
                "session_id": session_id,
                "async": False,
                # 媒体URL字段（支持图片和视频）
                "media_url": execution.get("media_url"),
                "video_url": execution.get("video_url"),  # 保持向后兼容
                "output_path": execution.get("output_path"),
                "output_type": execution.get("output_type"),
                "execution": execution
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("处理多模态输入失败")
        # 恢复会话状态
        session_manager.update_session(
            session_id=session_id,
            status=SessionStatus.ERROR
        )
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态和结果
    """
    try:
        result = task_executor.get_task_result(task_id)
        if not result:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 生成可访问的媒体URL（支持图片和视频）
        media_url = None
        output_type = None
        if result.output_path and os.path.exists(result.output_path):
            try:
                # 判断输出类型
                file_ext = os.path.splitext(result.output_path)[1].lower()
                if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    output_type = 'image'
                elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    output_type = 'video'
                else:
                    output_type = 'video'  # 默认为视频
                
                _project_root = Path(__file__).parent.parent.parent
                _data_dir = _project_root / "data"
                relative_path = os.path.relpath(result.output_path, str(_data_dir))
                media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                logger.info(f"生成媒体URL ({output_type}): {media_url}")
            except ValueError:
                # 如果路径不在data目录下，尝试从execution结果中获取
                logger.warning(f"输出路径不在data目录: {result.output_path}")
                if hasattr(result, 'result') and isinstance(result.result, dict):
                    execution = result.result.get('execution', {})
                    media_url = execution.get('media_url') or execution.get('video_url')
                    output_type = execution.get('output_type', 'video')
        
        return {
            "status": "success",
            "task": {
                "task_id": result.task_id,
                "session_id": result.session_id,
                "status": result.status.value,
                "output_path": result.output_path,
                "media_url": media_url,
                "video_url": media_url,  # 保持向后兼容
                "output_type": output_type,
                "error_message": result.error_message,
                "execution_time": result.execution_time,
                "metadata": result.metadata
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取任务状态失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/sessions/{session_id}/tasks")
async def get_session_tasks(session_id: str):
    """
    获取会话的所有任务
    
    Args:
        session_id: 会话ID
        
    Returns:
        任务列表
    """
    try:
        tasks = task_executor.get_session_tasks(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "count": len(tasks),
            "tasks": [
                {
                    "task_id": result.task_id,
                    "status": result.status.value,
                    "output_path": result.output_path,
                    "execution_time": result.execution_time
                }
                for result in tasks.values()
            ]
        }
    except Exception as e:
        logger.exception("获取会话任务失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        取消结果
    """
    try:
        success = task_executor.cancel_task(task_id)
        
        if not success:
            return {
                "status": "warning",
                "message": "任务无法取消（可能已完成或不存在）"
            }
        
        return {
            "status": "success",
            "message": "任务已取消"
        }
    except Exception as e:
        logger.exception("取消任务失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/executor/stats")
async def get_executor_stats():
    """
    获取执行器统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = task_executor.get_executor_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.exception("获取执行器统计失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/health")
async def health_check():
    """健康检查"""
    session_count = session_manager.get_session_count()
    executor_stats = task_executor.get_executor_stats()
    
    return {
        "status": "ok",
        "session_count": session_count,
        "running_tasks": executor_stats["running"],
        "available_workers": executor_stats["available_workers"]
    }


def _parse_range(range_header: str, file_size: int) -> Tuple[int, int]:
    """解析HTTP Range请求头"""
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


@session_app.get("/media/{path:path}")
async def serve_media_file(path: str, request: Request):
    """
    提供媒体文件服务（视频、图片等）
    支持Range请求实现断点续传和流式播放
    
    Args:
        path: 文件路径（相对于data目录）
        
    Returns:
        媒体文件流
    """
    try:
        # 安全检查：防止路径遍历攻击
        if ".." in path or path.startswith("/"):
            raise HTTPException(status_code=400, detail="非法的文件路径")
        
        # 构建完整路径（在项目根目录的data文件夹下查找）
        _project_root = Path(__file__).parent.parent.parent
        base_dir = _project_root / "data"
        file_path = str(base_dir / path)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 如果在data目录找不到，尝试在Results目录查找（兼容旧代码）
            alt_path = os.path.join("Results", os.path.basename(path))
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                logger.warning(f"文件不存在: {file_path}")
                raise HTTPException(status_code=404, detail="文件不存在")
        
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get('range') or request.headers.get('Range')
        
        # 判断MIME类型
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
            media_type = "video/mp4"
        elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            media_type = "image/jpeg"
        else:
            media_type = "application/octet-stream"
        
        # 处理Range请求（用于视频流式播放）
        if range_header:
            byte1, byte2 = _parse_range(range_header, file_size)
            length = byte2 - byte1 + 1
            
            def iter_file(path: str, start: int, length: int):
                with open(path, 'rb') as f:
                    f.seek(start)
                    remaining = length
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while remaining > 0:
                        read_size = min(chunk_size, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            headers = {
                "Content-Type": media_type,
                "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(length),
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Range"
            }
            return StreamingResponse(
                iter_file(file_path, byte1, length), 
                status_code=206, 
                headers=headers
            )
        
        # 无Range请求，返回完整文件
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
        return StreamingResponse(
            iter_full(file_path), 
            media_type=media_type, 
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("访问媒体文件失败")
        raise HTTPException(status_code=500, detail=str(e))

