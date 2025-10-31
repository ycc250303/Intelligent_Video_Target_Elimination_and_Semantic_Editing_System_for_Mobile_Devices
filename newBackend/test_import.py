#!/usr/bin/env python3
"""
测试所有必要的模块导入
"""
import sys

print("=" * 60)
print("测试模块导入")
print("=" * 60)

# 测试1: config.demo_config
try:
    from config.demo_config import get_demo_video_path, is_demo_mode_enabled
    print("\n[OK] config.demo_config 导入成功")
    print(f"    Demo模式: {'启用' if is_demo_mode_enabled() else '禁用'}")
except Exception as e:
    print(f"\n[FAIL] config.demo_config 导入失败: {e}")
    sys.exit(1)

# 测试2: session_api
try:
    from api.session_api import session_app
    print("[OK] api.session_api 导入成功")
except Exception as e:
    print(f"[FAIL] api.session_api 导入失败: {e}")
    sys.exit(1)

# 测试3: integrated_server
try:
    from api.integrated_server import app
    print("[OK] api.integrated_server 导入成功")
except Exception as e:
    print(f"[FAIL] api.integrated_server 导入失败: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("所有模块导入测试通过！")
print("=" * 60)








