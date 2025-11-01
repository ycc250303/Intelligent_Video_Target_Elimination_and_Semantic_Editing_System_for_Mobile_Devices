#!/usr/bin/env python3
"""
CoEdit 后端服务器启动脚本 - 简化版
直接运行 session_app，不使用复杂的挂载结构
"""

import sys
import os

# 将当前目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 导入会话管理和人格管理应用
from api.session_api import session_app
from api.persona_api import persona_app

# 创建主应用
app = FastAPI(title="CoEdit Backend API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加根路径信息
@app.get("/", tags=["系统信息"])
def root():
    """
    系统根路径 - 返回系统基本信息
    
    访问各个API文档：
    - 主文档（所有接口）: /docs
    - 会话管理文档: /api/sessions/docs
    - 人格系统文档: /api/persona/docs
    """
    return {
        "name": "CoEdit 智能视频编辑系统",
        "version": "2.1.0",
        "mode": "单用户模式",
        "features": [
            "多会话管理",
            "并发任务处理",
            "多模态输入支持",
            "视频智能编辑",
            "用户剪辑人格建模",
            "智能操作推荐"
        ],
        "api_groups": {
            "sessions": "/api/sessions/* - 会话管理API",
            "persona": "/api/persona/* - 用户人格与推荐API"
        },
        "documentation": {
            "main": "/docs - 主文档（当前页面）",
            "sessions": "/api/sessions/docs - 会话管理完整文档",
            "persona": "/api/persona/docs - 人格系统完整文档"
        }
    }

@app.get("/api-docs-info", tags=["系统信息"])
def api_docs_info():
    """
    API文档索引
    
    由于使用了子应用架构，各个模块有独立的文档页面
    """
    return {
        "message": "各个子系统有独立的API文档",
        "docs": {
            "main": {
                "url": "/docs",
                "description": "主应用文档（系统信息接口）"
            },
            "sessions": {
                "url": "/api/sessions/docs",
                "description": "会话管理完整文档（创建会话、处理视频、获取推荐等）"
            },
            "persona": {
                "url": "/api/persona/docs",
                "description": "人格系统完整文档（训练模型、获取推荐等）"
            }
        },
        "tip": "建议访问 /api/sessions/docs 查看完整的会话管理接口"
    }

# 挂载子应用（统一使用/api前缀）
# 注意：子应用有独立的文档页面
app.mount("/api/sessions", session_app)
app.mount("/api/persona", persona_app)

# 🆕 挂载静态文件服务 - 提供处理后的媒体文件访问
# data/results 目录映射到 /media/results 路径
# data/sessions 目录映射到 /media/sessions 路径（用户上传的文件）
data_dir = Path(__file__).parent.parent / "data"
results_dir = data_dir / "results"
sessions_dir = data_dir / "sessions"
results_dir.mkdir(parents=True, exist_ok=True)
sessions_dir.mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录
app.mount("/media/results", StaticFiles(directory=str(results_dir)), name="media_results")
app.mount("/media/sessions", StaticFiles(directory=str(sessions_dir)), name="media_sessions")
print(f"📁 静态文件服务已配置:")
print(f"   - /media/results -> {results_dir}")
print(f"   - /media/sessions -> {sessions_dir}")

if __name__ == "__main__":
    print("="*60)
    print("  CoEdit 后端服务启动中...")
    print("  模式: 单用户模式（完整版 - 包含人格系统）")
    print("="*60)
    print(f"  API 接口地址: http://localhost:8000")
    print(f"  API 文档: http://localhost:8000/docs")
    print("="*60)
    print("\n  📡 可用服务:")
    print("     - 会话管理: /api/sessions/*")
    print("     - 人格系统: /api/persona/*")
    print("     - 媒体文件: /media/results/* (视频/图片下载)")
    print(f"     - 手机端配置: http://YOUR_IP:8000\n")
    print("  📚 API文档（重要）:")
    print("     - 系统概览: http://localhost:8000/docs")
    print("     - 会话管理完整文档: http://localhost:8000/api/sessions/docs ⭐")
    print("     - 人格系统完整文档: http://localhost:8000/api/persona/docs ⭐")
    print("")
    print("  💡 提示:")
    print("     - 主文档(/docs)只显示系统信息接口")
    print("     - 实际业务接口请访问子应用文档:")
    print("       → /api/sessions/docs (会话、视频处理、推荐等)")
    print("       → /api/persona/docs  (人格训练、推荐等)")
    print("")
    print("="*60)
    
    # 打印所有注册的路由用于调试
    from fastapi.routing import APIRoute
    print("\n已注册的路由:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"  {', '.join(route.methods):12s} {route.path}")
    print()
    
    # 配置uvicorn日志（禁用颜色避免Windows乱码）
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        # 禁用uvicorn的默认日志格式器，使用我们自己的
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO"},
            },
        }
    )

