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
from config.demo_config import get_demo_video_path, is_demo_mode_enabled
from core.generate_image import generate_style_card_image

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
    """根路径 - 获取所有会话（单用户模式）"""
    try:
        sessions = session_manager.get_all_sessions()
        sessions_dict = [session.to_dict() for session in sessions]
        return {
            "status": "ok",
            "message": "CoEdit 后端服务运行中",
            "sessions": sessions_dict,
            "count": len(sessions_dict),
            "api_docs": "/docs",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.exception("获取会话列表失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.post("/create")
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


@session_app.get("/{session_id}")
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



@session_app.put("/update")
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


@session_app.delete("/all")
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


@session_app.delete("/{session_id}")
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


@session_app.post("/add_message")
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


@session_app.post("/process-multimodal")
async def process_multimodal_in_session(
    session_id: str = Form(...),
    text: str = Form(...),
    video: Optional[UploadFile] = File(None),
    images: List[UploadFile] = File(default=[]),  # 修改：使用默认空列表而不是None
    execute_async: str = Form("false"),  # 修改为字符串类型，前端发送的是 "true"/"false"
    function_name: Optional[str] = Form(None),  # 可选：直接指定函数名（用于风格卡应用）
    function_params: Optional[str] = Form(None),  # 可选：函数参数JSON字符串
    style_card_name: Optional[str] = Form(None)  # 可选：风格卡名称（用于Demo模式检测）
):
    """
    在会话中处理多模态输入
    
    Args:
        session_id: 会话ID
        text: 文本指令
        video: 视频文件
        images: 图片文件列表
        execute_async: 是否异步执行
        function_name: 可选，直接指定函数名（用于风格卡应用）
        function_params: 可选，函数参数JSON字符串
        
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
        
        # 🆕 为用户上传的媒体生成可访问的URL
        user_media_url = None
        if video_path:
            # 将绝对路径转换为相对URL
            # 例如: D:\...\data\sessions\xxx\uploads\video.mp4 
            # -> /media/sessions/xxx/uploads/video.mp4
            try:
                import os
                rel_path = os.path.relpath(video_path, str(_base_data_dir / "sessions"))
                user_media_url = f"/media/sessions/{rel_path.replace(os.sep, '/')}"
                logger.info(f"🔗 用户视频URL: {user_media_url}")
            except Exception as e:
                logger.warning(f"生成用户视频URL失败: {e}")
        
        # 添加用户消息到会话
        user_msg = session_manager.add_message_to_session(
            session_id=session_id,
            content=text,
            message_type=MessageType.MULTIMODAL if (video_path or image_paths) else MessageType.TEXT,
            sender=MessageSender.USER,
            media_path=video_path,
            metadata={
                "image_paths": image_paths,
                "media_url": user_media_url,  # 🆕 添加URL
                "video_url": user_media_url   # 保持向后兼容
            }
        )
        
        # 更新会话状态
        session_manager.update_session(
            session_id=session_id,
            status=SessionStatus.PROCESSING,
            current_video=video_path
        )
        
        # 创建DialogueManager实例处理输入
        dialogue_manager = DialogueManager()
        
        # 🆕 获取视频元数据（如时长）
        video_metadata = None
        if video_path:
            try:
                import subprocess
                import shlex
                input_ff = video_path.replace("\\", "/")
                cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_ff}"'
                result = subprocess.run(shlex.split(cmd), check=True, capture_output=True, text=True)
                duration = float(result.stdout.strip())
                video_metadata = {"duration": duration}
                logger.info(f"📊 视频时长: {duration}秒")
            except Exception as e:
                logger.warning(f"获取视频时长失败: {e}")
        
        # 定义任务函数
        def process_task():
            # 🎯 优先检测Demo风格卡（即使全局Demo模式关闭，也检查特定风格卡）
            if style_card_name:
                from config.demo_config import get_demo_style_card_video
                demo_video_path, demo_description = get_demo_style_card_video(style_card_name)
                if demo_video_path:
                    logger.info(f"🎨 检测到Demo风格卡: {style_card_name}，返回预设视频: {demo_video_path}")
                    
                    # 生成可访问的URL
                    _project_root = Path(__file__).parent.parent.parent
                    try:
                        newbackend_dir = _project_root / "newBackend"
                        relative_path = os.path.relpath(demo_video_path, str(newbackend_dir))
                        media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                    except ValueError:
                        filename = os.path.basename(demo_video_path)
                        media_url = f"/media/demo_videos/{filename}"
                    
                    logger.info(f"🎬 Demo风格卡视频URL: {media_url}")
                    
                    # 返回demo结果
                    return {
                        "success": True,
                        "response": demo_description,
                        "modal_type": "text+video",
                        "action": "",
                        "execution": {
                            "success": True,
                            "video_url": media_url,
                            "output_path": demo_video_path
                        },
                        "function_call": None
                    }
            
            # 🎯 Demo模式检测（仅对智能剪辑指令生效）
            if is_demo_mode_enabled():
                
                # 检测Demo指令
                demo_video_path, demo_description, demo_function_call = get_demo_video_path(text)
                if demo_video_path:
                    logger.info(f"🎬 检测到Demo指令，返回预设视频: {demo_video_path}")
                    
                    # 生成可访问的URL（demo视频在newBackend/demo_videos目录）
                    _project_root = Path(__file__).parent.parent.parent
                    try:
                        # 尝试获取相对于newBackend目录的路径
                        newbackend_dir = _project_root / "newBackend"
                        relative_path = os.path.relpath(demo_video_path, str(newbackend_dir))
                        media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                    except ValueError:
                        # 如果路径不在newBackend下，使用文件名
                        filename = os.path.basename(demo_video_path)
                        media_url = f"/media/demo_videos/{filename}"
                    
                    logger.info(f"🎬 Demo视频URL: {media_url}")
                    
                    # 返回demo结果
                    return {
                        "success": True,
                        "response": demo_description,
                        "modal_type": "text+video",
                        "action": "",
                        "execution": {
                            "success": True,
                            "output_path": demo_video_path,
                            "media_url": media_url,
                            "video_url": media_url,
                            "output_type": "video",
                            "error_message": None,
                            "operation_name": "demo_playback",
                            "operation_details": {},
                            "function_call": demo_function_call  # 添加函数调用信息
                        }
                    }
            
            # 🎯 检查是否提供了函数调用信息（风格卡应用模式）
            import json
            if function_name and function_params:
                logger.info(f"🎨 风格卡应用模式: {function_name}")
                try:
                    params = json.loads(function_params)
                    logger.info(f"   参数: {params}")
                    
                    # 构造操作JSON（跳过NLP解析）
                    operation_json = {
                        "operations": {
                            "operation": function_name,
                            "params": params
                        }
                    }
                    
                    # 执行操作
                    exec_result = video_executor.execute_from_json(
                        operation_json,
                        input_video=video_path
                    )
                    
                    output_path = None
                    media_url = None
                    output_type = None
                    
                    if exec_result.success and exec_result.output_path:
                        output_path = exec_result.output_path
                        
                        # 判断输出类型
                        file_ext = os.path.splitext(output_path)[1].lower()
                        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                            output_type = 'image'
                        else:
                            output_type = 'video'
                        
                        # 生成可访问的URL
                        _project_root = Path(__file__).parent.parent.parent
                        _data_dir = _project_root / "data"
                        relative_path = os.path.relpath(output_path, str(_data_dir))
                        media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                        
                        logger.info(f"✅ 风格卡操作成功: {media_url}")
                    
                    # 返回结果
                    return {
                        "success": True,
                        "response": text,  # 使用用户指令作为响应
                        "modal_type": "text+video" if output_type == 'video' else "text+image",
                        "action": json.dumps(operation_json),
                        "execution": {
                            "success": exec_result.success,
                            "output_path": output_path,
                            "media_url": media_url,
                            "video_url": media_url,
                            "output_type": output_type,
                            "error_message": exec_result.error_message,
                            "operation_name": function_name,
                            "execution_time": exec_result.execution_time,
                            "function_call": {
                                "functionName": function_name,
                                "parameters": params
                            }
                        }
                    }
                except Exception as e:
                    logger.error(f"❌ 风格卡应用失败: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # 1. 先使用 DialogueManager 解析用户指令
            # 注意：对于大视频(>20MB)，只传递文本指令给千问，避免API错误
            # 视频文件路径会在后续视频编辑时使用
            
            # 🆕 如果有视频元数据，添加到文本提示中
            enhanced_text = text
            if video_metadata and video_metadata.get("duration"):
                enhanced_text = f"{text}\n[视频时长: {video_metadata['duration']:.1f}秒]"
                logger.info(f"🔧 增强后的文本: {enhanced_text}")
            
            result = dialogue_manager.process_multimodal_input(
                text=enhanced_text,
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
                    
                    # 提取函数调用信息（排除执行时上下文参数）
                    all_params = operation_json.get("operations", {}).get("params", {})
                    # 过滤掉执行时动态生成的参数
                    context_params = {'input_video', 'output_video', 'input_image', 'output_image'}
                    user_params = {k: v for k, v in all_params.items() if k not in context_params}
                    
                    function_call = {
                        "functionName": operation_name,
                        "parameters": user_params
                    }
                    logger.info(f"📝 提取函数调用信息: {function_call} (已过滤执行上下文参数)")
                    
                    # 更新结果
                    result["execution"] = {
                        "success": exec_result.success,
                        "output_path": output_path,
                        "media_url": media_url,
                        "video_url": media_url,  # 保持向后兼容
                        "output_type": output_type,
                        "error_message": exec_result.error_message,
                        "operation_name": exec_result.operation_name,
                        "execution_time": exec_result.execution_time,
                        "function_call": function_call  # 添加函数调用信息
                    }
                    logger.info(f"📦 返回结果包含function_call: {result['execution'].get('function_call')}")
                    
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
        
        # 提取function_call信息
        function_call = None
        
        # 首先尝试从完整结果中获取（Demo模式和其他预设的media_url）
        if hasattr(result, 'result') and isinstance(result.result, dict):
            execution = result.result.get('execution', {})
            if execution:
                media_url = execution.get('media_url') or execution.get('video_url')
                output_type = execution.get('output_type', 'video')
                function_call = execution.get('function_call')
                logger.info(f"从execution结果提取媒体URL ({output_type}): {media_url}")
                logger.info(f"从execution结果提取function_call: {function_call}")
        
        # 如果没有预设的media_url，尝试从output_path生成
        if not media_url and result.output_path and os.path.exists(result.output_path):
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
                
                try:
                    relative_path = os.path.relpath(result.output_path, str(_data_dir))
                    media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                    logger.info(f"生成媒体URL ({output_type}): {media_url}")
                except ValueError:
                    # 路径不在data目录下，可能是demo视频或其他特殊路径
                    logger.warning(f"输出路径不在data目录: {result.output_path}")
                    # 尝试从newBackend目录生成相对路径
                    newbackend_dir = _project_root / "newBackend"
                    try:
                        relative_path = os.path.relpath(result.output_path, str(newbackend_dir))
                        media_url = f"/media/{relative_path.replace(os.sep, '/')}"
                        logger.info(f"生成Demo媒体URL: {media_url}")
                    except ValueError:
                        logger.error(f"无法为路径生成URL: {result.output_path}")
            except Exception as e:
                logger.error(f"生成媒体URL失败: {e}")
        
        response_data = {
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
                "metadata": result.metadata,
                "function_call": function_call  # 添加函数调用信息
            }
        }
        logger.info(f"📤 返回任务状态，function_call: {function_call}")
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取任务状态失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/{session_id}/tasks")
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


@session_app.post("/{session_id}/recommendations")
async def get_session_recommendations(
    session_id: str,
    video_metadata: dict = {}
):
    """
    获取基于用户人格的智能推荐操作
    
    Args:
        session_id: 会话ID
        video_metadata: 视频元数据（duration, category, aspect_ratio等）
        
    Returns:
        推荐操作列表
    """
    try:
        # 验证会话存在
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取推荐（使用默认用户ID）
        recommendations = video_executor.get_recommendations(
            video_metadata=video_metadata,
            user_id="default_user"
        )
        
        logger.info(f"为会话 {session_id} 生成了 {len(recommendations)} 条推荐")
        
        return {
            "status": "success",
            "session_id": session_id,
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取推荐失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/{session_id}/persona")
async def get_session_persona(session_id: str, refresh: bool = False):
    """
    获取用户的人格数据
    
    Args:
        session_id: 会话ID
        refresh: 是否强制重新训练人格模型
        
    Returns:
        用户人格数据
    """
    try:
        # 验证会话存在
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取人格数据
        persona = video_executor.get_persona(user_id="default_user", refresh=refresh)
        
        if not persona:
            return {
                "status": "success",
                "has_persona": False,
                "message": "人格数据尚未生成，需要更多操作记录（建议至少50次操作）",
                "persona": None
            }
        
        logger.info(f"返回人格数据，总操作数: {persona.get('total_operations', 0)}")
        
        return {
            "status": "success",
            "has_persona": True,
            "persona": persona
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取人格数据失败")
        raise HTTPException(status_code=500, detail=str(e))


@session_app.get("/{session_id}/workflow-templates")
async def get_workflow_templates(session_id: str):
    """
    获取用户的常用工作流模板
    
    Args:
        session_id: 会话ID
        
    Returns:
        工作流模板列表
    """
    try:
        # 验证会话存在
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取人格数据
        persona = video_executor.get_persona(user_id="default_user")
        
        if not persona:
            return {
                "status": "success",
                "count": 0,
                "templates": []
            }
        
        # 提取工作流模板
        templates = persona.get('workflow_templates', [])
        
        logger.info(f"返回 {len(templates)} 个工作流模板")
        
        return {
            "status": "success",
            "count": len(templates),
            "templates": templates
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("获取工作流模板失败")
        raise HTTPException(status_code=500, detail=str(e))


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
        
        logger.info(f"📁 查找媒体文件: {path}")
        logger.info(f"   首先尝试: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 如果在data目录找不到，尝试在newBackend目录查找（demo视频）
            newbackend_path = str(_project_root / "newBackend" / path)
            logger.info(f"   data目录未找到，尝试: {newbackend_path}")
            if os.path.exists(newbackend_path):
                file_path = newbackend_path
                logger.info(f"   ✅ 找到文件: {file_path}")
            else:
                # 尝试在Results目录查找（兼容旧代码）
                alt_path = os.path.join("Results", os.path.basename(path))
                logger.info(f"   newBackend目录未找到，尝试: {alt_path}")
                if os.path.exists(alt_path):
                    file_path = alt_path
                    logger.info(f"   ✅ 找到文件: {file_path}")
                else:
                    logger.error(f"   ❌ 所有位置都未找到文件")
                    logger.error(f"   尝试过的路径:")
                    logger.error(f"   1. {str(base_dir / path)}")
                    logger.error(f"   2. {newbackend_path}")
                    logger.error(f"   3. {alt_path}")
                    raise HTTPException(status_code=404, detail="文件不存在")
        else:
            logger.info(f"   ✅ 找到文件: {file_path}")
        
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


@session_app.post("/generate-style-card-image")
async def generate_image_for_style_card(
    title: str = Form(...),
    description: str = Form(...),
    operations: str = Form("[]")  # JSON字符串
):
    """
    为风格卡生成AI图片
    
    Args:
        title: 风格卡标题
        description: 风格卡描述
        operations: 操作列表（JSON字符串）
        
    Returns:
        生成的图片本地路径
    """
    try:
        import json
        
        # 解析operations JSON
        try:
            operations_list = json.loads(operations)
        except:
            operations_list = []
        
        logger.info(f"🎨 收到生图请求:")
        logger.info(f"   标题: {title}")
        logger.info(f"   描述: {description}")
        logger.info(f"   操作数: {len(operations_list)}")
        
        # 调用生图函数
        image_path = generate_style_card_image(
            title=title,
            description=description,
            operations=operations_list
        )
        
        if image_path:
            logger.info(f"✅ 图片生成成功: {image_path}")
            return {
                "status": "success",
                "image_path": image_path,
                "message": "图片生成成功"
            }
        else:
            logger.error("❌ 图片生成失败")
            raise HTTPException(
                status_code=500,
                detail="图片生成失败，请稍后重试"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("生成图片异常")
        raise HTTPException(status_code=500, detail=f"生成图片失败: {str(e)}")

