"""
测试文生视频功能
"""
import requests
import json
import time

# 配置
BASE_URL = "http://100.80.59.113:8000"

def test_text_to_video():
    """测试文生视频"""
    print("=" * 60)
    print("测试文生视频功能")
    print("=" * 60)
    
    # 1. 创建会话
    print("\n1. 创建会话...")
    response = requests.post(
        f"{BASE_URL}/sessions/create",
        json={"title": "文生视频测试", "icon": "🎬"}
    )
    if response.status_code == 200:
        session_data = response.json()
        # API 现在同时返回 session_id 和 session 对象
        session_id = session_data.get("session_id")
        if session_id:
            print(f"✅ 会话创建成功: {session_id}")
        else:
            print(f"❌ 会话创建失败: 返回数据中没有session_id")
            print(f"   返回数据: {session_data}")
            return
    else:
        print(f"❌ 会话创建失败: {response.status_code}, {response.text}")
        return
    
    # 2. 发送文生视频请求
    print("\n2. 发送文生视频请求...")
    
    # 准备表单数据
    form_data = {
        'session_id': session_id,
        'text': '生成一个小猫在草地上奔跑的视频',
        'execute_async': 'true'  # ⚠️ 修正：后端参数名是 execute_async
    }
    
    response = requests.post(
        f"{BASE_URL}/sessions/process-multimodal",
        data=form_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 请求提交成功")
        print(f"   状态: {result.get('status')}")
        print(f"   消息: {result.get('message')}")
        
        if result.get('async'):
            task_id = result.get('task_id')
            print(f"   任务ID: {task_id}")
            
            # 3. 轮询任务状态
            print("\n3. 轮询任务状态...")
            max_polls = 60  # 最多轮询60次（2分钟）
            poll_count = 0
            
            while poll_count < max_polls:
                poll_count += 1
                print(f"\n   🔄 第 {poll_count} 次轮询...")
                
                # 获取任务状态
                task_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    task = task_data.get('task', {})
                    status = task.get('status')
                    
                    print(f"      状态: {status}")
                    print(f"      output_path: {task.get('output_path')}")
                    print(f"      video_url: {task.get('video_url')}")
                    print(f"      error_message: {task.get('error_message')}")
                    
                    if status == 'completed':
                        if task.get('output_path') and task.get('video_url'):
                            print(f"\n✅ 任务完成成功！")
                            print(f"   输出路径: {task.get('output_path')}")
                            print(f"   访问URL: {task.get('video_url')}")
                        else:
                            print(f"\n⚠️  任务完成但没有返回视频")
                            print(f"   这可能是因为：")
                            print(f"   1. 文生视频 API 调用失败")
                            print(f"   2. 视频下载失败")
                            print(f"   3. 后端日志中应该有详细错误信息")
                        break
                    elif status == 'failed':
                        print(f"\n❌ 任务失败: {task.get('error_message')}")
                        break
                    elif status == 'running':
                        print(f"      ⏳ 任务进行中，等待2秒...")
                        time.sleep(2)
                    else:
                        print(f"      未知状态: {status}")
                        time.sleep(2)
                else:
                    print(f"   ❌ 获取任务状态失败: {task_response.status_code}")
                    break
            
            if poll_count >= max_polls:
                print(f"\n⏱️  轮询超时（2分钟）")
        else:
            # 同步结果
            print(f"\n✅ 同步执行完成")
            print(f"   响应: {result.get('response')}")
            print(f"   video_url: {result.get('video_url')}")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"   错误: {response.text}")

def check_server():
    """检查服务器是否运行"""
    print("\n检查后端服务器...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端服务器运行正常")
            print(f"   状态: {data.get('status')}")
            print(f"   消息: {data.get('message')}")
            print(f"   版本: {data.get('version')}")
            return True
        else:
            print(f"⚠️  后端服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务器: {e}")
        print(f"   请确保后端服务器已启动:")
        print(f"   cd newBackend")
        print(f"   python run_server.py")
        return False

if __name__ == "__main__":
    if check_server():
        test_text_to_video()
    else:
        print("\n请先启动后端服务器再运行测试")

