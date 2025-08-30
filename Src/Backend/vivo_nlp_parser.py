import uuid
import time
import requests
import logging
from typing import Dict, Any, Callable, Optional, Tuple, List
from auth_util_tools import gen_sign_headers
from config import APP_ID, APP_KEY, URI, DOMAIN, METHOD, SYSTEM_PROMPT

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 编辑器类型枚举
EDITOR_TYPES = {
    'moviepy': 'MoviePyVideoEditor',
    'ffmpeg': 'FFmpegVideoEditor', 
    'opencv': 'OpenCVVideoEditor'   # 示例：未来可能添加的编辑器
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
        'supported_editors': ['moviepy', 'ffmpeg', 'opencv']  # 支持该操作的编辑器类型
    },
    'add_transition': {
        'params': {
            'type': {'type': str, 'default': 'fade', 'required': True},
            'duration': {'type': float, 'default': 1.0, 'required': True},
            'start_time': {'type': float, 'default': 0.0, 'required': False}
        },
        'description': '添加转场效果，type=转场类型，duration=秒数，start_time=开始时间（秒）。',
        'supported_editors': ['moviepy', 'ffmpeg']  # 现在ffmpeg也支持转场效果
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
        'description': '添加背景音乐，支持精确时间控制。audio_file=音频文件路径，video_start_time=视频中音频起始时间，video_end_time=视频中音频结束时间，audio_start_time=音频文件起始时间，audio_end_time=音频文件结束时间，overwrite=是否覆盖原音频。',
        'supported_editors': ['moviepy']
    },
    'add_audio_segment': {
        'params': {
            'audio_file': {'type': str, 'default': '', 'required': True},
            'video_start_time': {'type': float, 'default': 0.0, 'required': True},
            'video_end_time': {'type': float, 'default': 0.0, 'required': True},
            'audio_start_time': {'type': float, 'default': 0.0, 'required': False},
            'audio_end_time': {'type': float, 'default': None, 'required': False},
            'volume': {'type': float, 'default': 1.0, 'required': False},
            'mix': {'type': bool, 'default': True, 'required': False},
            'overwrite': {'type': bool, 'default': False, 'required': False},
        },
        'description': '在视频的特定时间段添加音频片段。audio_file=音频文件路径，video_start_time=视频中音频起始时间，video_end_time=视频中音频结束时间，audio_start_time=音频文件起始时间，audio_end_time=音频文件结束时间，volume=音量倍数，overwrite=是否覆盖原音频。',
        'supported_editors': ['moviepy']
    },
    'concatenate': {
        'params': {
            'second_video': {'type': str, 'default': '', 'required': True},
            'transition': {'type': str, 'default': 'none', 'required': False},
            'transition_duration': {'type': float, 'default': 1.0, 'required': False}
        },
        'description': '合并另一个视频，支持转场效果。second_video=视频文件路径，transition=转场类型(none/fade)，transition_duration=转场持续时间。',
        'supported_editors': ['moviepy']
    },
    'concatenate_multiple': {
        'params': {
            'video_files': {'type': list, 'default': [], 'required': True},
            'transition': {'type': str, 'default': 'none', 'required': False},
            'transition_duration': {'type': float, 'default': 1.0, 'required': False}
        },
        'description': '合并多个视频文件，支持转场效果。video_files=视频文件路径列表，transition=转场类型(none/fade)，transition_duration=转场持续时间。',
        'supported_editors': ['moviepy']
    },
    'adjust_volume': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整音量，factor=倍数（例如 0.5 降低一半）。',
        'supported_editors': ['moviepy']
    },
    'rotate': {
        'params': {
            'angle': {'type': float, 'default': 90.0, 'required': True}
        },
        'description': '旋转视频，angle=角度（顺时针，单位：度）。',
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
    'adjust_brightness': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整亮度，factor=倍数（大于1增亮，小于1减暗）。',
        'supported_editors': ['moviepy']
    },
    "adjust_contrast": {
        "params": {
            "factor": {"type": float, "default": 1.0, "required": True}
        },
        "description": "调整对比度，factor=倍数（大于1增强，小于1减弱）。",
        'supported_editors': ['moviepy'] 
    },
    "adjust_saturation": {
    "params": {
        "factor": {"type": float, "default": 1.0, "required": True},
        "video_start_time": {"type": float, "default": 0.0, "required": False},
        "video_end_time": {"type": float, "default": None, "required": False}
    },
    "description": "调整饱和度，factor=倍数（0.0为黑白，1.0为正常，大于1增强饱和度）。支持指定时间段调整。",
    'supported_editors': ['moviepy'] 
},
    "make_black_and_white": {
        "params": {
            "start_time": {"type": float, "default": 0.0, "required": False},
            "duration": {"type": float, "default": 1.0, "required": False}
        },
        "description": "将视频变为黑白效果，start_time=开始时间（秒），duration=持续时间（秒）。",
        'supported_editors': ['ffmpeg']
    }
}

def init_config() -> Callable:
    """
    初始化 API 调用所需的配置信息，并返回处理用户提问的函数。

    Returns:
        Callable: 处理用户单次提问的函数。
    """

    def ask_qwen(user_input: str, history: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str], List[Dict[str, str]]]:
        """
        处理用户的单次提问，调用 API 并返回响应结果，同时更新历史对话。

        Args:
            user_input: 用户输入的视频剪辑指令。
            history: 历史对话列表。

        Returns:
            tuple: (API 响应内容, 确认消息, 更新后的历史对话)。
        """
        params = {'requestId': str(uuid.uuid4())}
        #logger.info(f'requestId: {params["requestId"]}')

        new_message = {"role": "user", "content": user_input}
        history.append(new_message)

        prompt_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
        prompt_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in prompt_messages])

        data = {
            'prompt': prompt_str,
            'model': 'vivo-BlueLM-TB-Pro',
            'sessionId': str(uuid.uuid4()),
            'extra': {'temperature': 0.9}
        }
        headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
        headers['Content-Type'] = 'application/json'

        start_time = time.time()
        url = f'https://{DOMAIN}{URI}'
        
        # 添加重试机制和SSL错误处理
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
                break  # 成功则跳出循环
            except requests.exceptions.SSLError as e:
                retry_count += 1
                logger.warning(f'SSL连接错误 (尝试 {retry_count}/{max_retries}): {e}')
                if retry_count >= max_retries:
                    logger.error(f'SSL连接失败，已达到最大重试次数')
                    return None, "网络连接失败，请检查网络设置或稍后重试", history
                time.sleep(2)  # 等待2秒后重试
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f'网络请求错误 (尝试 {retry_count}/{max_retries}): {e}')
                if retry_count >= max_retries:
                    logger.error(f'网络请求失败，已达到最大重试次数')
                    return None, "网络请求失败，请检查网络连接", history
                time.sleep(2)  # 等待2秒后重试
            except Exception as e:
                logger.error(f'未知错误: {e}')
                return None, f"请求处理失败: {str(e)}", history

        content = None
        confirmation = None
        if response.status_code == 200:
            res_obj = response.json()
            # 只输出content和clearHistory字段
            content_info = res_obj.get('data', {}).get('content', '') if res_obj.get('data') else ''
            clear_history = res_obj.get('data', {}).get('clearHistory', '') if res_obj.get('data') else ''
            logger.info(f'content: {content_info}, clearHistory: {clear_history}')
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
                logger.info(f'final content:{content}')
                
                # 移除assistant:前缀后再生成确认消息
                clean_content = content
                if content.startswith("assistant:"):
                    clean_content = content.replace("assistant:", "").strip()
                
                confirmation = generate_confirmation(clean_content)
                assistant_message = {"role": "assistant", "content": content}
                history.append(assistant_message)
        else:
            logger.error(f'{response.status_code} {response.text}')
            confirmation = "哎呀，处理指令时出错了，检查一下输入或稍后再试吧！"
        end_time = time.time()
        logger.info(f'请求耗时: {end_time - start_time:.2f}秒')
        return content, confirmation, history

    return ask_qwen

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
    ask_qwen = init_config()
    
    try:
        content, confirmation, history = ask_qwen(user_input, history)
        
        # 如果AI服务失败，尝试本地解析
        if content is None:
            logger.warning("AI服务不可用，尝试本地指令解析")
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
    本地指令解析器，当AI服务不可用时的备用方案
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
        self.ask_qwen = init_config()
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
                "action": 操作指令,
                "response": 自然语言响应,
                "success": 是否成功解析
            }
        """
        try:
            # 处理特殊命令
            if user_input.lower() in ["撤销", "回退", "取消"]:
                return self._handle_undo()
            elif "帮助" in user_input.lower() or "支持什么功能" in user_input:
                return self._get_help_info()
                
            # 处理常规编辑指令
            logger.info(f"当前历史记录长度: {len(self.history)}")
            content, confirmation, updated_history = self.ask_qwen(user_input, self.history)
            
            # 更新历史记录
            self.history = updated_history
            logger.info(f"更新后历史记录长度: {len(self.history)}")
            logger.info(f"生成的确认消息: {confirmation}")
                
            # 处理LLM返回的内容格式（可能包含assistant:前缀）
            if content:
                # 移除assistant:前缀（如果存在）
                if content.startswith("assistant:"):
                    content = content.replace("assistant:", "").strip()
                
                if content.startswith("action:"):
                    self.context["last_operation"] = content
                    self.context["total_operations"] += 1
                    return {
                        "action": content,
                        "response":confirmation,
                        "success": True
                    }
            
            return {
                "action": None,
                "response": "嘿，俺没搞懂你的意思，试试说'帮助'看看支持啥？",
                "success": False
            }
                
        except Exception as e:
            logger.error(f"处理用户输入时出错: {e}")
            return {
                "action": None,
                "response": f"哎呀，出错了！处理你的指令时有点问题: {str(e)}",
                "success": False
            }
        
    def update_personality_card(self, operation_name, params):
        """更新用户偏好并存储到人格卡中"""
        card_name = "clip1"  # 假设我们使用的是名为"clip1"的人格卡
        # card = UserPersonalityCard(card_name) # This line is removed as per the edit hint
        # card.update_operation(operation_name, params) # This line is removed as per the edit hint
        pass # Added pass to avoid syntax error if card is removed
            
    def _handle_undo(self) -> Dict[str, Any]:
        """处理撤销操作"""
        if not self.context["last_operation"]:
            return {
                "action": None,
                "response": "嘿，没啥可以撤回了哦！",
                "success": False
            }
        
        # 清除最后一次操作记录
        self.context["last_operation"] = None
        return {
            "action": "undo",
            "response": "OK，刚刚那步撤掉了！",
            "success": True
        }
        
    def _get_help_info(self) -> Dict[str, Any]:
        """获取帮助信息"""
        help_text = "嘿，我能帮你搞定这些视频编辑：\n\n"
        for op_name, op_info in OPERATIONS.items():
            help_text += f"- {op_info['description']}\n"
        help_text += "\n还能用这些命令：\n"
        help_text += "- 撤销/回退：取消上一步\n"
        help_text += "- 帮助：看看俺能干啥"
        
        return {
            "action": None,
            "response": help_text,
            "success": True
        }

    def set_current_video(self, video_path: str):
        """设置当前正在编辑的视频"""
        self.context["current_video"] = video_path
        
    def clear_history(self):
        """清除对话历史"""
        self.history = []
        self.context["last_operation"] = None
        self.context["total_operations"] = 0

if __name__ == "__main__":
    inputs = ["我想让整个视频速度快一点"]
    for user_input in inputs:
        logger.info(f"处理用户输入: {user_input}")
        content, confirmation, history = process_instruction(user_input)
        print(f"指令: {content}")
        print(f"确认: {confirmation}")  