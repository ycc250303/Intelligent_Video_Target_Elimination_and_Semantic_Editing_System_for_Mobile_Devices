import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.config import QWEN_API_KEY, QWEN_BASE_CHAT_URL, QWEN_BASE_CHAT_MODEL

import base64
from pathlib import Path
from openai import OpenAI
from typing import Optional, Dict
import http.server
import socketserver
import threading
import time
import hashlib
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 视频理解结果缓存 - 避免重复分析同一视频
_video_comprehension_cache: Dict[str, str] = {}


def _generate_cache_key(video_path: str, prompt: str) -> str:
    """
    生成缓存键
    
    Args:
        video_path: 视频路径
        prompt: 提示词
        
    Returns:
        str: 缓存键（MD5哈希）
    """
    # 对于本地文件，使用文件路径+修改时间+prompt作为键
    if not (video_path.startswith('http://') or video_path.startswith('https://')):
        try:
            file_path = Path(video_path)
            if file_path.exists():
                mtime = file_path.stat().st_mtime
                key_str = f"{video_path}_{mtime}_{prompt}"
            else:
                key_str = f"{video_path}_{prompt}"
        except:
            key_str = f"{video_path}_{prompt}"
    else:
        # 对于URL，使用URL+prompt作为键
        key_str = f"{video_path}_{prompt}"
    
    return hashlib.md5(key_str.encode('utf-8')).hexdigest()


def comprehend_video(
    video_path: str, 
    prompt: str = "请详细描述这段视频的内容", 
    use_base64: bool = True,
    use_cache: bool = True,
    max_retries: int = 3
) -> str:
    """
    理解视频内容并返回描述（增强版：支持缓存和重试）
    
    参数:
        video_path: 视频文件的本地路径（Windows路径）或在线URL
        prompt: 提示词，用于指定如何描述视频内容
        use_base64: 是否使用base64编码（适合小于20MB的视频，默认True）
        use_cache: 是否使用缓存（默认True）
        max_retries: 最大重试次数（默认3次）
        
    返回:
        str: 视频内容的文字描述
        
    异常:
        FileNotFoundError: 视频文件不存在
        ValueError: 视频文件格式不支持或文件过大
        Exception: API调用失败
        
    注意:
        - 使用base64编码时，建议视频文件小于20MB
        - 如果视频过大，会自动尝试使用本地HTTP服务器方式
        - 缓存基于视频路径和提示词，相同输入会返回缓存结果
    """
    # 检查缓存
    if use_cache:
        cache_key = _generate_cache_key(video_path, prompt)
        if cache_key in _video_comprehension_cache:
            logger.info(f"✅ 使用缓存的视频理解结果 (缓存键: {cache_key[:8]}...)")
            return _video_comprehension_cache[cache_key]
    
    # 判断是否为在线URL
    if video_path.startswith('http://') or video_path.startswith('https://'):
        video_url = video_path
        logger.info(f"使用在线视频URL: {video_path}")
    else:
        # 处理本地文件
        video_file = Path(video_path)
        
        # 检查文件是否存在
        if not video_file.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 检查文件扩展名
        supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        if video_file.suffix.lower() not in supported_formats:
            raise ValueError(f"不支持的视频格式: {video_file.suffix}。支持的格式: {', '.join(supported_formats)}")
        
        # 检查文件大小
        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        
        if use_base64 and file_size_mb > 20:
            print(f"警告: 视频文件过大 ({file_size_mb:.2f}MB)，建议使用use_base64=False")
            print("尝试使用本地HTTP服务器方式...")
            use_base64 = False
        
        if use_base64:
            # 方案1: 使用base64编码
            print(f"使用base64编码方式 (文件大小: {file_size_mb:.2f}MB)...")
            with open(video_file, 'rb') as f:
                video_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 根据文件扩展名设置MIME类型
            mime_types = {
                '.mp4': 'video/mp4',
                '.avi': 'video/x-msvideo',
                '.mov': 'video/quicktime',
                '.mkv': 'video/x-matroska',
                '.flv': 'video/x-flv',
                '.wmv': 'video/x-ms-wmv'
            }
            mime_type = mime_types.get(video_file.suffix.lower(), 'video/mp4')
            video_url = f"data:{mime_type};base64,{video_data}"
        else:
            # 方案2: 使用本地HTTP服务器
            print(f"启动本地HTTP服务器 (文件大小: {file_size_mb:.2f}MB)...")
            video_url = _start_local_server(video_file)
    
    # 带重试的API调用
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"🎬 调用视频理解API (尝试 {attempt + 1}/{max_retries})...")
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=QWEN_API_KEY,
                base_url=QWEN_BASE_CHAT_URL,
            )
            
            # 调用API进行视频理解
            completion = client.chat.completions.create(
                model=QWEN_BASE_CHAT_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                # 直接传入视频文件时，请将type的值设置为video_url
                                # 使用OpenAI SDK时，视频文件默认每间隔0.5秒抽取一帧，且不支持修改
                                # 如需自定义抽帧频率，请使用DashScope SDK
                                "type": "video_url",
                                "video_url": {"url": video_url}
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                timeout=60.0  # 设置60秒超时
            )
            
            # 获取结果
            result = completion.choices[0].message.content
            
            # 存入缓存
            if use_cache:
                cache_key = _generate_cache_key(video_path, prompt)
                _video_comprehension_cache[cache_key] = result
                logger.info(f"✅ 视频理解成功，已缓存结果 (缓存键: {cache_key[:8]}...)")
            
            return result
            
        except Exception as e:
            last_error = e
            logger.warning(f"❌ 第 {attempt + 1} 次尝试失败: {str(e)}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 递增等待时间：2秒、4秒、6秒
                logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                # 最后一次尝试失败，抛出异常
                raise Exception(f"视频理解API调用失败（已重试{max_retries}次）: {str(last_error)}")


def clear_video_comprehension_cache():
    """
    清除视频理解缓存
    """
    global _video_comprehension_cache
    cache_size = len(_video_comprehension_cache)
    _video_comprehension_cache.clear()
    logger.info(f"✅ 已清除视频理解缓存 ({cache_size} 个条目)")


def get_cache_stats() -> Dict[str, any]:
    """
    获取缓存统计信息
    
    Returns:
        Dict: 缓存统计
    """
    return {
        "cache_size": len(_video_comprehension_cache),
        "cache_keys": list(_video_comprehension_cache.keys())
    }


def _start_local_server(video_file: Path, port: int = 8765) -> str:
    """
    启动本地HTTP服务器提供视频文件访问
    
    参数:
        video_file: 视频文件路径
        port: HTTP服务器端口
        
    返回:
        str: 视频文件的HTTP访问URL
    """
    class VideoHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(video_file.parent), **kwargs)
        
        def log_message(self, format, *args):
            pass  # 禁用日志输出
    
    def run_server():
        with socketserver.TCPServer(("", port), VideoHandler) as httpd:
            httpd.serve_forever()
    
    # 在后台线程启动服务器
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)  # 等待服务器启动
    
    return f"http://localhost:{port}/{video_file.name}"


# 测试代码（可选）
if __name__ == "__main__":
    # 示例用法
    test_video_path = r"D:\GitHub\ycc\Intelligent_Video_Target_Elimination_and_Semantic_Editing_System_for_Mobile_Devices\newBackend\core\0.mp4"  # 替换为实际的视频路径
    
    try:
        # 尝试方案1: Base64编码（适合小文件）
        print("=" * 60)
        print("正在分析视频...")
        print("=" * 60)
        description = comprehend_video(test_video_path,prompt="描述视频内容，并指出视频中存在几次转场",use_base64=True)
        print("\n" + "=" * 60)
        print("视频内容描述：")
        print("=" * 60)
        print(description)
        print("\n理解成功！")
    except Exception as e:
        print(f"错误: {e}")
        print("\n如果base64方式失败，可以尝试:")
        print("1. 使用在线视频URL")
        print("2. 压缩视频文件大小")
        print("3. 设置 use_base64=False 使用本地HTTP服务器方式")