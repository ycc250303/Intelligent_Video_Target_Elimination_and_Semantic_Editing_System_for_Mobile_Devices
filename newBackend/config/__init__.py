"""
配置模块
包含系统配置、操作定义、提示词等
"""

from .config import (
    QWEN_API_KEY,
    QWEN_BASE_CHAT_URL,
    QWEN_BASE_CHAT_MODEL,
    QWEN_BASE_GENERATE_MEDIA_URL,
    OPERATIONS,
    SYSTEM_PROMPT_JSON,
    InstructionType,
)

from .demo_config import (
    get_demo_video_path,
    is_demo_mode_enabled,
    DEMO_VIDEO_DIR,
    DEMO_INSTRUCTIONS,
)

__all__ = [
    'QWEN_API_KEY',
    'QWEN_BASE_CHAT_URL',
    'QWEN_BASE_CHAT_MODEL',
    'QWEN_BASE_GENERATE_MEDIA_URL',
    'OPERATIONS',
    'SYSTEM_PROMPT_JSON',
    'InstructionType',
    'get_demo_video_path',
    'is_demo_mode_enabled',
    'DEMO_VIDEO_DIR',
    'DEMO_INSTRUCTIONS',
]


