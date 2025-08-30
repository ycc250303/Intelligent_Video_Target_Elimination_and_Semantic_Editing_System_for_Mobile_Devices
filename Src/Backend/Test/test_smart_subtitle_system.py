#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能字幕系统
利用千问的图片理解能力分析视频帧颜色，自动生成对应颜色的字幕
"""

import os
import cv2
import numpy as np
import base64
import json
import logging
from openai import OpenAI
from typing import Dict, List, Tuple, Optional
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartSubtitleSystem:
    """智能字幕系统"""
    
    def __init__(self, api_key: str = None):
        """
        初始化智能字幕系统
        
        Args:
            api_key: 千问API密钥，如果为None则使用环境变量
        """
        self.client = OpenAI(
            api_key=api_key or "sk-20b4e293dc524e6ca819d9b37e2cadd2",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # 颜色映射表：从RGB值到中文颜色名称
        self.color_mapping = {
            'red': '红色',
            'blue': '蓝色',
            'green': '绿色',
            'yellow': '黄色',
            'purple': '紫色',
            'orange': '橙色',
            'pink': '粉色',
            'brown': '棕色',
            'black': '黑色',
            'white': '白色',
            'gray': '灰色',
            'cyan': '青色',
            'magenta': '洋红色',
            'lime': '青柠色',
            'navy': '海军蓝',
            'teal': '蓝绿色',
            'maroon': '栗色',
            'olive': '橄榄色'
        }
        
        # 颜色分析提示词
        self.color_analysis_prompt = """
你是一个专业的颜色分析专家。请分析图片中占比最大的颜色，并按照以下格式返回结果：

格式要求：
1. 只返回一个颜色名称，使用英文
2. 必须是以下颜色之一：red, blue, green, yellow, purple, orange, pink, brown, black, white, gray, cyan, magenta, lime, navy, teal, maroon, olive
3. 不要包含任何其他文字、标点符号或解释

分析标准：
- 选择在图片中视觉占比最大的颜色
- 考虑颜色的饱和度和亮度
- 如果多个颜色占比相近，选择更鲜艳的颜色
- 背景色通常占比最大，优先考虑背景色

请直接返回颜色名称，例如：red
"""
    
    def extract_frame(self, video_path: str, frame_number: int = 0) -> Optional[np.ndarray]:
        """
        从视频中提取指定帧
        
        Args:
            video_path: 视频文件路径
            frame_number: 帧序号（从0开始）
            
        Returns:
            numpy.ndarray: 提取的帧图像，失败返回None
        """
        try:
            video = cv2.VideoCapture(video_path)
            if not video.isOpened():
                logger.error(f"无法打开视频文件: {video_path}")
                return None
            
            # 设置帧位置
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = video.read()
            video.release()
            
            if ret:
                logger.info(f"成功提取第{frame_number}帧")
                return frame
            else:
                logger.error(f"提取第{frame_number}帧失败")
                return None
                
        except Exception as e:
            logger.error(f"提取帧时出错: {e}")
            return None
    
    def encode_image(self, image: np.ndarray) -> str:
        """
        将图像编码为base64字符串
        
        Args:
            image: 图像数组
            
        Returns:
            str: base64编码的字符串
        """
        try:
            # 将BGR转换为RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', image_rgb, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            return ""
    
    def analyze_frame_color(self, frame: np.ndarray) -> Optional[str]:
        """
        使用千问分析帧中占比最大的颜色
        
        Args:
            frame: 视频帧图像
            
        Returns:
            str: 颜色名称（英文），失败返回None
        """
        try:
            # 编码图像
            base64_image = self.encode_image(frame)
            if not base64_image:
                logger.error("图像编码失败")
                return None
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": self.color_analysis_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": "请分析这张图片中占比最大的颜色，只返回颜色名称。"
                        }
                    ]
                }
            ]
            
            # 调用千问API
            completion = self.client.chat.completions.create(
                model="qwen-vl-max-latest",
                messages=messages,
                stream=False,
                max_tokens=10
            )
            
            # 提取颜色名称
            response_text = completion.choices[0].message.content.strip().lower()
            logger.info(f"千问返回的颜色分析结果: {response_text}")
            
            # 验证颜色名称是否有效
            if response_text in self.color_mapping:
                return response_text
            else:
                logger.warning(f"无效的颜色名称: {response_text}")
                # 尝试从文本中提取颜色名称
                for color_name in self.color_mapping.keys():
                    if color_name in response_text:
                        return color_name
                
                # 如果都失败，返回默认颜色
                logger.warning("无法识别颜色，使用默认颜色: blue")
                return "blue"
                
        except Exception as e:
            logger.error(f"颜色分析失败: {e}")
            return None
    
    def generate_smart_subtitle(self, video_path: str, start_time: float = 0.0, 
                               duration: float = 3.0, frame_number: int = 0) -> Dict[str, any]:
        """
        生成智能字幕
        
        Args:
            video_path: 视频文件路径
            start_time: 字幕开始时间（秒）
            duration: 字幕持续时间（秒）
            frame_number: 用于颜色分析的帧序号
            
        Returns:
            Dict: {
                'success': bool,
                'subtitle_text': str,
                'color_name': str,
                'color_rgb': tuple,
                'action_command': str
            }
        """
        try:
            logger.info(f"开始生成智能字幕，分析第{frame_number}帧")
            
            # 1. 提取指定帧
            frame = self.extract_frame(video_path, frame_number)
            if frame is None:
                return {
                    'success': False,
                    'error': '无法提取视频帧'
                }
            
            # 2. 分析帧中占比最大的颜色
            color_name = self.analyze_frame_color(frame)
            if not color_name:
                return {
                    'success': False,
                    'error': '颜色分析失败'
                }
            
            # 3. 获取中文颜色名称
            chinese_color = self.color_mapping.get(color_name, color_name)
            
            # 4. 生成字幕文本
            subtitle_text = f"这是{chinese_color}的视频"
            
            # 5. 获取颜色RGB值（用于后续处理）
            color_rgb = self._get_color_rgb(color_name)
            
            # 6. 生成操作命令
            action_command = f"action: add_text text={subtitle_text} duration={duration} start_time={start_time} editor=ffmpeg"
            
            result = {
                'success': True,
                'subtitle_text': subtitle_text,
                'color_name': color_name,
                'chinese_color': chinese_color,
                'color_rgb': color_rgb,
                'action_command': action_command,
                'frame_number': frame_number,
                'start_time': start_time,
                'duration': duration
            }
            
            logger.info(f"智能字幕生成成功: {subtitle_text} (颜色: {chinese_color})")
            return result
            
        except Exception as e:
            logger.error(f"生成智能字幕时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_color_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """
        获取颜色的RGB值
        
        Args:
            color_name: 颜色名称（英文）
            
        Returns:
            Tuple[int, int, int]: RGB值
        """
        color_rgb_map = {
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128),
            'orange': (255, 165, 0),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'gray': (128, 128, 128),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'lime': (0, 255, 0),
            'navy': (0, 0, 128),
            'teal': (0, 128, 128),
            'maroon': (128, 0, 0),
            'olive': (128, 128, 0)
        }
        
        return color_rgb_map.get(color_name, (0, 0, 255))  # 默认蓝色
    
    def batch_analyze_frames(self, video_path: str, frame_numbers: List[int]) -> List[Dict]:
        """
        批量分析多个帧的颜色
        
        Args:
            video_path: 视频文件路径
            frame_numbers: 要分析的帧序号列表
            
        Returns:
            List[Dict]: 每帧的颜色分析结果
        """
        results = []
        
        for frame_num in frame_numbers:
            logger.info(f"分析第{frame_num}帧")
            
            # 提取帧
            frame = self.extract_frame(video_path, frame_num)
            if frame is None:
                results.append({
                    'frame_number': frame_num,
                    'success': False,
                    'error': '无法提取帧'
                })
                continue
            
            # 分析颜色
            color_name = self.analyze_frame_color(frame)
            if color_name:
                results.append({
                    'frame_number': frame_num,
                    'success': True,
                    'color_name': color_name,
                    'chinese_color': self.color_mapping.get(color_name, color_name),
                    'color_rgb': self._get_color_rgb(color_name)
                })
            else:
                results.append({
                    'frame_number': frame_num,
                    'success': False,
                    'error': '颜色分析失败'
                })
        
        return results
    
    def generate_color_report(self, video_path: str, sample_frames: int = 5) -> Dict:
        """
        生成视频颜色分析报告
        
        Args:
            video_path: 视频文件路径
            sample_frames: 采样帧数量
            
        Returns:
            Dict: 颜色分析报告
        """
        try:
            # 获取视频信息
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            video.release()
            
            if total_frames == 0:
                return {
                    'success': False,
                    'error': '无法获取视频信息'
                }
            
            # 选择采样帧（均匀分布）
            frame_numbers = []
            if total_frames <= sample_frames:
                frame_numbers = list(range(total_frames))
            else:
                step = total_frames // sample_frames
                frame_numbers = [i * step for i in range(sample_frames)]
            
            # 分析采样帧
            frame_analysis = self.batch_analyze_frames(video_path, frame_numbers)
            
            # 统计颜色分布
            color_count = {}
            for result in frame_analysis:
                if result['success']:
                    color = result['chinese_color']
                    color_count[color] = color_count.get(color, 0) + 1
            
            # 找出主要颜色
            main_color = max(color_count.items(), key=lambda x: x[1]) if color_count else None
            
            report = {
                'success': True,
                'video_path': video_path,
                'total_frames': total_frames,
                'sampled_frames': frame_numbers,
                'frame_analysis': frame_analysis,
                'color_distribution': color_count,
                'main_color': main_color[0] if main_color else '未知',
                'recommendation': f"建议使用{main_color[0]}作为字幕颜色" if main_color else "无法确定推荐颜色"
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成颜色报告时出错: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def test_smart_subtitle_system():
    """测试智能字幕系统"""
    
    print("=== 测试智能字幕系统 ===\n")
    
    # 创建系统实例
    system = SmartSubtitleSystem()
    
    # 测试视频路径（请替换为实际的视频路径）
    test_video = "uploads/001.mp4"  # 使用你现有的测试视频
    
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        print("请确保有可用的测试视频文件")
        return
    
    print(f"使用测试视频: {test_video}")
    
    # 测试1: 生成智能字幕
    print("\n--- 测试1: 生成智能字幕 ---")
    result = system.generate_smart_subtitle(
        video_path=test_video,
        start_time=0.0,
        duration=3.0,
        frame_number=0
    )
    
    if result['success']:
        print(f"✓ 字幕生成成功")
        print(f"  字幕文本: {result['subtitle_text']}")
        print(f"  颜色名称: {result['chinese_color']} ({result['color_name']})")
        print(f"  RGB值: {result['color_rgb']}")
        print(f"  操作命令: {result['action_command']}")
    else:
        print(f"✗ 字幕生成失败: {result.get('error', '未知错误')}")
    
    # 测试2: 批量分析帧颜色
    print("\n--- 测试2: 批量分析帧颜色 ---")
    frame_numbers = [0, 10, 20, 30, 40]  # 分析多个帧
    batch_results = system.batch_analyze_frames(test_video, frame_numbers)
    
    for result in batch_results:
        if result['success']:
            print(f"  第{result['frame_number']}帧: {result['chinese_color']}")
        else:
            print(f"  第{result['frame_number']}帧: 分析失败 - {result['error']}")
    
    # 测试3: 生成颜色报告
    print("\n--- 测试3: 生成颜色报告 ---")
    report = system.generate_color_report(test_video, sample_frames=5)
    
    if report['success']:
        print(f"✓ 颜色报告生成成功")
        print(f"  主要颜色: {report['main_color']}")
        print(f"  颜色分布: {report['color_distribution']}")
        print(f"  建议: {report['recommendation']}")
    else:
        print(f"✗ 颜色报告生成失败: {report.get('error', '未知错误')}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_smart_subtitle_system()

