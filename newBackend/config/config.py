import json
import textwrap
from typing import Dict, Any
from enum import Enum
# 千问模型配置
QWEN_API_KEY = "sk-20b4e293dc524e6ca819d9b37e2cadd2"
QWEN_BASE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_BASE_GENERATE_MEDIA_URL = "https://dashscope.aliyuncs.com/api/v1"
QWEN_BASE_CHAT_MODEL = "qwen3-vl-plus"  # 可以改为 qwen-turbo, qwen-max 等

class InstructionType(Enum):
    MATCH_OPERATION_AND_PARAMS = 1
    MATCH_OPERATION_BUT_NO_PARAMS = 2
    NO_MATCH_OPERATION = 3

# 操作注册表
OPERATIONS: Dict[str, Dict[str, Any]] = {
    'trim': {
        'params': {
            'start': {'type': float, 'default': 0.0, 'required': True},
            'end': {'type': float, 'default': None, 'required': False}
        },
        'description': '裁剪视频，start=秒数，end=秒数（可选，默认为视频末尾）。例：剪掉前 1 秒 → action: trim start=1.0',
        'supported_editors': 'ffmpeg'
    },
    'add_transition': {
        'params': {
            'type': {'type': str, 'default': 'fade', 'required': True},
            'duration': {'type': float, 'default': 1.0, 'required': True},
            'start_time': {'type': float, 'default': 0.0, 'required': False}
        },
        'description': '添加转场效果，type=转场类型，duration=秒数，start_time=开始时间（秒）。',
        'supported_editors': 'ffmpeg'
    },
    'concatenate': {
        'params': {
            'second_video': {'type': str, 'default': '', 'required': True},
            'transition': {'type': str, 'default': 'none', 'required': False},
            'transition_duration': {'type': float, 'default': 1.0, 'required': False}
        },
        'description': '合并另一个视频，支持设置转场类型与持续时间。',
        'supported_editors': 'ffmpeg'
    },
    'concatenate_multiple': {
        'params': {
            # 注意：通过 action 字符串传递列表参数暂未通用实现，建议前端自行拆分或使用单步合并。
            'video_files': {'type': list, 'default': None, 'required': True},
            'transition': {'type': str, 'default': 'none', 'required': False},
            'transition_duration': {'type': float, 'default': 1.0, 'required': False}
        },
        'description': '合并多个视频文件，支持转场。',
        'supported_editors': 'ffmpeg'
    },
    'adjust_speed': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整视频速度，factor=倍数。',
        'supported_editors': 'ffmpeg'
    },
    'add_text': {
        'params': {
            'text': {'type': str, 'default': '', 'required': True},
            'start_time': {'type': float, 'default': None, 'required': True},
            'fontsize': {'type': int, 'default': 24, 'required': False},
            'duration': {'type': float, 'default': None, 'required': False}
        },
        'description': '添加字幕（固定底部居中）。start_time 必填；未给出 duration 时按文本长度自动计算。',
        'supported_editors': 'ffmpeg'
    },
    'adjust_volume': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整音量，factor=倍数。',
        'supported_editors': 'ffmpeg'
    },
    'rotate': {
        'params': {
            'angle': {'type': float, 'default': 90.0, 'required': True}
        },
        'description': '旋转视频，angle=角度。',
        'supported_editors': 'ffmpeg'
    },
    'crop': {
        'params': {
            'x1': {'type': float, 'default': 0.0, 'required': True},
            'y1': {'type': float, 'default': 0.0, 'required': True},
            'x2': {'type': float, 'default': None, 'required': True},
            'y2': {'type': float, 'default': None, 'required': True}
        },
        'description': '裁剪画面，x1,y1=左上角坐标，x2,y2=右下角坐标。',
        'supported_editors': 'ffmpeg'
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
        'supported_editors': 'ffmpeg'
    },
    'add_audio_segment': {
        'params': {
            'audio_file': {'type': str, 'default': '', 'required': True},
            'video_start_time': {'type': float, 'default': None, 'required': True},
            'video_end_time': {'type': float, 'default': None, 'required': True},
            'audio_start_time': {'type': float, 'default': 0.0, 'required': False},
            'audio_end_time': {'type': float, 'default': None, 'required': False},
            'volume': {'type': float, 'default': 1.0, 'required': False},
            'mix': {'type': bool, 'default': True, 'required': False},
            'overwrite': {'type': bool, 'default': False, 'required': False},
        },
        'description': '在指定时间段叠加一段音频，可控制音量与覆盖策略。',
        'supported_editors': 'ffmpeg'
    },
    'adjust_brightness': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整亮度，factor=倍数。',
        'supported_editors': 'ffmpeg'
    },
    'adjust_contrast': {
        'params': {
            'factor': {'type': float, 'default': 1.0, 'required': True}
        },
        'description': '调整对比度，factor=倍数。',
        'supported_editors': 'ffmpeg'
    },
    'make_black_and_white': {
        'params': {
            'start_time': {'type': float, 'default': 0.0, 'required': False},
            'duration': {'type': float, 'default': None, 'required': False}
        },
        'description': '将视频变为黑白效果。',
        'supported_editors': 'ffmpeg'
    },
    # ---------------- Qwen 视频生成相关操作（仅解析，不在此处调用API） ----------------
    'make_video_by_first_frame': {
        'params': {
            'img_url': {'type': str, 'default': '', 'required': True},
            'prompt': {'type': str, 'default': '', 'required': True},
            'model': {'type': str, 'default': 'wan2.2-i2v-flash', 'required': False},
            'resolution': {'type': str, 'default': '1080P', 'required': False}
        },
        'description': '通义千问：基于单张首帧图生成视频（I2V）。用于图片+文本描述的场景，当用户没有明确提到特效时使用此操作',
        'supported_editors': 'qwen'
    },
    'make_video_by_first_and_last_frame': {
        'params': {
            'first_img_url': {'type': str, 'default': '', 'required': True},
            'last_img_url': {'type': str, 'default': '', 'required': True},
            'prompt': {'type': str, 'default': '', 'required': True},
            'model': {'type': str, 'default': 'wanx2.2-kf2v-flash', 'required': False},
            'resolution': {'type': str, 'default': '720P', 'required': False}
        },
        'description': '通义千问：基于首尾两帧图生成视频（KF2V）。用于用户提供两张图片的场景，生成从第一张图到第二张图的过渡视频',
        'supported_editors': 'qwen'
    },
    'make_video_by_text': {
        'params': {
            'prompt': {'type': str, 'default': '', 'required': True},
            'model': {'type': str, 'default': 'wan2.2-t2v-plus', 'required': False},
            'size': {'type': str, 'default': '832*480', 'required': False}
        },
        'description': '通义千问：文本生成视频（T2V）',
        'supported_editors': 'qwen'
    },
    'make_video_by_first_frame_and_template': {
        'params': {
            'img_url': {'type': str, 'default': '', 'required': True},
            'template': {'type': str, 'default': '', 'required': True},
            'model': {'type': str, 'default': 'wanx2.1-i2v-plus', 'required': False},
            'resolution': {'type': str, 'default': '720P', 'required': False}
        },
        'description': '通义千问：图片+特效模板生成视频。支持的特效包括：解压捏捏(squish)、转圈圈(rotation)、戳戳乐(poke)、气球膨胀(inflate)、分子扩散(dissolve)、热浪融化(melt)、冰淇淋星球(icecream)。当用户明确提到这些特效时使用此操作，template参数填写括号中的英文值',
        'supported_editors': 'qwen'
    },
    'extend_video': {
        'params': {
            'prompt': {'type': str, 'default': '', 'required': True},
            'first_clip_url': {'type': str, 'default': '', 'required': True},
            'prompt_extend': {'type': bool, 'default': False, 'required': False}
        },
        'description': '通义千问：视频延展功能，将短视频延长到5秒。first_clip_url必须是公网可访问的HTTP/HTTPS URL（不支持本地文件路径）。视频要求：MP4格式，帧率≥16FPS，大小≤50MB，长度≤3秒。prompt描述期望的延展内容，prompt_extend为是否开启智能改写（默认False推荐）',
        'supported_editors': 'qwen'
    },
    'make_image_by_text': {
        'params': {
            'text': {'type': str, 'default': '', 'required': True},
            'model': {'type': str, 'default': 'qwen-image-plus', 'required': False},
            'size': {'type': str, 'default': '1328*1328', 'required': False},
            'watermark': {'type': bool, 'default': True, 'required': False},
            'prompt_extend': {'type': bool, 'default': True, 'required': False},
            'negative_prompt': {'type': str, 'default': '', 'required': False}
        },
        'description': '通义千问：文本生成图片（T2I）。text为生成图片的文本描述，size支持1024*1024、1328*1328等尺寸，watermark为是否添加水印，prompt_extend为是否智能改写提示词以获得更好效果',
        'supported_editors': 'qwen'
    }
}


example1_json=json.dumps({
    "operations":{
        "operation": "trim",
        "params": {
            "start": 1.0,
            "end": 2.0
        },
        "editor": "ffmpeg"
     
    }
})

print(InstructionType.MATCH_OPERATION_AND_PARAMS.value)

example2_json=json.dumps({
    "operations":{
        "operation": "adjust_speed",
        "params": {
           "factor": 2
        },
        "editor": "ffmpeg"
        
    }
})

example3_json=json.dumps({
    "operations":{
        "operation": "make_black_and_white",
        "params": {
           "start_time": 0,
           "duration":2
        },
        "editor": "ffmpeg"
    }
})

example4_json=json.dumps({
    "operations":{
        "operation": "adjust_speed",
        "params": {
           "factor": "Unknown"
        },
        "editor": "ffmpeg"
    }
})

# 文生视频示例
example5_json=json.dumps({
    "operations":{
        "operation": "make_video_by_text",
        "params": {
           "prompt": "一只小猫在草地上奔跑"
        },
        "editor": "qwen"
    }
})

# 文生图示例
example6_json=json.dumps({
    "operations":{
        "operation": "make_image_by_text",
        "params": {
           "text": "一朵玉兰花，背景为纯白色"
        },
        "editor": "qwen"
    }
})

# 图生视频示例
example7_json=json.dumps({
    "operations":{
        "operation": "make_video_by_first_frame",
        "params": {
           "img_url": "Unknown",
           "prompt": "花瓣随风飘落"
        },
        "editor": "qwen"
    }
})

SYSTEM_PROMPT_JSON=textwrap.dedent(
f"""\你是一个专业的视频剪辑和AI生成内容指令解析器。
    你需要根据用户输入的指令和操作表中已有的操作，判断能否根据已有操作完成用户的指令。
    请严格输出标准 JSON（json），不包含额外文本或代码块标记。

    【操作表】
    操作表中包含了所有可用的操作，包括：
    1. 视频剪辑操作（ffmpeg编辑器）：裁剪、调速、添加字幕、调整音量等
    2. AI生成操作（qwen编辑器）：文生视频、文生图、图生视频等
    
    请根据用户指令和操作表中的操作，判断能否根据已有操作完成用户的指令。
    {OPERATIONS}

    【用户指令类型及处理规则】
    1.第一种情况：能直接匹配到操作表中的操作，并且能提取出操作参数；
       - 按照原规则返回完整的操作和参数
    2.第二种情况：能直接匹配到操作表中的操作，但是不能提取出操作参数；
       - 返回操作名称，但所有参数值设为 "Unknown"
    3.第三种情况：不能匹配到操作表中的操作；
       - 返回空的operations字段

    【重要提示】
    - 对于"生成视频"、"创建视频"、"制作视频"等指令，如果只有文本描述没有图片，使用 make_video_by_text 操作
    - 对于"生成图片"、"创建图片"、"画一张图"等指令，使用 make_image_by_text 操作
    - 对于有图片输入的"生成视频"指令，使用 make_video_by_first_frame 操作
    - text 和 prompt 参数都是文本描述，根据操作定义选择正确的参数名
    - 如果用户指令中包含 [视频时长: X秒]，这是视频的总时长，可以用来计算相对时间
    - 当用户说"剪掉最后N秒"时，end参数 = 视频时长 - N
    - 当用户说"保留前N秒"时，end参数 = N
    - 当用户说"从倒数第N秒开始"时，start参数 = 视频时长 - N

    【输出规则】
    - 仅输出 JSON；
    - 使用 None 表示空值，不使用 null；
    1.operations：包含多个操作，每个操作包含operation、params和editor；
    2.operation：操作名称；
    3.params：操作参数；
    4.editor：操作编辑器（ffmpeg或qwen）；

    【参考示例】    
    示例1（视频剪辑：能匹配操作且能提取参数）：
    Q：剪掉视频第一秒
    A：{example1_json}
    
    示例2（视频剪辑：能匹配操作且能提取参数）：
    Q：将视频速度调到2倍
    A：{example2_json}
    
    示例3（视频剪辑：能匹配操作且能提取参数）：
    Q：将视频从第2秒开始变黑白，持续2秒
    A：{example3_json}
    
    示例4（能匹配操作但不能提取参数）：
    Q：视频速度太慢了，调快一点
    A：{example4_json}
    
    示例5（AI生成：文生视频）：
    Q：生成一个小猫在草地上奔跑的视频
    A：{example5_json}
    
    示例6（AI生成：文生图）：
    Q：帮我画一朵白色背景的玉兰花
    A：{example6_json}
    
    示例7（AI生成：图生视频，缺少图片参数）：
    Q：让这张图动起来，花瓣随风飘落
    A：{example7_json}
    
    示例8（不能匹配操作）：
    Q：给视频添加3D特效
    A：{{"operations": {{}}}}

     请严格按照上述格式和规则提取信息并输出JSON。
    \
""")

