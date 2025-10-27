import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta

# 添加父目录到路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import QWEN_API_KEY, QWEN_BASE_CHAT_MODEL

def get_upload_policy(api_key, model_name):
    """获取文件上传凭证"""
    url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "action": "getPolicy",
        "model": model_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to get upload policy: {response.text}")
    
    return response.json()['data']

def upload_file_to_oss(policy_data, file_path):
    """将文件上传到临时存储OSS"""
    file_name = Path(file_path).name
    key = f"{policy_data['upload_dir']}/{file_name}"
    
    with open(file_path, 'rb') as file:
        files = {
            'OSSAccessKeyId': (None, policy_data['oss_access_key_id']),
            'Signature': (None, policy_data['signature']),
            'policy': (None, policy_data['policy']),
            'x-oss-object-acl': (None, policy_data['x_oss_object_acl']),
            'x-oss-forbid-overwrite': (None, policy_data['x_oss_forbid_overwrite']),
            'key': (None, key),
            'success_action_status': (None, '200'),
            'file': (file_name, file)
        }
        
        response = requests.post(policy_data['upload_host'], files=files)
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")
    
    return f"oss://{key}"

def upload_file_and_get_url(api_key, model_name, file_path):
    """上传文件并获取URL"""
    # 1. 获取上传凭证，上传凭证接口有限流，超出限流将导致请求失败
    policy_data = get_upload_policy(api_key, model_name) 
    # 2. 上传文件到OSS
    oss_url = upload_file_to_oss(policy_data, file_path)
    
    return oss_url

# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("视频上传工具 - 获取公网可访问的临时 URL")
    print("=" * 60)
    print()
    
    # 从config中获取API Key
    api_key = QWEN_API_KEY
        
    # 设置model名称（视频延展使用 qwen-vl-plus）
    model_name = "qwen-vl-plus"

    # 待上传的文件路径（可以上传本地已生成的视频）
    # 示例：使用VideoEditor目录下已生成的视频
    file_path = r"Results\make_video_from_first_frame_001.mp4"
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        print("\n请修改 file_path 变量为实际的视频文件路径")
        print("视频要求：")
        print("  - 格式: MP4")
        print("  - 帧率: ≥16FPS")
        print("  - 大小: ≤50MB")
        print("  - 长度: ≤3秒（用于视频延展）")
        exit(1)
    
    print(f"准备上传文件: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB")
    print()
    
    try:
        print("正在上传到阿里云 OSS 临时存储...")
        public_url = upload_file_and_get_url(api_key, model_name, file_path)
        expire_time = datetime.now() + timedelta(hours=48)
        
        print()
        print("✓ 文件上传成功！")
        print("-" * 60)
        print(f"临时 URL: {public_url}")
        print(f"有效期: 48小时")
        print(f"过期时间: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        print()
        print("此 URL 可用于:")
        print("  1. 视频延展功能 (extend_video)")
        print("  2. 视频理解功能")
        print("  3. 其他需要公网视频 URL 的 API")
        print()
        print("注意: 使用 OSS URL 时，某些 API 需要特殊处理")

    except Exception as e:
        print(f"\n✗ 上传失败: {str(e)}")
        import traceback
        traceback.print_exc()