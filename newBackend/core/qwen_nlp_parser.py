#!/usr/bin/env python3
"""
千问模型版本的 NLP 解析器
基于阿里云 DashScope 的千问模型进行自然语言指令解析
"""

import uuid
import time
import logging
import os
import json
import re
import ast
from typing import Dict, Any, Callable, Optional, Tuple, List
from openai import OpenAI
from config.config import SYSTEM_PROMPT_JSON,QWEN_API_KEY,QWEN_BASE_CHAT_MODEL,QWEN_BASE_CHAT_URL,OPERATIONS,InstructionType
from .multimodal_processor import MultimodalProcessor, MultimodalInput


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局历史记录
history = []

def safe_json_loads(s: str):
    """
    解析 AI 返回字符串为 Python 对象（dict/list）。
    - 优先使用 json.loads
    - 出错时修正常见 Python 字面量（None/True/False）、尾随逗号、单引号等，然后再解析
    - 最后尝试 ast.literal_eval 作为后备
    """
    if isinstance(s, (dict, list)):
        return s
    if not isinstance(s, str):
        raise TypeError("Input must be a string or dict/list")
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        fixed = s
        # Python -> JSON token fixes
        fixed = re.sub(r'\bNone\b', 'null', fixed)
        fixed = re.sub(r'\bTrue\b', 'true', fixed)
        fixed = re.sub(r'\bFalse\b', 'false', fixed)
        # remove trailing commas
        fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
        # heuristic: convert single-quoted strings to double-quoted
        fixed = re.sub(r"(?<!\")'([^']*?)'(?!\")", r'"\1"', fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            try:
                # fallback to parsing Python literal like "{'a': None}"
                return ast.literal_eval(s)
            except Exception as e:
                raise json.JSONDecodeError(f"Could not parse input even after fixes: {e}", s, 0)

def classify_instruction_type(user_input: str, ai_response: str) -> int:
    """
    分类用户指令类型
    
    Args:
        user_input: 用户输入的自然语言指令
        ai_response: AI模型的响应内容
        
    Returns:
        int: 指令类型 (1, 2, 3)
        1: 能直接匹配到操作表中的操作，并且能提取出操作参数
        2: 能直接匹配到操作表中的操作，但是不能提取出操作参数  
        3: 不能匹配到操作表中的操作
    """
    try:
        # 移除可能的 "action:" 前缀
        clean_response = ai_response.replace("action:", "").strip() if ai_response.strip().startswith("action:") else ai_response
        
        response_data = safe_json_loads(clean_response)
        operations = response_data.get("operations", {})
        operation_name = operations.get("operation")

        if not operation_name or operation_name not in OPERATIONS:
            
            return InstructionType.NO_MATCH_OPERATION.value

        params = operations.get("params", {})
        op_def = OPERATIONS[operation_name]

        # 检查是否所有 required 参数都有值
        missing_required = False
        for p_name, p_info in op_def["params"].items():
            if p_info.get("required", False):
                val = params.get(p_name, None)
                if val is None or val == "Unknown":
                    missing_required = True
                    break

        if missing_required:
            return InstructionType.MATCH_OPERATION_BUT_NO_PARAMS.value
        else:
            return InstructionType.MATCH_OPERATION_AND_PARAMS.value

    except Exception as e:
        logger.warning(f"解析AI响应失败: {e}")
        return InstructionType.NO_MATCH_OPERATION.value


def generate_response_by_type(instruction_type: int, ai_response: str, user_input: str) -> str:
    """
    根据指令类型生成相应的响应
    
    Args:
        instruction_type: 指令类型 (1, 2, 3)
        ai_response: AI模型的原始响应
        user_input: 用户输入
        
    Returns:
        str: 处理后的响应
    """
    try:
        # 移除可能的 "action:" 前缀
        clean_response = ai_response.replace("action:", "").strip() if ai_response.strip().startswith("action:") else ai_response
        
        if instruction_type == 1:
            # 第一种情况：按照原规则返回，但需要填充缺失的默认参数
            response_data = json.loads(clean_response)
            operations = response_data.get("operations", {})
            
            if not operations or "operation" not in operations:
                return ai_response
            
            operation_name = operations.get("operation")
            if operation_name not in OPERATIONS:
                return ai_response
            
            operation_def = OPERATIONS[operation_name]
            params = operations.get("params", {})
            
            # 填充缺失的默认参数
            for param_name, param_info in operation_def["params"].items():
                if param_name not in params or params[param_name] is None:
                    # 使用默认值
                    default_value = param_info.get("default")
                    if default_value is not None:
                        params[param_name] = default_value
            
            # 更新响应
            response_data["operations"]["params"] = params
            result = json.dumps(response_data, ensure_ascii=False)
            # 添加 "action:" 前缀标识这是一个可执行的操作（避免重复添加）
            return result if result.startswith("action:") else "action:" + result
            
        elif instruction_type == 2:
            # 第二种情况：返回的值为None的params
            response_data = json.loads(clean_response)
            operations = response_data["operations"]
            
            # 获取操作定义
            operation_name = operations["operation"]
            operation_def = OPERATIONS[operation_name]
            
            # 创建包含None值的params
            none_params = {}
            for param_name, param_info in operation_def["params"].items():
                none_params[param_name] = None
            
            # 构建新的响应
            new_response = {
                "operations": {
                    "operation": operation_name,
                    "params": none_params,
                    "editor": operations.get("editor", "ffmpeg")
                }
            }
            
            result = json.dumps(new_response, ensure_ascii=False)
            # 添加 "action:" 前缀标识这是一个可执行的操作（避免重复添加）
            return result if result.startswith("action:") else "action:" + result
            
        elif instruction_type == 3:
            # 第三种情况：返回空的operations字段
            empty_response = {
                "operations": {}
            }
            return json.dumps(empty_response, ensure_ascii=False)
            
        else:
            logger.error(f"未知的指令类型: {instruction_type}")
            return ai_response
            
    except Exception as e:
        logger.error(f"生成响应时出错: {e}")
        return ai_response

def init_qwen_client() -> OpenAI:
    """
    初始化千问模型客户端
    """
    if not QWEN_API_KEY:
        raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")
    
    return OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_CHAT_URL,
    )

def ask_qwen(user_input: str, history: List[Dict[str, str]]) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    使用千问模型处理用户的单次提问，调用 API 并返回响应结果，同时更新历史对话。

    Args:
        user_input: 用户输入的视频剪辑指令。
        history: 历史对话列表。

    Returns:
        tuple: (API 响应内容, 更新后的历史对话)。
    """
    try:
        client = init_qwen_client()
        
        # 构建消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT_JSON}]
        
        # 添加历史对话
        for msg in history:
            messages.append(msg)
        
        # 添加当前用户输入
        new_message = {"role": "user", "content": user_input}
        messages.append(new_message)
        
        start_time = time.time()
        
        # 调用千问模型
        completion = client.chat.completions.create(
            model=QWEN_BASE_CHAT_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=1000
        )
        
        raw_content = completion.choices[0].message.content
        logger.info(f'千问模型原始响应: {raw_content}')
        
        # 分类指令类型
        instruction_type = classify_instruction_type(user_input, raw_content)
        logger.info(f'指令类型: {instruction_type}')
        
        # 根据指令类型生成相应响应
        processed_content = generate_response_by_type(instruction_type, raw_content, user_input)
        logger.info(f'处理后的响应: {processed_content}')
        
        # 更新历史记录
        history.append(new_message)
        assistant_message = {"role": "assistant", "content": processed_content}
        history.append(assistant_message)
        
        end_time = time.time()
        logger.info(f'千问模型请求耗时: {end_time - start_time:.2f}秒')
        
        return processed_content, history
        
    except Exception as e:
        logger.error(f'千问模型调用失败: {e}')
        return None, history


def _enhance_multimodal_params(ai_response: str, multimodal_input: MultimodalInput) -> str:
    """
    增强多模态参数，自动填充 AI 无法推断的参数（如图片路径、用户文本等）
    
    Args:
        ai_response: AI 的原始响应
        multimodal_input: 多模态输入对象
        
    Returns:
        str: 增强后的响应
    """
    # 特效名称映射表（中文 -> template）
    TEMPLATE_EFFECTS = {
        "解压捏捏": "squish",
        "捏捏": "squish",
        "转圈圈": "rotation",
        "转圈": "rotation",
        "戳戳乐": "poke",
        "戳戳": "poke",
        "气球膨胀": "inflate",
        "膨胀": "inflate",
        "分子扩散": "dissolve",
        "扩散": "dissolve",
        "热浪融化": "melt",
        "融化": "melt",
        "冰淇淋星球": "icecream",
        "冰淇淋": "icecream"
    }
    
    try:
        # 移除可能的 "action:" 前缀
        has_prefix = ai_response.strip().startswith("action:")
        clean_response = ai_response.replace("action:", "").strip() if has_prefix else ai_response
        
        response_data = safe_json_loads(clean_response)
        operations = response_data.get("operations", {})
        
        if not operations or "operation" not in operations:
            return ai_response
        
        operation_name = operations.get("operation")
        params = operations.get("params", {})
        
        modified = False
        
        # 对于图生视频操作，自动填充参数
        if operation_name in ["make_video_by_first_frame", "make_video_by_first_and_last_frame", "make_video_by_first_frame_and_template"]:
            # 填充图片路径
            if multimodal_input.images and len(multimodal_input.images) > 0:
                if params.get("img_url") in [None, "Unknown", ""]:
                    params["img_url"] = multimodal_input.images[0].content
                    modified = True
                    logger.info(f'自动填充 img_url: {params["img_url"]}')
                
                # 如果需要第二张图片（首尾帧视频生成）
                if operation_name == "make_video_by_first_and_last_frame" and len(multimodal_input.images) > 1:
                    # 首帧
                    if params.get("first_img_url") in [None, "Unknown", ""]:
                        params["first_img_url"] = multimodal_input.images[0].content
                        modified = True
                        logger.info(f'自动填充 first_img_url: {params["first_img_url"]}')
                    # 尾帧
                    if params.get("last_img_url") in [None, "Unknown", ""]:
                        params["last_img_url"] = multimodal_input.images[1].content
                        modified = True
                        logger.info(f'自动填充 last_img_url: {params["last_img_url"]}')
            
            # 特殊处理：template 操作的参数填充
            if operation_name == "make_video_by_first_frame_and_template":
                # 检查用户文本中是否包含特效关键词
                user_text = multimodal_input.text
                detected_template = None
                
                for chinese_name, template_value in TEMPLATE_EFFECTS.items():
                    if chinese_name in user_text:
                        detected_template = template_value
                        logger.info(f'识别到特效: {chinese_name} -> {template_value}')
                        break
                
                # 填充 template 参数
                if params.get("template") in [None, "Unknown", ""]:
                    if detected_template:
                        params["template"] = detected_template
                        modified = True
                        logger.info(f'自动填充 template: {params["template"]}')
                    else:
                        # 如果没有识别到特效，尝试直接使用 AI 返回的值或用户输入
                        # 如果 AI 已经返回了 template，保持不变
                        pass
                
                # 确保使用正确的模型
                if params.get("model") in [None, "Unknown", ""]:
                    params["model"] = "wanx2.1-i2v-plus"
                    modified = True
                    logger.info(f'自动填充 model: {params["model"]}')
            else:
                # 其他图生视频操作：填充 prompt
                if params.get("prompt") in [None, "Unknown", ""]:
                    # 使用用户的文本输入作为提示词
                    prompt = multimodal_input.text
                    # 过滤掉一些通用的指令词
                    generic_phrases = ["让这张图片动起来", "让图片动起来", "生成视频", "制作视频", "动起来"]
                    for phrase in generic_phrases:
                        if phrase in prompt:
                            # 如果只是通用指令，使用默认提示
                            prompt = "自然流畅的动画效果"
                            break
                    params["prompt"] = prompt
                    modified = True
                    logger.info(f'自动填充 prompt: {params["prompt"]}')
        
        # 对于文生视频操作，自动填充文本提示
        elif operation_name == "make_video_by_text":
            if params.get("prompt") in [None, "Unknown", ""]:
                params["prompt"] = multimodal_input.text
                modified = True
                logger.info(f'自动填充 prompt: {params["prompt"]}')
        
        if modified:
            response_data["operations"]["params"] = params
            result = json.dumps(response_data, ensure_ascii=False)
            # 如果原响应有 "action:" 前缀，保留它
            return ("action:" + result) if has_prefix else result
        
        return ai_response
        
    except Exception as e:
        logger.warning(f"增强多模态参数失败: {e}")
        return ai_response


def ask_qwen_multimodal(
    multimodal_input: MultimodalInput, 
    history: List[Dict[str, str]]
) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    使用千问模型处理多模态输入（文本+图片+视频）
    
    Args:
        multimodal_input: 多模态输入对象
        history: 历史对话列表
        
    Returns:
        tuple: (API 响应内容, 更新后的历史对话)
    """
    try:
        client = init_qwen_client()
        processor = MultimodalProcessor()
        
        # 构建消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT_JSON}]
        
        # 添加历史对话
        for msg in history:
            messages.append(msg)
        
        # 将多模态输入转换为千问格式
        content = processor.convert_to_qwen_format(multimodal_input)
        
        # 添加当前用户输入
        new_message = {"role": "user", "content": content}
        messages.append(new_message)
        
        start_time = time.time()
        
        logger.info(f'发送多模态请求，模态类型: {multimodal_input.get_modal_type()}')
        
        # 调用千问模型
        completion = client.chat.completions.create(
            model=QWEN_BASE_CHAT_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=1000
        )
        
        raw_content = completion.choices[0].message.content
        logger.info(f'千问模型原始响应: {raw_content}')
        
        # 对于多模态输入，尝试自动填充参数（如图片路径、文本提示等）
        enhanced_content = _enhance_multimodal_params(raw_content, multimodal_input)
        if enhanced_content != raw_content:
            logger.info(f'多模态参数填充后: {enhanced_content}')
            raw_content = enhanced_content
        
        # 分类指令类型
        instruction_type = classify_instruction_type(multimodal_input.text, raw_content)
        logger.info(f'指令类型: {instruction_type}')
        
        # 根据指令类型生成相应响应
        processed_content = generate_response_by_type(instruction_type, raw_content, multimodal_input.text)
        logger.info(f'处理后的响应: {processed_content}')
        
        # 更新历史记录（历史中保存文本描述）
        history.append({
            "role": "user", 
            "content": f"[{multimodal_input.get_modal_type()}] {multimodal_input.text}"
        })
        assistant_message = {"role": "assistant", "content": processed_content}
        history.append(assistant_message)
        
        end_time = time.time()
        logger.info(f'千问模型请求耗时: {end_time - start_time:.2f}秒')
        
        return processed_content, history
        
    except Exception as e:
        logger.error(f'千问模型多模态调用失败: {e}')
        return None, history

## 取消顶层 process_instruction 包装：直接使用 ask_qwen 并在调用方维护 history

class DialogueManager:
    """对话管理器，用于处理用户交互和生成自然语言响应"""
    
    def __init__(self):
        self.history = []
        self.context = {
            "current_video": None,
            "last_operation": None,
            "total_operations": 0
        }
        self.multimodal_processor = MultimodalProcessor()
    
    def process_multimodal_input(
        self,
        text: str,
        image_paths: Optional[List[str]] = None,
        video_paths: Optional[List[str]] = None,
        audio_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        处理多模态用户输入
        
        Args:
            text: 文本指令
            image_paths: 图片路径列表
            video_paths: 视频路径列表
            audio_paths: 音频路径列表
            
        Returns:
            Dict: {
                "response": 处理结果的自然语言响应,
                "success": 是否成功执行,
                "action": 执行的操作指令,
                "modal_type": 模态类型
            }
        """
        try:
            # 处理多模态输入
            multimodal_input = self.multimodal_processor.process_input(
                text=text,
                image_paths=image_paths,
                video_paths=video_paths,
                audio_paths=audio_paths
            )
            
            # 如果只是纯文本，使用原有方法
            if multimodal_input.is_text_only():
                return self.process_user_input(text)
            
            # 处理多模态输入
            content, updated_history = ask_qwen_multimodal(multimodal_input, self.history)
            self.history = updated_history if isinstance(updated_history, list) else self.history
            
            if content is None:
                return {
                    "response": "无法理解您的多模态输入，请重试",
                    "success": False,
                    "action": None,
                    "modal_type": multimodal_input.get_modal_type()
                }
            
            # 检查是否是操作指令
            if content.startswith("action:"):
                return {
                    "response": "指令已解析，准备执行",
                    "success": True,
                    "action": content,
                    "modal_type": multimodal_input.get_modal_type()
                }
            else:
                return {
                    "response": content,
                    "success": True,
                    "action": None,
                    "modal_type": multimodal_input.get_modal_type()
                }
                
        except Exception as e:
            logger.error(f"处理多模态输入失败: {e}")
            return {
                "response": f"处理多模态输入时出错: {str(e)}",
                "success": False,
                "action": None,
                "modal_type": "unknown"
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
        content,  updated_history = ask_qwen(user_input, self.history)
        self.history = updated_history if isinstance(updated_history, list) else self.history
        
        if content is None:
            return {
                "response": "无法理解您的指令，请重试",
                "success": False,
                "action": None
            }
        
        # 检查是否是操作指令
        if content.startswith("action:"):
            return {
                "response":  "指令已解析，准备执行",
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
def test_instruction_classification():
    """
    测试指令分类功能
    """
    print("=== 测试指令分类功能 ===")
    
    # 测试用例：模拟AI响应
    test_cases = [
        {
            "user_input": "剪掉视频第一秒",
            "ai_response": '{"operations": {"operation": "trim", "params": {"start": 1.0, "end": None}, "editor": "ffmpeg"}}',
            "expected_type": 1,
            "description": "情况1：能匹配操作且能提取参数"
        },
        {
            "user_input": "视频速度太慢了，调快一点",
            "ai_response": '{"operations": {"operation": "adjust_speed", "params": {"factor": "Unknown"}, "editor": "ffmpeg"}}',
            "expected_type": 2,
            "description": "情况2：能匹配操作但不能提取参数"
        },
        {
            "user_input": "给视频添加魔法特效",
            "ai_response": '{"operations": {}}',
            "expected_type": 3,
            "description": "情况3：不能匹配操作"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"用户输入: {test_case['user_input']}")
        print(f"AI响应: {test_case['ai_response']}")
        
        # 测试分类功能
        instruction_type = classify_instruction_type(test_case['user_input'], test_case['ai_response'])
        print(f"分类结果: {instruction_type}")
        print(f"期望结果: {test_case['expected_type']}")
        
        # 测试响应生成功能
        processed_response = generate_response_by_type(instruction_type, test_case['ai_response'], test_case['user_input'])
        print(f"处理后响应: {processed_response}")
        
        # 验证结果
        if instruction_type == test_case['expected_type']:
            print("✅ 分类正确")
        else:
            print("❌ 分类错误")

def test_qwen_nlp():
    """
    测试千问模型 NLP 解析功能
    """
    print("=== 测试千问模型 NLP 解析功能 ===")
    
    test_instructions = [
        "把开头一秒剪掉",
        "片头加 1.5 秒淡入效果",
        "整体速度调到 1.5 倍",
        "打字幕 Hello 3 秒放左下",
        "声音小一半",
        "生成小猫在草地上快速奔跑的视频"
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        print(f"\n测试 {i}: {instruction}")
        try:
            global history
            content, history = ask_qwen(instruction, history)
            print(f"解析结果: {content}")

        except Exception as e:
            print(f"测试失败: {e}")

if __name__ == "__main__":
    # 先测试指令分类功能
    test_instruction_classification()
    
    # 然后测试完整的NLP解析功能
    test_qwen_nlp() 
