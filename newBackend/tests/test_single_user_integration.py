#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单用户模式集成测试
验证后端API在单用户模式下的功能
"""

import sys
import os
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import time
import json

# 配置
BASE_URL = "http://localhost:8000/api/v2"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_create_session():
    """测试1: 创建会话（单用户模式，无需user_id）"""
    print_section("测试1: 创建会话（单用户模式）")
    
    response = requests.post(
        f"{BASE_URL}/sessions/create",
        json={
            "title": "测试对话1",
            "icon": "🎬"
        }
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    if response.status_code == 200:
        session_id = data['session']['id']
        print(f"✓ 成功创建会话: {session_id}")
        return session_id
    else:
        print("✗ 创建会话失败")
        return None

def test_get_all_sessions():
    """测试2: 获取所有会话（单用户模式）"""
    print_section("测试2: 获取所有会话")
    
    response = requests.get(f"{BASE_URL}/sessions")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"会话数量: {data.get('count', 0)}")
    
    if response.status_code == 200:
        sessions = data.get('sessions', [])
        for session in sessions:
            print(f"  - {session['title']} (ID: {session['id']})")
        print(f"✓ 成功获取 {len(sessions)} 个会话")
        return sessions
    else:
        print("✗ 获取会话失败")
        return []

def test_get_session(session_id):
    """测试3: 获取单个会话详情"""
    print_section("测试3: 获取会话详情")
    
    response = requests.get(f"{BASE_URL}/sessions/{session_id}")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        session = data['session']
        print(f"✓ 会话标题: {session['title']}")
        print(f"  状态: {session['status']}")
        print(f"  进度: {session['progress']}")
        print(f"  消息数: {len(session.get('messages', []))}")
        return True
    else:
        print("✗ 获取会话详情失败")
        return False

def test_add_message(session_id):
    """测试4: 向会话添加消息"""
    print_section("测试4: 添加消息")
    
    response = requests.post(
        f"{BASE_URL}/sessions/add_message",
        json={
            "session_id": session_id,
            "content": "你好，这是一条测试消息",
            "message_type": "text",
            "sender": "user"
        }
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        message = data['message']
        print(f"✓ 消息ID: {message['id']}")
        print(f"  内容: {message['content']}")
        print(f"  发送者: {message['sender']}")
        return True
    else:
        print("✗ 添加消息失败")
        return False

def test_update_session(session_id):
    """测试5: 更新会话信息"""
    print_section("测试5: 更新会话")
    
    response = requests.put(
        f"{BASE_URL}/sessions/update",
        json={
            "session_id": session_id,
            "title": "更新后的标题",
            "status": "processing"
        }
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ 会话更新成功")
        return True
    else:
        print("✗ 会话更新失败")
        return False

def test_delete_session(session_id):
    """测试6: 删除会话"""
    print_section("测试6: 删除会话")
    
    response = requests.delete(f"{BASE_URL}/sessions/{session_id}")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ 成功删除会话: {session_id}")
        return True
    else:
        print("✗ 删除会话失败")
        return False

def test_data_format():
    """测试7: 数据格式验证"""
    print_section("测试7: 数据格式验证")
    
    # 创建测试会话
    response = requests.post(
        f"{BASE_URL}/sessions/create",
        json={"title": "格式测试", "icon": "📝"}
    )
    
    if response.status_code != 200:
        print("✗ 创建测试会话失败")
        return False
    
    session = response.json()['session']
    session_id = session['id']
    
    # 验证字段
    required_fields = ['id', 'title', 'icon', 'status', 'created_at', 
                      'updated_at', 'messages', 'progress']
    
    missing_fields = []
    for field in required_fields:
        if field not in session:
            missing_fields.append(field)
    
    # 验证没有user_id字段
    if 'user_id' in session:
        print("✗ 错误: 数据中仍包含user_id字段")
        has_user_id = True
    else:
        print("✓ 确认: 数据中不包含user_id字段（单用户模式正确）")
        has_user_id = False
    
    # 验证ID格式
    id_prefix_ok = not session_id.startswith("session_user_")
    if id_prefix_ok:
        print(f"✓ 确认: ID格式已简化（{session_id}）")
    else:
        print(f"✗ 警告: ID格式仍包含user前缀")
    
    # 清理
    requests.delete(f"{BASE_URL}/sessions/{session_id}")
    
    if not missing_fields and not has_user_id and id_prefix_ok:
        print("\n✓ 数据格式验证通过")
        return True
    else:
        if missing_fields:
            print(f"\n✗ 缺少字段: {missing_fields}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  CoEdit 单用户模式集成测试")
    print("  验证前后端对接功能")
    print("="*60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/sessions", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务器")
        print(f"  请确保服务器已在 {BASE_URL} 上运行")
        print("  启动命令: cd newBackend && python api/integrated_server.py")
        return
    
    results = []
    session_id = None
    
    # 执行测试
    try:
        # 测试1: 创建会话
        session_id = test_create_session()
        results.append(('创建会话', session_id is not None))
        
        if session_id:
            # 测试2: 获取所有会话
            sessions = test_get_all_sessions()
            results.append(('获取所有会话', len(sessions) > 0))
            
            # 测试3: 获取单个会话
            success = test_get_session(session_id)
            results.append(('获取会话详情', success))
            
            # 测试4: 添加消息
            success = test_add_message(session_id)
            results.append(('添加消息', success))
            
            # 测试5: 更新会话
            success = test_update_session(session_id)
            results.append(('更新会话', success))
        
        # 测试7: 数据格式验证
        success = test_data_format()
        results.append(('数据格式验证', success))
        
        # 测试6: 删除会话（清理）
        if session_id:
            success = test_delete_session(session_id)
            results.append(('删除会话', success))
    
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印测试结果汇总
    print_section("测试结果汇总")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！单用户模式对接成功！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

if __name__ == "__main__":
    main()

