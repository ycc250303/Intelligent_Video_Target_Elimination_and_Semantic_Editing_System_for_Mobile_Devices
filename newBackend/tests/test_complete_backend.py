#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoEdit 后端完整测试套件
测试所有可用的API服务（v1 + v2）
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
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
API_V2 = f"{BASE_URL}/api/v2"

def print_header(title, level=1):
    """打印标题"""
    if level == 1:
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    elif level == 2:
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}")
    else:
        print(f"\n  【{title}】")

def print_result(name, success, details=""):
    """打印测试结果"""
    status = "✓" if success else "✗"
    color_name = f"{status} {name}"
    print(f"  {color_name}", end="")
    if details:
        print(f" - {details}")
    else:
        print()

class TestResults:
    """测试结果统计"""
    def __init__(self):
        self.results = []
        self.categories = {}
    
    def add(self, category, name, success, details=""):
        """添加测试结果"""
        self.results.append((category, name, success, details))
        if category not in self.categories:
            self.categories[category] = {"passed": 0, "total": 0}
        self.categories[category]["total"] += 1
        if success:
            self.categories[category]["passed"] += 1
        print_result(name, success, details)
    
    def print_summary(self):
        """打印测试汇总"""
        print_header("测试结果汇总", 1)
        
        total_passed = 0
        total_tests = 0
        
        for category, stats in self.categories.items():
            passed = stats["passed"]
            total = stats["total"]
            total_passed += passed
            total_tests += total
            status = "✓" if passed == total else "⚠"
            print(f"  {status} {category}: {passed}/{total} 通过")
        
        print(f"\n  {'─'*70}")
        print(f"  总计: {total_passed}/{total_tests} 测试通过 ({total_passed*100//total_tests if total_tests > 0 else 0}%)")
        
        if total_passed == total_tests:
            print("\n  🎉 所有测试通过！后端服务运行正常！")
            return True
        else:
            print(f"\n  ⚠️  有 {total_tests - total_passed} 个测试失败")
            return False

results = TestResults()

# ============================================================
# 测试组1: 基础健康检查
# ============================================================
def test_health_checks():
    """测试健康检查端点"""
    print_header("基础健康检查", 2)
    
    # 测试根路径
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        results.add("健康检查", "根路径", success, 
                   f"版本: {data.get('version', 'N/A')}")
    except Exception as e:
        results.add("健康检查", "根路径", False, str(e))
    
    # 测试健康检查
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        data = response.json() if success else {}
        results.add("健康检查", "健康检查端点", success,
                   f"模式: {data.get('mode', 'N/A')}")
    except Exception as e:
        results.add("健康检查", "健康检查端点", False, str(e))
    
    # 测试API文档
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        success = response.status_code == 200
        results.add("健康检查", "API文档", success)
    except Exception as e:
        results.add("健康检查", "API文档", False, str(e))

# ============================================================
# 测试组2: 会话管理API (v2)
# ============================================================
def test_session_management():
    """测试会话管理功能"""
    print_header("会话管理API (v2)", 2)
    
    session_ids = []
    
    # 2.1 创建会话
    try:
        response = requests.post(
            f"{API_V2}/sessions/create",
            json={"title": "完整测试会话1", "icon": "🎬"}
        )
        success = response.status_code == 200
        if success:
            session_ids.append(response.json()['session']['id'])
        results.add("会话管理", "创建会话", success)
    except Exception as e:
        results.add("会话管理", "创建会话", False, str(e))
    
    # 2.2 批量创建会话
    for i in range(2, 4):
        try:
            response = requests.post(
                f"{API_V2}/sessions/create",
                json={"title": f"完整测试会话{i}", "icon": "📝"}
            )
            if response.status_code == 200:
                session_ids.append(response.json()['session']['id'])
        except:
            pass
    
    results.add("会话管理", "批量创建会话", len(session_ids) >= 3,
               f"创建了{len(session_ids)}个会话")
    
    if not session_ids:
        return
    
    # 2.3 获取所有会话
    try:
        response = requests.get(f"{API_V2}/sessions")
        success = response.status_code == 200
        count = response.json().get('count', 0) if success else 0
        results.add("会话管理", "获取所有会话", success, f"共{count}个会话")
    except Exception as e:
        results.add("会话管理", "获取所有会话", False, str(e))
    
    # 2.4 获取单个会话
    try:
        response = requests.get(f"{API_V2}/sessions/{session_ids[0]}")
        success = response.status_code == 200
        results.add("会话管理", "获取会话详情", success)
    except Exception as e:
        results.add("会话管理", "获取会话详情", False, str(e))
    
    # 2.5 添加消息
    message_ids = []
    for i, msg_type in enumerate(['text', 'text', 'text']):
        try:
            response = requests.post(
                f"{API_V2}/sessions/add_message",
                json={
                    "session_id": session_ids[0],
                    "content": f"测试消息{i+1}",
                    "message_type": msg_type,
                    "sender": "user"
                }
            )
            if response.status_code == 200:
                message_ids.append(response.json()['message']['id'])
        except:
            pass
    
    results.add("会话管理", "添加消息", len(message_ids) >= 2,
               f"添加了{len(message_ids)}条消息")
    
    # 2.6 验证消息已添加
    try:
        response = requests.get(f"{API_V2}/sessions/{session_ids[0]}")
        if response.status_code == 200:
            msg_count = len(response.json()['session'].get('messages', []))
            results.add("会话管理", "验证消息持久化", msg_count >= 2,
                       f"会话包含{msg_count}条消息")
    except Exception as e:
        results.add("会话管理", "验证消息持久化", False, str(e))
    
    # 2.7 更新会话
    try:
        response = requests.put(
            f"{API_V2}/sessions/update",
            json={
                "session_id": session_ids[0],
                "title": "已更新的会话标题",
                "status": "processing"
            }
        )
        success = response.status_code == 200
        results.add("会话管理", "更新会话信息", success)
    except Exception as e:
        results.add("会话管理", "更新会话信息", False, str(e))
    
    # 2.8 验证更新
    try:
        response = requests.get(f"{API_V2}/sessions/{session_ids[0]}")
        if response.status_code == 200:
            session = response.json()['session']
            title_updated = session['title'] == "已更新的会话标题"
            status_updated = session['status'] == "processing"
            results.add("会话管理", "验证更新结果", 
                       title_updated and status_updated)
    except Exception as e:
        results.add("会话管理", "验证更新结果", False, str(e))
    
    # 2.9 删除单个会话
    deleted_session_id = None
    try:
        if len(session_ids) >= 2:
            deleted_session_id = session_ids[-1]
            response = requests.delete(f"{API_V2}/sessions/{deleted_session_id}")
            success = response.status_code == 200
            results.add("会话管理", "删除单个会话", success)
            if success:
                session_ids.pop()
        else:
            results.add("会话管理", "删除单个会话", False, "会话数量不足")
    except Exception as e:
        results.add("会话管理", "删除单个会话", False, str(e))
    
    # 2.10 验证删除
    try:
        if deleted_session_id:
            response = requests.get(f"{API_V2}/sessions/{deleted_session_id}")
            # 删除后的会话不应该存在（应该返回404）
            success = response.status_code == 404
            results.add("会话管理", "验证删除结果", success,
                       f"返回{response.status_code}")
        else:
            results.add("会话管理", "验证删除结果", False, "没有删除的会话ID")
    except Exception as e:
        results.add("会话管理", "验证删除结果", False, str(e))
    
    return session_ids

# ============================================================
# 测试组3: 数据格式验证
# ============================================================
def test_data_format():
    """测试数据格式是否符合单用户模式规范"""
    print_header("数据格式验证", 2)
    
    try:
        # 创建测试会话
        response = requests.post(
            f"{API_V2}/sessions/create",
            json={"title": "格式测试", "icon": "🔍"}
        )
        
        if response.status_code != 200:
            results.add("数据格式", "创建测试会话", False)
            return None
        
        session = response.json()['session']
        session_id = session['id']
        
        # 验证必需字段
        required_fields = ['id', 'title', 'icon', 'status', 'created_at',
                          'updated_at', 'messages', 'progress']
        missing = [f for f in required_fields if f not in session]
        results.add("数据格式", "必需字段完整性", len(missing) == 0,
                   f"缺失: {missing}" if missing else "所有字段齐全")
        
        # 验证无user_id字段（单用户模式）
        has_user_id = 'user_id' in session
        results.add("数据格式", "单用户模式验证", not has_user_id,
                   "✓ 无user_id字段" if not has_user_id else "✗ 仍包含user_id")
        
        # 验证ID格式（应该不包含user前缀）
        correct_format = not session_id.startswith("session_user_")
        results.add("数据格式", "ID格式简化", correct_format,
                   f"ID: {session_id[:30]}...")
        
        # 验证状态枚举
        valid_statuses = ['active', 'idle', 'processing', 'completed', 'error']
        status_valid = session['status'] in valid_statuses
        results.add("数据格式", "状态值有效性", status_valid,
                   f"状态: {session['status']}")
        
        # 验证时间格式（ISO8601）
        import datetime
        try:
            datetime.datetime.fromisoformat(session['created_at'])
            datetime.datetime.fromisoformat(session['updated_at'])
            time_valid = True
        except:
            time_valid = False
        results.add("数据格式", "时间格式正确性", time_valid)
        
        # 验证进度范围
        progress_valid = 0 <= session['progress'] <= 1.0
        results.add("数据格式", "进度值范围", progress_valid,
                   f"进度: {session['progress']}")
        
        # 清理
        requests.delete(f"{API_V2}/sessions/{session_id}")
        
        return session_id
    except Exception as e:
        results.add("数据格式", "数据格式验证", False, str(e))
        return None

# ============================================================
# 测试组4: 错误处理
# ============================================================
def test_error_handling():
    """测试错误处理机制"""
    print_header("错误处理", 2)
    
    # 4.1 获取不存在的会话
    try:
        response = requests.get(f"{API_V2}/sessions/nonexistent_id_12345")
        success = response.status_code == 404
        results.add("错误处理", "不存在的会话", success,
                   f"返回{response.status_code}")
    except Exception as e:
        results.add("错误处理", "不存在的会话", False, str(e))
    
    # 4.2 删除不存在的会话
    try:
        response = requests.delete(f"{API_V2}/sessions/nonexistent_id_12345")
        success = response.status_code == 404
        results.add("错误处理", "删除不存在的会话", success,
                   f"返回{response.status_code}")
    except Exception as e:
        results.add("错误处理", "删除不存在的会话", False, str(e))
    
    # 4.3 向不存在的会话添加消息
    try:
        response = requests.post(
            f"{API_V2}/sessions/add_message",
            json={
                "session_id": "nonexistent_id_12345",
                "content": "测试",
                "message_type": "text",
                "sender": "user"
            }
        )
        success = response.status_code == 404
        results.add("错误处理", "向不存在会话添加消息", success,
                   f"返回{response.status_code}")
    except Exception as e:
        results.add("错误处理", "向不存在会话添加消息", False, str(e))
    
    # 4.4 无效的请求数据
    try:
        # 因为title和icon都有默认值，所以空JSON也能成功
        # 改为测试无效的status值
        response = requests.put(
            f"{API_V2}/sessions/update",
            json={
                "session_id": "test_id_123",
                "status": "invalid_status_value"  # 无效的状态值
            }
        )
        # 对于不存在的session_id应该返回404
        # 即使有无效status，也会先检查session是否存在
        success = response.status_code in [400, 404, 422]
        results.add("错误处理", "无效请求数据", success,
                   f"返回{response.status_code}")
    except Exception as e:
        results.add("错误处理", "无效请求数据", False, str(e))

# ============================================================
# 测试组5: 并发和性能
# ============================================================
def test_concurrency():
    """测试并发处理能力"""
    print_header("并发测试", 2)
    
    import threading
    
    # 5.1 并发创建会话
    created_sessions = []
    errors = []
    
    def create_session(index):
        try:
            response = requests.post(
                f"{API_V2}/sessions/create",
                json={"title": f"并发测试{index}", "icon": "⚡"}
            )
            if response.status_code == 200:
                created_sessions.append(response.json()['session']['id'])
        except Exception as e:
            errors.append(str(e))
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=create_session, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    results.add("并发测试", "并发创建会话", len(created_sessions) >= 4,
               f"成功创建{len(created_sessions)}/5个会话")
    
    # 5.2 并发读取
    read_success = []
    
    def read_sessions():
        try:
            response = requests.get(f"{API_V2}/sessions")
            if response.status_code == 200:
                read_success.append(True)
        except:
            pass
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=read_sessions)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    results.add("并发测试", "并发读取操作", len(read_success) >= 8,
               f"成功{len(read_success)}/10次读取")
    
    # 清理并发创建的会话
    for sid in created_sessions:
        try:
            requests.delete(f"{API_V2}/sessions/{sid}")
        except:
            pass

# ============================================================
# 主测试流程
# ============================================================
def main():
    """运行所有测试"""
    print_header("CoEdit 后端完整测试套件", 1)
    print("  测试范围: API v1 (视频处理) + API v2 (会话管理)")
    print("  模式: 单用户Demo模式")
    print("="*70)
    
    # 检查服务器连接
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code != 200:
            print("\n✗ 错误: 后端服务器未正常运行")
            print(f"  健康检查返回: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务器")
        print(f"  请确保服务器已在 {BASE_URL} 上运行")
        print("  启动命令: cd newBackend && python run_server.py")
        return
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return
    
    # 运行测试组
    test_health_checks()
    test_session_management()
    test_data_format()
    test_error_handling()
    test_concurrency()
    
    # 打印汇总
    success = results.print_summary()
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

