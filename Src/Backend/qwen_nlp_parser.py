#!/usr/bin/env python3
"""
千问模型版本的 NLP 解析器
基于阿里云 DashScope 的千问模型进行自然语言指令解析
"""

import uuid
import time
import logging
import os
from typing import Dict, Any, Callable, Optional, Tuple, List
from openai import OpenAI
from config import SYSTEM_PROMPT


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 千问模型配置
QWEN_API_KEY = "sk-20b4e293dc524e6ca819d9b37e2cadd2"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"  # 可以改为 qwen-turbo, qwen-max 等

# 编辑器类型枚举
EDITOR_TYPES = {
    'moviepy': 'MoviePyVideoEditor',
    'ffmpeg': 'FFmpegVideoEditor',
    'opencv': 'OpenCVVideoEditor'
}

# 全局历史记录
history = []

# 操作注册表
OPERATIONS: Dict[str, Dict[str, Any]] = {
    'trim': {
        'params': {
            'start': {'type': float, 'default': 0.0, 'required': True},
            'end': {'type': float, 'default': None, 'required': False}
        },
        'description': '裁剪视频，start=秒数，end=秒数（可选，默认为视频末尾）。例：剪掉前 1 秒 → action: trim start=1.0',
        'supported_editors': ['moviepy', 'ffmpeg', 'opencv']
    },
    'add_transition': {
        'params': {
            'type': {'type': str, 'default': 'fade', 'required': True},
            'duration': {'type': float, 'default': 1.0, 'required': True},
            'start_time': {'type': float, 'default': 0.0, 'required': False}
        },
        'description': '添加转场效果，type=转场类型，duration=秒数，start_time=开始时间（秒）。',
        'supported_editors': ['moviepy', 'ffmpeg']
    },
    'speed': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整视频速度，factor=倍数。',
        'supported_editors': ['moviepy']
    },
    'add_text': {
        'params': {
            'text': {'type': str, 'default': '', 'required': True},
            'fontsize': {'type': int, 'default': 24, 'required': False},
            'duration': {'type': float, 'default': 5.0, 'required': False},
            'position': {'type': str, 'default': 'center', 'required': False},
            'start_time': {'type': float, 'default': 0.0, 'required': False}
        },
        'description': '添加字幕，text=内容，fontsize=字体大小，duration=秒数，position=位置，start_time=开始时间（秒）。',
        'supported_editors': ['ffmpeg']
    },
    'adjust_volume': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整音量，factor=倍数。',
        'supported_editors': ['moviepy']
    },
    'rotate': {
        'params': {
            'angle': {'type': float, 'default': 90.0, 'required': True}
        },
        'description': '旋转视频，angle=角度。',
        'supported_editors': ['moviepy']
    },
    'crop': {
        'params': {
            'x1': {'type': float, 'default': 0.0, 'required': True},
            'y1': {'type': float, 'default': 0.0, 'required': True},
            'x2': {'type': float, 'default': None, 'required': True},
            'y2': {'type': float, 'default': None, 'required': True}
        },
        'description': '裁剪画面，x1,y1=左上角坐标，x2,y2=右下角坐标。',
        'supported_editors': ['moviepy']
    },
    'add_background_music': {
        'params': {
            'audio_file': {'type': str, 'default': '', 'required': True},
            'video_start_time': {'type': float, 'default': 0.0, 'required': False},
            'video_end_time': {'type': float, 'default': None, 'required': False},
            'audio_start_time': {'type': float, 'default': 0.0, 'required': False},
            'audio_end_time': {'type': float, 'default': None, 'required': False},
            'mix': {'type': bool, 'default': False, 'required': False},
            'overwrite': {'type': bool, 'default': False, 'required': False},
        },
        'description': '添加背景音乐，支持精确时间控制。',
        'supported_editors': ['moviepy']
    },
    'adjust_brightness': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整亮度，factor=倍数。',
        'supported_editors': ['moviepy']
    },
    'adjust_contrast': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整对比度，factor=倍数。',
        'supported_editors': ['moviepy']
    },
    'make_black_and_white': {
        'params': {
            'start_time': {'type': float, 'default': 0.0, 'required': False},
            'duration': {'type': float, 'default': None, 'required': False}
        },
        'description': '将视频变为黑白效果。',
        'supported_editors': ['ffmpeg']
    }
}

def init_qwen_client() -> OpenAI:
    """
    初始化千问模型客户端
    """
    if not QWEN_API_KEY:
        raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")
    
    return OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
    )

def ask_qwen(user_input: str, history: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str], List[Dict[str, str]]]:
    """
    使用千问模型处理用户的单次提问，调用 API 并返回响应结果，同时更新历史对话。

    Args:
        user_input: 用户输入的视频剪辑指令。
        history: 历史对话列表。

    Returns:
        tuple: (API 响应内容, 确认消息, 更新后的历史对话)。
    """
    try:
        client = init_qwen_client()
        
        # 构建消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # 添加历史对话
        for msg in history:
            messages.append(msg)
        
        # 添加当前用户输入
        new_message = {"role": "user", "content": user_input}
        messages.append(new_message)
        
        start_time = time.time()
        
        # 调用千问模型
        completion = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=1000
        )
        
        content = completion.choices[0].message.content
        logger.info(f'千问模型响应: {content}')
        
        # 更新历史记录
        history.append(new_message)
        assistant_message = {"role": "assistant", "content": content}
        history.append(assistant_message)
        
        # 生成确认消息
        clean_content = content
        if content.startswith("assistant:"):
            clean_content = content.replace("assistant:", "").strip()
        
        confirmation = generate_confirmation(clean_content)
        
        end_time = time.time()
        logger.info(f'千问模型请求耗时: {end_time - start_time:.2f}秒')
        
        return content, confirmation, history
        
    except Exception as e:
        logger.error(f'千问模型调用失败: {e}')
        return None, f"千问模型调用失败: {str(e)}", history

def generate_confirmation(action_str: str) -> str:
    """
    根据 LLM 的操作指令生成自然语言确认消息。

    Args:
        action_str: LLM 返回的操作指令，例如 'action: trim start=10 end=20'.

    Returns:
        str: 自然语言确认消息。
    """
    if not action_str:
        return ""

    try:
        action_parts = action_str.strip().split()
        if not action_parts or action_parts[0] != 'action:':
            return ""
        
        action = action_parts[1]
        if action not in OPERATIONS:
            return ""

        # 不再生成详细的确认消息，直接返回空字符串
        return ""
    except Exception as e:
        return ""

def process_instruction(user_input: str) -> Tuple[Optional[str], str, List[Dict[str, str]]]:
    """
    处理用户输入的自然语言指令，返回解析后的操作指令和确认消息。

    Args:
        user_input: 用户输入的自然语言指令。

    Returns:
        Tuple: (操作指令, 确认消息, 更新后的历史记录)。
    """
    global history
    
    try:
        content, confirmation, history = ask_qwen(user_input, history)
        
        # 如果千问模型服务失败，尝试本地解析
        if content is None:
            logger.warning("千问模型服务不可用，尝试本地指令解析")
            content = local_instruction_parser(user_input)
            confirmation = ""
            
        return content, confirmation, history
        
    except Exception as e:
        logger.error(f"处理指令时出错: {e}")
        # 尝试本地解析作为备用方案
        try:
            content = local_instruction_parser(user_input)
            confirmation = ""
            return content, confirmation, history
        except Exception as local_error:
            logger.error(f"本地解析也失败: {local_error}")
            return None, "指令处理失败，请稍后重试", history

def local_instruction_parser(user_input: str) -> Optional[str]:
    """
    本地指令解析器，当千问模型服务不可用时的备用方案
    """
    try:
        # 简单的关键词匹配
        user_input_lower = user_input.lower()
        
        if "裁剪" in user_input_lower or "trim" in user_input_lower:
            # 提取时间参数
            import re
            time_match = re.search(r'(\d+(?:\.\d+)?)\s*秒', user_input)
            if time_match:
                start_time = float(time_match.group(1))
                return f"action: trim start={start_time} end={start_time + 5.0} editor=moviepy"
            else:
                return "action: trim start=0.0 end=5.0 editor=moviepy"
                
        elif "调整亮度" in user_input_lower or "亮度" in user_input_lower:
            return "action: adjust_brightness factor=1.2 editor=moviepy"
            
        elif "调整对比度" in user_input_lower or "对比度" in user_input_lower:
            return "action: adjust_contrast factor=1.2 editor=moviepy"
            
        elif "添加字幕" in user_input_lower or "字幕" in user_input_lower:
            return "action: add_text text='字幕内容' start_time=0.0 duration=5.0 editor=ffmpeg"
            
        elif "转场" in user_input_lower or "过渡" in user_input_lower or "transition" in user_input_lower:
            return "action: add_transition type=fade duration=1.0 start_time=1.0 editor=moviepy"
            
        elif "黑白" in user_input_lower or "黑白效果" in user_input_lower:
            return "action: make_black_and_white start_time=0.0 duration=1.0 editor=ffmpeg"
            
        else:
            # 默认返回一个基本操作
            return "action: adjust_brightness factor=1.0 editor=moviepy"
            
    except Exception as e:
        logger.error(f"本地解析出错: {e}")
        return None

class DialogueManager:
    """对话管理器，用于处理用户交互和生成自然语言响应"""
    
    def __init__(self):
        self.history = []
        self.context = {
            "current_video": None,
            "last_operation": None,
            "total_operations": 0
        }
        
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入，返回响应信息。

        Args:
            user_input: 用户输入的自然语言指令
            
        Returns:
            Dict: {
                "response": 处理结果的自然语言响应,
                "success": 是否成功执行,
                "action": 执行的操作指令
            }
        """
        try:
            # 处理用户输入
            result = self.process_instruction(user_input)
            print("result: ", result)
            
            if not result["success"]:
                return {
                    "response": result["response"],
                    "success": False,
                    "action": None
                }
                
            # 如果是撤销操作
            if result["action"] == "undo":
                return {
                    "response": result["response"],
                    "success": True,
                    "action": "undo"
                }
                    
            # 如果是帮助信息
            if not result["action"]:
                return {
                    "response": result["response"],
                    "success": True,
                    "action": None
                }
                
            return {
                "response": result["response"],
                "success": True,
                "action": result["action"]
            }
            
        except Exception as e:
            logger.error(f"处理用户输入失败: {e}")
            return {
                "response": f"处理用户输入时出错: {str(e)}",
                "success": False,
                "action": None
            }
    
    def process_instruction(self, user_input: str) -> Dict[str, Any]:
        """
        处理指令并返回结果
        """
        content, confirmation, updated_history = process_instruction(user_input)
        self.history = updated_history
        
        if content is None:
            return {
                "response": "无法理解您的指令，请重试",
                "success": False,
                "action": None
            }
        
        # 检查是否是操作指令
        if content.startswith("action:"):
            return {
                "response": confirmation or "指令已解析，准备执行",
                "success": True,
                "action": content
            }
        else:
            return {
                "response": content,
                "success": True,
                "action": None
            }
    
    def set_current_video(self, video_path: str):
        """设置当前处理的视频文件"""
        self.context["current_video"] = video_path
        
    def clear_history(self):
        """清空对话历史"""
        self.history = []
        self.context = {
            "current_video": None,
            "last_operation": None,
            "total_operations": 0
        }

# 测试函数
def test_qwen_nlp():
    """
    测试千问模型 NLP 解析功能
    """
    print("=== 测试千问模型 NLP 解析功能 ===")
    
    test_instructions = [
        "把开头 1 秒剪掉",
        "片头加 1.5 秒淡入效果",
        "整体速度调到 1.5 倍",
        "打字幕 Hello 3 秒放左下",
        "声音小一半"
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        print(f"\n测试 {i}: {instruction}")
        try:
            content, confirmation, history = process_instruction(instruction)
            print(f"解析结果: {content}")
            print(f"确认消息: {confirmation}")
        except Exception as e:
            print(f"测试失败: {e}")

if __name__ == "__main__":
    test_qwen_nlp()
