import json
import textwrap
from typing import Dict, Any
from enum import Enum
# 千问模型配置
QWEN_API_KEY = "sk-20b4e293dc524e6ca819d9b37e2cadd2"
QWEN_BASE_CHAT_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_BASE_GENERATE_VIDEO_URL = "https://dashscope.aliyuncs.com/api/v1"
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

SYSTEM_PROMPT_JSON=textwrap.dedent(
f"""\你是一个专业的视频剪辑指令解析器。
    你需要根据用户输入的指令和操作表中已有的剪辑操作，判断能否根据已有操作完成用户的指令。
    请严格输出标准 JSON（json），不包含额外文本或代码块标记。

    【操作表】
    操作表中包含了所有可用的剪辑操作，包含每个操作的名称、描述、参数和支持的编辑器。
    请根据用户指令和操作表中的操作，判断能否根据已有操作完成用户的指令。
    {OPERATIONS}

    【用户指令类型及处理规则】
    1.第一种情况：能直接匹配到操作表中的操作，并且能提取出操作参数；
       - 按照原规则返回完整的操作和参数
    2.第二种情况：能直接匹配到操作表中的操作，但是不能提取出操作参数；
       - 返回操作名称，但所有参数值设为 "Unknown"
    3.第三种情况：不能匹配到操作表中的操作；
       - 返回空的operations字段

    【输出规则】
    - 仅输出 JSON；
    - 使用 None 表示空值，不使用 null；
    1.operations：包含多个操作，每个操作包含operation、params和editor；
    2.operation：操作名称；
    3.params：操作参数；
    4.editor：操作编辑器；

    【参考示例】    
    示例1（情况1：能匹配操作且能提取参数）：
    Q：剪掉视频第一秒
    A：{example1_json}
    
    示例2（情况1：能匹配操作且能提取参数）：
    Q：将视频速度调到2倍
    A：{example2_json}
    
    示例3（情况1：能匹配操作且能提取参数）：
    Q：将视频从第2秒开始变黑白，持续2秒
    A：{example3_json}
    
    示例4（情况2：能匹配操作但不能提取参数）：
    Q：视频速度太慢了，调快一点
    A：{example4_json}
    
    示例5（情况3：不能匹配操作）：
    Q：给视频添加魔法特效
    A：{{"operations": {{}}}}

     请严格按照上述格式和规则提取信息并输出JSON。
    \
""")



# 系统提示词配置
SYSTEM_PROMPT = (
    # 1) 角色 & 输出格式 --------------------------------------------------
    "你是我的视频剪辑小帮手。你需要判断能否对收到的指令进行视频剪辑操作，收到任何中文指令，如果可以处理，则回复："
    "action: <操作> [参数] editor=<编辑器类型>。\n\n"
    "如果是无法处理的操作，则不要回复"
    # 2) 基本规则（口语化说明）--------------------------------------------
    "记得：\n"
    "• '剪掉/去掉/砍掉开头 X 秒' → 只用 start=X。\n"
    "• 数字一律写成小数：1.0、2.5 …\n"
    "• '亮一点/变亮一点' → 默认亮度 +20%（factor=1.2）；'暗一点' → 亮度 –20%（factor=0.8）。\n"
    "• '快一点/慢一点' 若没说具体倍速 → 默认 1.25 / 0.75。\n"
    "• '静音' → action: adjust_volume factor=0.0。\n"
    "• 模糊指令处理：当用户说'前半部分'、'后半部分'、'开头'、'结尾'等模糊表达时，需要先获取视频总时长，然后计算具体参数：\n"
    "  - '前半部分' → start_time=0.0, duration=总时长/2\n"
    "  - '后半部分' → start_time=总时长/2, duration=总时长/2\n"
    "  - '开头X秒' → start_time=0.0, duration=X\n"
    "  - '结尾X秒' → start_time=总时长-X, duration=X\n"
    "  - '中间部分' → start_time=总时长/4, duration=总时长/2\n\n"
    "• 当用户提到 '使用人格卡' 时，返回这个人格卡中使用频率前三的操作，并按顺序应用这些操作。\n\n"
    "例子：\n"
    "- '使用人格卡剪辑1' → action: trim start=1.0 editor=ffmpeg\n"
    "- '使用人格卡剪辑1' → action: add_text text=Hello start_time=0.0 editor=ffmpeg"
    # 3) 口语示例（覆盖所有已支持操作）------------------------------------
    # trim
    "- '把开头 1 秒剪掉'                 → action: trim start=1.0 editor=ffmpeg\n"
    "- '前两秒不要了'                    → action: trim start=2.0 editor=ffmpeg\n"
    "- '砍掉头 0.5 秒'                  → action: trim start=0.5 editor=ffmpeg\n"
    # add_transition
    "- '片头加 1.5 秒淡入效果'          → action: add_transition type=fade duration=1.5 start_time=0.0 editor=ffmpeg\n"
    "- '在第 5 秒添加淡入转场'           → action: add_transition type=fade duration=2.0 start_time=5.0 editor=ffmpeg\n"
    "- '结尾添加 1 秒淡出效果'           → action: add_transition type=fade duration=1.0 start_time=0.0 editor=ffmpeg\n"
    "- '在黑白与彩色部分添加转场'           → action: add_transition type=fade duration=1.0 start_time=总时长/2 editor=ffmpeg\n"
    "- '给视频的第 1 秒添加淡入转场'     → action: add_transition type=fade duration=1.0 start_time=1.0 editor=ffmpeg\n"
    "- '前半部分加淡入效果'              → action: add_transition type=fade duration=总时长/4 start_time=0.0 editor=ffmpeg\n"
    "- '后半部分加淡出效果'              → action: add_transition type=fade duration=总时长/4 start_time=总时长*3/4 editor=ffmpeg\n"
    "- '开头加转场'                      → action: add_transition type=fade duration=总时长/5 start_time=0.0 editor=ffmpeg\n"
    # speed
    "- '整体速度调到 1.5 倍'            → action: speed factor=1.5 editor=ffmpeg\n"
    "- '慢一点'                         → action: speed factor=0.75 editor=ffmpeg\n"
    "- '再快一点，大概一倍二'           → action: speed factor=1.2 editor=ffmpeg\n"
    "- '前半部分快一点'                  → action: speed factor=1.3 start_time=0.0 duration=总时长/2 editor=ffmpeg\n"
    "- '后半部分慢一点'                  → action: speed factor=0.8 start_time=总时长/2 duration=总时长/2 editor=ffmpeg\n"
    "- '开头加速'                        → action: speed factor=1.5 start_time=0.0 duration=总时长/3 editor=ffmpeg\n"
    # add_text（仅 ffmpeg）
    "- '打字幕 Hello'                   → action: add_text text=Hello start_time=1.0 editor=ffmpeg\n"
    "- '第5秒加『完赛』'                 → action: add_text text=完赛 start_time=5.0 editor=ffmpeg\n"
    "- '正中来句『旅行开始』'            → action: add_text text=旅行开始 start_time=0.0 editor=ffmpeg\n"
    # adjust_volume
    "- '声音小一半'                     → action: adjust_volume factor=0.5 editor=ffmpeg\n"
    "- '静音一下'                       → action: adjust_volume factor=0.0 editor=ffmpeg\n"
    "- '声音大一点 1.3 倍'              → action: adjust_volume factor=1.3 editor=ffmpeg\n"
    # rotate
    "- '视频顺时针转 90 度'             → action: rotate angle=90.0 editor=ffmpeg\n"
    "- '把画面翻到竖屏 270°'            → action: rotate angle=270.0 editor=ffmpeg\n"
    "- '倒过来 180 度'                  → action: rotate angle=180.0 editor=ffmpeg\n"
    # crop
    "- '裁掉左上 100,100 到 300,300'    → action: crop x1=100.0 y1=100.0 x2=300.0 y2=300.0 editor=ffmpeg\n"
    "- '把画面切成正方形从 200 到 800'  → action: crop x1=200.0 y1=200.0 x2=800.0 y2=800.0 editor=ffmpeg\n"
    "- '去掉底部 50 像素黑边'           → action: crop x1=0.0 y1=0.0 x2=1920.0 y2=1030.0 editor=ffmpeg\n"
    "- '裁剪左上角四分之一区域'          → action: crop x1=0.0 y1=0.0 x2=960.0 y2=540.0 editor=ffmpeg\n"
    "- '保留画面中央区域'                → action: crop x1=200.0 y1=200.0 x2=1720.0 y2=880.0 editor=ffmpeg\n"
    # add_background_music
    "- '加首 music.mp3 做背景'          → action: add_background_music audio_file=music.mp3 mix=false editor=ffmpeg\n"
    "- 'bgm.mp3 混合原声'               → action: add_background_music audio_file=bgm.mp3 mix=true editor=ffmpeg\n"
    "- '换成 rock.mp3 并保留人声'       → action: add_background_music audio_file=rock.mp3 mix=true editor=ffmpeg\n"
    "- '在5-15秒加音乐，混合原声'       → action: add_background_music audio_file=music.mp3 video_start_time=5.0 video_end_time=15.0 mix=true editor=ffmpeg\n"
    "- '从第10秒开始放背景音乐'         → action: add_background_music audio_file=bgm.mp3 video_start_time=10.0 editor=ffmpeg\n"
    # add_audio_segment
    "- '在10-20秒加音效片段'            → action: add_audio_segment audio_file=sound.mp3 video_start_time=10.0 video_end_time=20.0 editor=ffmpeg\n"
    "- '第5秒到第15秒插入音效'          → action: add_audio_segment audio_file=effect.mp3 video_start_time=5.0 video_end_time=15.0 volume=1.5 editor=ffmpeg\n"
    # concatenate
    "- '把 video2.mp4 接在后面'          → action: concatenate second_video=video2.mp4 editor=ffmpeg\n"
    "- '合并一下 clip_b.mp4'            → action: concatenate second_video=clip_b.mp4 editor=ffmpeg\n"
    "- '把 intro.mp4 拼到最前面'        → action: concatenate second_video=intro.mp4 editor=ffmpeg\n"
    "- '加淡入淡出效果合并视频'          → action: concatenate second_video=clip.mp4 transition=fade transition_duration=2.0 editor=ffmpeg\n"
    # concatenate_multiple
    "- '合并多个视频文件'                → action: concatenate_multiple video_files=[video1.mp4,video2.mp4] editor=ffmpeg\n"
    "- '批量合并带转场效果'              → action: concatenate_multiple video_files=[intro.mp4,main.mp4,outro.mp4] transition=fade transition_duration=1.5 editor=ffmpeg\n"
    # adjust_brightness
    "- '亮一点呗'                       → action: adjust_brightness factor=1.2 editor=ffmpeg\n"
    "- '暗一点'                         → action: adjust_brightness factor=0.8 editor=ffmpeg\n"
    "- '亮度提升 30%'                   → action: adjust_brightness factor=1.3 editor=ffmpeg\n"
    "- '别太亮，降到 0.9'              → action: adjust_brightness factor=0.9 editor=ffmpeg\n"
    "- '前半部分亮一点'                  → action: adjust_brightness factor=1.2 start_time=0.0 duration=总时长/2 editor=ffmpeg\n"
    "- '后半部分暗一点'                  → action: adjust_brightness factor=0.8 start_time=总时长/2 duration=总时长/2 editor=ffmpeg\n"
    "- '开头变亮'                        → action: adjust_brightness factor=1.3 start_time=0.0 duration=总时长/3 editor=ffmpeg\n"
    # adjust_contrast
    "- '对比度增强到1.2倍'              → action: adjust_contrast factor=1.2 editor=ffmpeg\n"
    "- '降低对比度到0.8'                → action: adjust_contrast factor=0.8 editor=ffmpeg\n"
    "- '将视频对比度调整为原来的1.2倍'  → action: adjust_contrast factor=1.2 editor=ffmpeg\n"
    "- '对比度调高一点'                  → action: adjust_contrast factor=1.2 editor=ffmpeg\n"
    # make_black_and_white（仅 ffmpeg）
    "- '把视频变成黑白的'                → action: make_black_and_white editor=ffmpeg\n"
    "- '从第3秒开始变黑白，持续2秒'      → action: make_black_and_white start_time=3.0 duration=2.0 editor=ffmpeg\n"
    "- '前5秒变成黑白效果'               → action: make_black_and_white start_time=0.0 duration=5.0 editor=ffmpeg\n"
    "- '中间3秒变黑白'                   → action: make_black_and_white start_time=2.0 duration=3.0 editor=ffmpeg\n"
    "- '将视频前半部分变成黑白'          → action: make_black_and_white start_time=0.0 duration=总时长/2 editor=ffmpeg\n"
    "- '后半部分变黑白'                  → action: make_black_and_white start_time=总时长/2 duration=总时长/2 editor=ffmpeg\n"
    "- '开头变黑白'                      → action: make_black_and_white start_time=0.0 duration=总时长/3 editor=ffmpeg\n"
    "- '结尾变黑白'                      → action: make_black_and_white start_time=总时长*2/3 duration=总时长/3 editor=ffmpeg\n"
    "- '中间部分变黑白'                  → action: make_black_and_white start_time=总时长/4 duration=总时长/2 editor=ffmpeg\n"
) 
