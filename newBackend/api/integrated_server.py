#!/usr/bin/env python3
"""
集成API服务器
整合原有的视频处理API和新的多会话管理API
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入现有的服务器
from api.fastapi_server import app as video_app
from api.session_api import session_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 创建主应用
app = FastAPI(
    title="CoEdit 智能视频编辑系统",
    description="支持多会话、并发处理的智能视频编辑服务",
    version="2.0.0"
)

# 配置CORS
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
        "name": "CoEdit 智能视频编辑系统",
        "version": "2.0.0",
        "features": [
            "多会话管理",
            "并发任务处理",
            "多模态输入支持",
            "视频智能编辑"
        ],
        "api_groups": {
            "sessions": "/sessions/* - 会话管理API",
            "tasks": "/tasks/* - 任务管理API",
            "video": "/upload-video, /process-video - 视频处理API（兼容旧版）",
            "executor": "/executor/* - 执行器统计API"
        },
        "documentation": "/docs"
    }


# 挂载会话管理API
app.mount("/api/v2", session_app)

# 注意：原有的video_app端点可以直接集成到这里
# 或者继续使用原有的fastapi_server.py


@app.get("/api-info")
def api_info():
    """API信息"""
    return {
        "v1_endpoints": {
            "upload_video": "POST /upload-video",
            "process_video": "POST /process-video",
            "serve_video": "GET /uploads/{filename}",
            "generate_from_image": "POST /generate-video-from-image",
            "process_multimodal": "POST /process-multimodal",
            "execute_operation": "POST /execute-operation-json"
        },
        "v2_endpoints": {
            "create_session": "POST /api/v2/sessions/create",
            "get_session": "GET /api/v2/sessions/{session_id}",
            "get_user_sessions": "GET /api/v2/users/{user_id}/sessions",
            "update_session": "PUT /api/v2/sessions/update",
            "delete_session": "DELETE /api/v2/sessions/{session_id}",
            "add_message": "POST /api/v2/sessions/message",
            "process_multimodal": "POST /api/v2/sessions/process-multimodal",
            "get_task": "GET /api/v2/tasks/{task_id}",
            "get_session_tasks": "GET /api/v2/sessions/{session_id}/tasks",
            "cancel_task": "DELETE /api/v2/tasks/{task_id}",
            "executor_stats": "GET /api/v2/executor/stats",
            "health": "GET /api/v2/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("CoEdit 智能视频编辑系统 - 集成API服务器")
    print("="*60)
    print("\n启动信息:")
    print("- 主机: 0.0.0.0")
    print("- 端口: 8000")
    print("- API文档: http://localhost:8000/docs")
    print("- 会话管理API: http://localhost:8000/api/v2/...")
    print("\n功能特性:")
    print("✓ 多用户多会话管理")
    print("✓ 并发任务处理（最多4个工作线程）")
    print("✓ 异步/同步执行模式")
    print("✓ 完整的任务状态跟踪")
    print("="*60 + "\n")
    
    uvicorn.run(
        "integrated_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


