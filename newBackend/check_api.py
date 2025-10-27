#!/usr/bin/env python3
"""
API 诊断脚本 - 检查所有可用的路由
"""

import sys
import os

# 将当前目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api.session_api import session_app
from fastapi.routing import APIRoute

print("\n" + "="*60)
print("API 路由诊断")
print("="*60 + "\n")

print("📋 session_app (API v2) 中注册的路由:\n")

routes = []
for route in session_app.routes:
    if isinstance(route, APIRoute):
        routes.append({
            'path': route.path,
            'methods': list(route.methods),
            'name': route.name
        })

# 按路径排序
routes.sort(key=lambda x: x['path'])

for idx, route in enumerate(routes, 1):
    methods_str = ', '.join(route['methods'])
    print(f"{idx:2d}. [{methods_str:12s}] {route['path']}")
    print(f"     └─ 函数: {route['name']}")

print(f"\n总共 {len(routes)} 个路由")

# 检查关键路由
print("\n" + "="*60)
print("🔍 关键路由检查")
print("="*60 + "\n")

critical_routes = [
    '/sessions',
    '/sessions/create',
    '/sessions/process-multimodal',
    '/sessions/add_message',
    '/tasks/{task_id}',
]

for route_path in critical_routes:
    found = any(r['path'] == route_path for r in routes)
    status = "✅ 存在" if found else "❌ 缺失"
    print(f"{status} {route_path}")

print("\n" + "="*60)
print("💡 提示")
print("="*60 + "\n")
print("如果 /sessions/process-multimodal 显示 ✅ 存在，")
print("但仍然返回 404，请检查：")
print("  1. 是否使用了正确的启动脚本 (python run_server.py)")
print("  2. 完整URL是否正确: http://IP:8000/api/v2/sessions/process-multimodal")
print("  3. 浏览器访问: http://IP:8000/docs 查看完整API文档")
print("")

