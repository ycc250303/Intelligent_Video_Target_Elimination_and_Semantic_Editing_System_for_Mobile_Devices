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


# ==================== 参数推断配置 ====================
# 用于模糊语义匹配+视频理解的参数自动推断

# 参数推断提示词模板 - 针对不同操作类型定制分析提示
PARAM_INFERENCE_PROMPTS = {
    'adjust_speed': """
请分析这个视频的整体节奏和动作速度，并根据用户的指令给出建议的速度调整系数。

分析要点：
- 视频中人物/物体的移动速度
- 画面切换的频率
- 整体节奏感（是否拖沓或过快）

建议范围：
- 如果视频动作很慢/拖沓，建议加速系数：1.5-2.5倍
- 如果视频节奏正常但用户想加速，建议系数：1.2-1.5倍
- 如果视频已经很快但用户想减速，建议系数：0.5-0.8倍
- 如果视频正常但用户想略微减速，建议系数：0.8-0.95倍

用户的指令是：{user_input}

请直接以JSON格式返回参数，格式：{{"factor": 数值}}
""",
    
    'adjust_brightness': """
请分析这个视频的整体亮度水平，并根据用户的指令给出建议的亮度调整系数。

分析要点：
- 画面整体明暗程度
- 是否存在过暗或过亮的区域
- 视频拍摄环境的光照条件

建议范围：
- 如果视频明显偏暗，建议亮度系数：1.3-1.8倍
- 如果视频略暗，建议系数：1.1-1.3倍
- 如果视频过亮/过曝，建议系数：0.7-0.9倍
- 如果需要轻微调暗，建议系数：0.9-0.95倍

用户的指令是：{user_input}

请直接以JSON格式返回参数，格式：{{"factor": 数值}}
""",
    
    'adjust_contrast': """
请分析这个视频的对比度情况，并给出建议的对比度调整系数。

分析要点：
- 画面明暗对比是否明显
- 色彩层次是否丰富
- 是否存在灰蒙蒙的感觉

建议范围：
- 如果对比度太低（画面灰蒙），建议系数：1.2-1.5倍
- 如果对比度过高（黑白分明），建议系数：0.7-0.9倍

用户的指令是：{user_input}

请直接以JSON格式返回参数，格式：{{"factor": 数值}}
""",
    
    'adjust_volume': """
请分析这个视频的音频音量水平，并给出建议的音量调整系数。

分析要点：
- 整体音量大小
- 背景音乐和人声的平衡
- 是否存在音量过小或过大的问题

建议范围：
- 如果音量太小，建议系数：1.5-2.5倍
- 如果音量过大，建议系数：0.3-0.7倍
- 如果需要轻微调整，建议系数：0.8-1.2倍

用户的指令是：{user_input}

请直接以JSON格式返回参数，格式：{{"factor": 数值}}
""",
    
    'trim': """
请分析这个视频的内容分布，识别开头和结尾是否有需要裁剪的部分。

分析要点：
- 视频开头是否有静止画面、黑屏或无意义内容
- 视频结尾是否有多余的部分
- 主要内容从哪里开始，到哪里结束

用户的指令是：{user_input}

请根据分析结果，以JSON格式返回建议的裁剪参数：
- 如果需要剪掉开头：{{"start": 开始秒数, "end": null}}
- 如果需要保留中间部分：{{"start": 开始秒数, "end": 结束秒数}}
- 如果需要剪掉结尾：{{"start": 0, "end": 结束秒数}}
""",
    
    'rotate': """
请分析这个视频的画面方向，判断是否需要旋转以及旋转角度。

分析要点：
- 画面中的人物或物体方向
- 文字或标识的方向
- 是否存在横竖屏问题

用户的指令是：{user_input}

请以JSON格式返回旋转角度（90, 180, 270, -90等），格式：{{"angle": 角度值}}
""",
    
    'crop': """
请分析这个视频的画面构图，识别主要内容区域的位置。

分析要点：
- 画面中主要内容的位置
- 是否有多余的边缘或背景
- 画面比例和构图

用户的指令是：{user_input}

请以JSON格式返回裁剪区域坐标（相对于画面宽高的比例，0-1之间），格式：
{{"x1": 左上角X, "y1": 左上角Y, "x2": 右下角X, "y2": 右下角Y}}
"""
}

# 智能默认值映射 - 基于用户输入关键词的兜底策略
SMART_DEFAULTS = {
    'adjust_speed': {
        # 加速相关
        '快': 1.5, '加快': 1.5, '快一点': 1.5, '快点': 1.5,
        '加速': 1.8, '更快': 2.0, '快速': 2.0, '倍速': 2.0,
        '稍微快': 1.2, '略快': 1.2,
        
        # 减速相关
        '慢': 0.7, '减慢': 0.7, '慢一点': 0.7, '慢点': 0.7,
        '减速': 0.6, '更慢': 0.5, '慢动作': 0.5,
        '稍微慢': 0.85, '略慢': 0.85,
    },
    
    'adjust_brightness': {
        # 调亮相关
        '亮': 1.3, '调亮': 1.3, '亮一点': 1.3, '提亮': 1.3,
        '更亮': 1.5, '很亮': 1.6, '增加亮度': 1.4,
        '稍微亮': 1.15,
        
        # 调暗相关  
        '暗': 0.8, '调暗': 0.8, '暗一点': 0.8, '降低亮度': 0.8,
        '更暗': 0.6, '很暗': 0.5,
        '稍微暗': 0.9,
    },
    
    'adjust_contrast': {
        '增强对比度': 1.3, '提高对比度': 1.3, '对比度高': 1.3,
        '降低对比度': 0.8, '减弱对比度': 0.8, '对比度低': 0.8,
        '柔和': 0.85, '锐利': 1.4,
    },
    
    'adjust_volume': {
        # 增大音量
        '大': 1.8, '大声': 1.8, '大一点': 1.5, '声音大': 1.5,
        '更大': 2.0, '很大': 2.5, '增加音量': 1.6,
        
        # 减小音量
        '小': 0.6, '小声': 0.6, '小一点': 0.7, '声音小': 0.7,
        '更小': 0.5, '很小': 0.3, '降低音量': 0.6,
        '静音': 0.1,
    },
    
    'rotate': {
        '顺时针': 90, '逆时针': -90, '倒过来': 180,
        '转90度': 90, '转180度': 180, '转270度': 270,
        '横屏': 90, '竖屏': -90,
    }
}

# 参数合理范围限制 - 避免极端值
PARAM_RANGES = {
    'adjust_speed': {'factor': (0.1, 4.0)},
    'adjust_brightness': {'factor': (0.1, 3.0)},
    'adjust_contrast': {'factor': (0.1, 3.0)},
    'adjust_volume': {'factor': (0.0, 5.0)},
    'rotate': {'angle': (-360, 360)},
    'crop': {'x1': (0, 1), 'y1': (0, 1), 'x2': (0, 1), 'y2': (0, 1)},
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

