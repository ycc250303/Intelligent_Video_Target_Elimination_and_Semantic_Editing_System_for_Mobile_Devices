#!/usr/bin/env python3
"""
多模态输入处理器
支持文本、图片、视频等多种输入方式
"""

import os
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """媒体类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


@dataclass
class MediaInput:
    """媒体输入数据类"""
    media_type: MediaType
    content: Any  # 可以是文本、文件路径、URL或base64编码
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.media_type, str):
            self.media_type = MediaType(self.media_type)


@dataclass
class MultimodalInput:
    """多模态输入数据类"""
    text: str  # 主要文本指令
    images: List[MediaInput] = field(default_factory=list)
    videos: List[MediaInput] = field(default_factory=list)
    audios: List[MediaInput] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_images(self) -> bool:
        """是否包含图片"""
        return len(self.images) > 0
    
    def has_videos(self) -> bool:
        """是否包含视频"""
        return len(self.videos) > 0
    
    def has_audios(self) -> bool:
        """是否包含音频"""
        return len(self.audios) > 0
    
    def is_text_only(self) -> bool:
        """是否仅包含文本"""
        return not (self.has_images() or self.has_videos() or self.has_audios())
    
    def get_modal_type(self) -> str:
        """获取模态类型描述"""
        modals = ["text"]
        if self.has_images():
            modals.append("image")
        if self.has_videos():
            modals.append("video")
        if self.has_audios():
            modals.append("audio")
        return "+".join(modals)


class MultimodalProcessor:
    """多模态输入处理器"""
    
    def __init__(self):
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        self.supported_audio_formats = ['.mp3', '.wav', '.aac', '.ogg', '.flac']
    
    def process_input(
        self, 
        text: str,
        image_paths: Optional[List[str]] = None,
        video_paths: Optional[List[str]] = None,
        audio_paths: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MultimodalInput:
        """
        处理多模态输入
        
        Args:
            text: 文本指令
            image_paths: 图片文件路径列表
            video_paths: 视频文件路径列表
            audio_paths: 音频文件路径列表
            metadata: 额外元数据
            
        Returns:
            MultimodalInput: 处理后的多模态输入对象
        """
        multimodal_input = MultimodalInput(
            text=text,
            metadata=metadata or {}
        )
        
        # 处理图片
        if image_paths:
            for img_path in image_paths:
                media_input = self._process_image(img_path)
                if media_input:
                    multimodal_input.images.append(media_input)
        
        # 处理视频
        if video_paths:
            for video_path in video_paths:
                media_input = self._process_video(video_path)
                if media_input:
                    multimodal_input.videos.append(media_input)
        
        # 处理音频
        if audio_paths:
            for audio_path in audio_paths:
                media_input = self._process_audio(audio_path)
                if media_input:
                    multimodal_input.audios.append(media_input)
        
        logger.info(f"处理多模态输入: {multimodal_input.get_modal_type()}")
        return multimodal_input
    
    def _process_image(self, image_path: str) -> Optional[MediaInput]:
        """处理图片输入"""
        try:
            path = Path(image_path)
            
            # 检查文件是否存在
            if not path.exists():
                logger.warning(f"图片文件不存在: {image_path}")
                return None
            
            # 检查文件格式
            if path.suffix.lower() not in self.supported_image_formats:
                logger.warning(f"不支持的图片格式: {path.suffix}")
                return None
            
            # 获取文件信息
            file_size = path.stat().st_size
            
            return MediaInput(
                media_type=MediaType.IMAGE,
                content=str(path.absolute()),
                metadata={
                    "filename": path.name,
                    "size": file_size,
                    "format": path.suffix.lower()
                }
            )
        except Exception as e:
            logger.error(f"处理图片失败: {e}")
            return None
    
    def _process_video(self, video_path: str) -> Optional[MediaInput]:
        """处理视频输入"""
        try:
            path = Path(video_path)
            
            # 检查文件是否存在
            if not path.exists():
                logger.warning(f"视频文件不存在: {video_path}")
                return None
            
            # 检查文件格式
            if path.suffix.lower() not in self.supported_video_formats:
                logger.warning(f"不支持的视频格式: {path.suffix}")
                return None
            
            # 获取文件信息
            file_size = path.stat().st_size
            
            return MediaInput(
                media_type=MediaType.VIDEO,
                content=str(path.absolute()),
                metadata={
                    "filename": path.name,
                    "size": file_size,
                    "format": path.suffix.lower()
                }
            )
        except Exception as e:
            logger.error(f"处理视频失败: {e}")
            return None
    
    def _process_audio(self, audio_path: str) -> Optional[MediaInput]:
        """处理音频输入"""
        try:
            path = Path(audio_path)
            
            # 检查文件是否存在
            if not path.exists():
                logger.warning(f"音频文件不存在: {audio_path}")
                return None
            
            # 检查文件格式
            if path.suffix.lower() not in self.supported_audio_formats:
                logger.warning(f"不支持的音频格式: {path.suffix}")
                return None
            
            # 获取文件信息
            file_size = path.stat().st_size
            
            return MediaInput(
                media_type=MediaType.AUDIO,
                content=str(path.absolute()),
                metadata={
                    "filename": path.name,
                    "size": file_size,
                    "format": path.suffix.lower()
                }
            )
        except Exception as e:
            logger.error(f"处理音频失败: {e}")
            return None
    
    def convert_to_qwen_format(self, multimodal_input: MultimodalInput) -> List[Dict[str, Any]]:
        """
        将多模态输入转换为千问模型API格式
        
        Args:
            multimodal_input: 多模态输入对象
            
        Returns:
            List[Dict]: 千问API格式的消息内容
        """
        content = []
        
        # 添加图片
        for img in multimodal_input.images:
            content.append(self._convert_image_to_qwen(img))
        
        # 添加视频
        for video in multimodal_input.videos:
            content.append(self._convert_video_to_qwen(video))
        
        # 添加文本（文本通常放在最后）
        content.append({
            "type": "text",
            "text": multimodal_input.text
        })
        
        return content
    
    def _convert_image_to_qwen(self, media_input: MediaInput) -> Dict[str, Any]:
        """将图片转换为千问格式"""
        # 判断是URL还是本地文件
        if media_input.content.startswith('http://') or media_input.content.startswith('https://'):
            image_url = media_input.content
        else:
            # 本地文件，使用file:// URL或base64编码
            path = Path(media_input.content)
            # 对于小图片，使用base64编码
            if media_input.metadata.get('size', 0) < 5 * 1024 * 1024:  # 小于5MB
                with open(path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                mime_type = self._get_image_mime_type(path.suffix)
                image_url = f"data:{mime_type};base64,{image_data}"
            else:
                image_url = path.as_uri()
        
        return {
            "type": "image_url",
            "image_url": {"url": image_url}
        }
    
    def _convert_video_to_qwen(self, media_input: MediaInput) -> Dict[str, Any]:
        """将视频转换为千问格式"""
        # 判断是URL还是本地文件
        if media_input.content.startswith('http://') or media_input.content.startswith('https://'):
            video_url = media_input.content
        else:
            # 本地文件，使用base64编码
            path = Path(media_input.content)
            file_size_mb = media_input.metadata.get('size', 0) / (1024 * 1024)
            
            # 对于小视频（<20MB），使用base64编码
            if file_size_mb < 20:
                with open(path, 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                mime_type = self._get_video_mime_type(path.suffix)
                video_url = f"data:{mime_type};base64,{video_data}"
            else:
                # 大视频使用文件路径（需要配合HTTP服务器）
                logger.warning(f"视频文件较大 ({file_size_mb:.2f}MB)，建议先上传到服务器")
                video_url = path.as_uri()
        
        return {
            "type": "video_url",
            "video_url": {"url": video_url}
        }
    
    def _get_image_mime_type(self, suffix: str) -> str:
        """获取图片MIME类型"""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(suffix.lower(), 'image/jpeg')
    
    def _get_video_mime_type(self, suffix: str) -> str:
        """获取视频MIME类型"""
        mime_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.flv': 'video/x-flv',
            '.wmv': 'video/x-ms-wmv'
        }
        return mime_types.get(suffix.lower(), 'video/mp4')


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = MultimodalProcessor()
    
    # 测试1: 纯文本
    print("=== 测试1: 纯文本输入 ===")
    input1 = processor.process_input(
        text="把这个视频剪掉前3秒"
    )
    print(f"模态类型: {input1.get_modal_type()}")
    print(f"是否纯文本: {input1.is_text_only()}")
    
    # 测试2: 文本+图片
    print("\n=== 测试2: 文本+图片 ===")
    input2 = processor.process_input(
        text="使用这张图片生成视频",
        image_paths=["D:/test/logo.png"]
    )
    print(f"模态类型: {input2.get_modal_type()}")
    print(f"包含图片: {input2.has_images()}")
    
    # 测试3: 文本+视频
    print("\n=== 测试3: 文本+视频 ===")
    input3 = processor.process_input(
        text="分析这个视频的内容",
        video_paths=["D:/test/video.mp4"]
    )
    print(f"模态类型: {input3.get_modal_type()}")
    print(f"包含视频: {input3.has_videos()}")
    
    # 测试4: 文本+视频+图片
    print("\n=== 测试4: 文本+视频+图片 ===")
    input4 = processor.process_input(
        text="把这个图片作为封面添加到视频开头",
        image_paths=["D:/test/cover.jpg"],
        video_paths=["D:/test/video.mp4"]
    )
    print(f"模态类型: {input4.get_modal_type()}")
    
    # 测试转换为千问格式
    print("\n=== 测试转换为千问格式 ===")
    if not input1.is_text_only():
        qwen_content = processor.convert_to_qwen_format(input1)
        print(f"千问格式内容项数: {len(qwen_content)}")

