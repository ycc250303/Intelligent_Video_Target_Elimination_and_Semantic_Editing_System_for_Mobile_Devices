"""
配置模块
包含系统配置、操作定义、提示词等
"""

from .config import (
    QWEN_API_KEY,
    QWEN_BASE_CHAT_URL,
    QWEN_BASE_CHAT_MODEL,
    QWEN_BASE_GENERATE_VIDEO_URL,
    OPERATIONS,
    SYSTEM_PROMPT_JSON,
    InstructionType,
)

__all__ = [
    'QWEN_API_KEY',
    'QWEN_BASE_CHAT_URL',
    'QWEN_BASE_CHAT_MODEL',
    'QWEN_BASE_GENERATE_VIDEO_URL',
    'OPERATIONS',
    'SYSTEM_PROMPT_JSON',
    'InstructionType',
]


