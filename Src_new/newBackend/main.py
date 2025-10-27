#!/usr/bin/env python3
"""
多模态视频编辑系统 - 主入口
快速启动API服务器
"""

import sys
import os

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from api.fastapi_server import app
    import uvicorn
    
    print("\n" + "="*60)
    print("🎬 多模态视频编辑系统 API 服务器")
    print("="*60)
    print("\n📡 服务器地址:")
    print("   - 本地: http://localhost:8000")
    print("   - 文档: http://localhost:8000/docs")
    print("\n📚 快速开始:")
    print("   - 查看文档: docs/MULTIMODAL_SYSTEM_README.md")
    print("   - 运行示例: python examples/quick_start_example.py")
    print("   - 运行测试: python tests/test_multimodal_system.py")
    print("\n⚙️  配置文件: config/config.py")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(
            "api.fastapi_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"\n❌ 启动服务器时出错: {e}")
        print("请检查端口 8000 是否被占用")


