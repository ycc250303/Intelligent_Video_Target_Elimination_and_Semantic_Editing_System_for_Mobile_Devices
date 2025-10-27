"""
测试删除所有会话功能
"""
import requests
import json
import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_delete_all_sessions():
    """测试删除所有会话功能"""
    print("=" * 60)
    print("测试删除所有会话功能")
    print("=" * 60)

    # 1. 先创建几个测试会话
    print("\n1. 创建3个测试会话...")
    created_ids = []
    for i in range(3):
        response = requests.post(
            f"{BASE_URL}/sessions/create",
            json={"title": f"测试会话{i+1}", "icon": "🎬"}
        )
        if response.status_code == 200:
            session_id = response.json()['session']['id']
            created_ids.append(session_id)
            print(f"   ✅ 创建成功: {session_id}")
        else:
            print(f"   ❌ 创建失败: {response.status_code}")

    # 2. 获取当前会话数
    print("\n2. 查看当前会话数...")
    response = requests.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        count_before = response.json()['count']
        print(f"   当前会话数: {count_before}")
    else:
        print(f"   ❌ 获取会话列表失败: {response.status_code}")
        return

    # 3. 删除所有会话
    print("\n3. 删除所有会话...")
    response = requests.delete(f"{BASE_URL}/sessions/all")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        deleted_count = response.json()['count']
        print(f"\n   ✅ 成功删除 {deleted_count} 个会话")
    else:
        print(f"\n   ❌ 删除失败")
        print(f"\n   ⚠️  提示：如果返回404，请确保已经重启后端服务器！")
        print(f"   后端路由修改需要重启才能生效。")
        return

    # 4. 验证删除结果
    print("\n4. 验证删除结果...")
    response = requests.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        count_after = response.json()['count']
        print(f"   当前会话数: {count_after}")
        if count_after == 0:
            print("\n   ✅ 所有会话已成功删除！")
        else:
            print(f"\n   ⚠️  还有 {count_after} 个会话未删除")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        test_delete_all_sessions()
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务器")
        print("请确保后端服务器已启动: python run_server.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

