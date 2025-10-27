#!/usr/bin/env python3
"""测试脚本 - 列出所有注册的路由"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api.session_api import session_app
from fastapi.routing import APIRoute

print("\n" + "="*60)
print("session_app 中注册的所有路由:")
print("="*60 + "\n")

for idx, route in enumerate(session_app.routes, 1):
    if isinstance(route, APIRoute):
        methods = ', '.join(route.methods)
        print(f"{idx:2d}. [{methods:12s}] {route.path}")

print(f"\n总共 {len([r for r in session_app.routes if isinstance(r, APIRoute)])} 个路由\n")

# 检查关键路由
critical = ['/sessions/process-multimodal', '/sessions', '/sessions/create']
print("="*60)
print("关键路由检查:")
print("="*60 + "\n")
for path in critical:
    exists = any(r.path == path for r in session_app.routes if isinstance(r, APIRoute))
    print(f"{'✅' if exists else '❌'} {path}")
print()

