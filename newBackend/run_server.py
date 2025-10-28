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
from fastapi.middleware.cors import CORSMiddleware

# 导入会话管理应用
from api.session_api import session_app as app

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    print("="*60)
    print("  CoEdit 后端服务启动中...")
    print("  模式: 单用户模式（简化版）")
    print("="*60)
    print(f"  API 接口地址: http://localhost:8000")
    print(f"  API 文档: http://localhost:8000/docs")
    print("="*60)
    print("\n  💡 提示:")
    print("     - 所有接口路径不需要 /api/v2 前缀")
    print("     - 访问 /docs 查看所有可用API")
    print(f"     - 手机端配置使用: http://YOUR_IP:8000\n")
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

