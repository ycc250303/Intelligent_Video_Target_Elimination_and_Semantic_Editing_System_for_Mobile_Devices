"""
AI 图像生成模块
基于通义千问的图像生成能力
"""
import json
import os
import sys
import logging
import requests
import uuid
from pathlib import Path
import dashscope
from dashscope import MultiModalConversation
from typing import Optional, Dict, Any

# 添加父目录到Python路径，以便导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import QWEN_API_KEY, QWEN_BASE_GENERATE_MEDIA_URL

# 配置日志
logger = logging.getLogger(__name__)

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = QWEN_BASE_GENERATE_MEDIA_URL


def generate_style_card_image(
    title: str,
    description: str,
    operations: list = None,
    size: str = '1328*1328'
) -> Optional[str]:
    """
    根据风格卡信息生成图片
    
    Args:
        title: 风格卡标题
        description: 风格卡描述
        operations: 记录的操作列表
        size: 图片尺寸，默认1024*1024
        
    Returns:
        str: 生成的图片本地路径，失败返回None
    """
    try:
        # 构建生图提示词
        # 注意：不直接提及"视频编辑操作"，而是提取风格和氛围
        prompt = f"创意风格卡片设计，主题：{title}。"
        
        if description:
            prompt += f"设计灵感：{description}。"
        
        # 不再直接列出操作，而是从操作中提取设计风格
        if operations and len(operations) > 0:
            # 可以根据操作类型推断风格，但不显示具体操作名称
            prompt += "设计风格：时尚、专业、艺术感。"
        
        prompt += f"设计要求：现代感、科技感、渐变色背景、简洁大气、抽象图案、适合作为应用图标。不要将 {operations} 中的操作指令直接生成在图片中"
        
        logger.info(f"🎨 开始生成风格卡图片")
        logger.info(f"   提示词: {prompt}")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ]
        
        response = MultiModalConversation.call(
            api_key=QWEN_API_KEY,
            model="qwen-image-plus",
            messages=messages,
            result_format='message',
            stream=False,
            watermark=False,  # 不添加水印
            prompt_extend=True,  # 自动扩展提示词
            negative_prompt='ugly, blurry, low quality, text, watermark',
            size=size
        )
        
        if response.status_code == 200:
            logger.info(f"✅ 图片生成成功")
            
            # 从响应中提取图片URL
            output = response.output
            if output and 'choices' in output:
                choices = output['choices']
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    content = message.get('content', [])
                    
                    # 查找图片URL
                    for item in content:
                        if isinstance(item, dict) and 'image' in item:
                            image_url = item['image']
                            logger.info(f"   图片URL: {image_url}")
                            
                            # 下载图片到本地
                            local_path = _download_image(image_url, title)
                            return local_path
            
            logger.error("❌ 无法从响应中提取图片URL")
            return None
            
        else:
            logger.error(f"❌ 图片生成失败")
            logger.error(f"   HTTP返回码：{response.status_code}")
            logger.error(f"   错误码：{response.code}")
            logger.error(f"   错误信息：{response.message}")
            return None
            
    except Exception as e:
        logger.exception(f"❌ 生成图片异常: {e}")
        return None


def _download_image(image_url: str, title: str) -> Optional[str]:
    """
    下载图片到本地
    
    Args:
        image_url: 图片URL
        title: 风格卡标题（用于生成文件名）
        
    Returns:
        str: 本地文件路径，失败返回None
    """
    try:
        # 创建保存目录
        project_root = Path(__file__).parent.parent.parent
        images_dir = project_root / "data" / "style_card_images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # 限制长度
        filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.png"
        local_path = images_dir / filename
        
        # 下载图片
        logger.info(f"📥 下载图片: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 保存到本地
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ 图片已保存: {local_path}")
        
        # 返回相对于data目录的路径（用于前端访问）
        try:
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            relative_path = local_path.relative_to(data_dir)
            relative_path_str = str(relative_path).replace('\\', '/')  # 统一使用正斜杠
            logger.info(f"📍 相对路径: {relative_path_str}")
            return relative_path_str
        except ValueError:
            # 如果无法获取相对路径，返回绝对路径
            logger.warning(f"⚠️ 无法获取相对路径，返回绝对路径")
            return str(local_path)
        
    except Exception as e:
        logger.error(f"❌ 下载图片失败: {e}")
        return None


# 测试代码
if __name__ == "__main__":
    # 测试生成图片
    test_path = generate_style_card_image(
        title="电影感风格",
        description="适合制作电影风格的视频，包含转场和调色",
        operations=["添加电影黑边", "应用LUT调色", "添加转场效果"]
    )
    
    if test_path:
        print(f"✅ 测试成功，图片路径: {test_path}")
    else:
        print("❌ 测试失败")