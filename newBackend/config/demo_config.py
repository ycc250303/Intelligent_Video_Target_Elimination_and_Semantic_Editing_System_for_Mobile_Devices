"""
Demo模式配置
用于演示时直接返回预设的视频结果
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Demo视频目录
DEMO_VIDEO_DIR = PROJECT_ROOT / "newBackend" / "demo_videos"

# Demo风格卡配置
# 格式: {风格卡名称: (demo视频文件名, 描述)}
DEMO_STYLE_CARDS = {
    "旅行vlog": {
        "video": "6.mp4",
        "description": "已应用旅行vlog风格，视频已优化完成！",
    }
}

# Demo指令映射
# 格式: {指令关键词: (demo视频文件名, 描述, 函数调用)}
DEMO_INSTRUCTIONS = {
    "为视频开头风景添加一个横向撕开的撕纸特效，画面变化之后，特效消失": {
        "video": "1.mp4",
        "description": "已为视频开头风景添加横向撕纸特效，特效会随画面变化自动消失",
        "function_call": {
            "functionName": "add_paper_tear_transition",
            "parameters": {
                "effect_type": "horizontal_tear",
                "position": "start",
                "auto_dismiss": True
            }
        }
    },
    "为开头风景添加撕纸特效": {
        "video": "1.mp4",
        "description": "已为开头风景添加撕纸特效",
        "function_call": {
            "functionName": "add_transition_effect",
            "parameters": {
                "effect_type": "paper_tear",
                "position": "start",
                "duration": 1.0
            }
        }
    },
    "在画面中间添加字幕'天山牧歌'，使用可爱字体，同撕纸特效一起消失": {
        "video": "2.mp4",
        "description": "已在画面中间添加字幕'天山牧歌'，使用可爱字体，与撕纸特效同步消失",
        "function_call": {
            "functionName": "add_text_with_effect",
            "parameters": {
                "text": "天山牧歌",
                "position": "center",
                "font_style": "cute",
                "sync_with_transition": True
            }
        }
    },
    "给视频开头添加标题字幕，字体可爱一点": {
        "video": "2.mp4",
        "description": "已添加标题'天山牧歌'，使用可爱字体",
        "function_call": {
            "functionName": "add_text_overlay",
            "parameters": {
                "text": "天山牧歌",
                "position": "top",
                "font_style": "cute",
                "duration": 3.0
            }
        }
    },
    "给视频开头添加标题'天山牧歌'": {
        "video": "2.mp4",
        "description": "已添加标题'天山牧歌'，使用可爱字体",
        "function_call": {
            "functionName": "add_text_overlay",
            "parameters": {
                "text": "天山牧歌",
                "position": "top",
                "font_style": "cute",
                "duration": 3.0
            }
        }
    },
    "在画面的上方和下方添加几个旅游风的可爱贴纸，不要让他们相互重叠，同撕纸特效一起消失": {
        "video": "3.mp4",
        "description": "已在画面上下方添加旅游风格贴纸，贴纸不重叠，与撕纸特效同步消失",
        "function_call": {
            "functionName": "add_travel_stickers",
            "parameters": {
                "style": "travel_cute",
                "positions": ["top", "bottom"],
                "avoid_overlap": True,
                "sync_with_transition": True
            }
        }
    },
    "给视频开头添加贴纸动画": {
        "video": "3.mp4",
        "description": "已为视频开头添加贴纸动画",
        "function_call": {
            "functionName": "add_sticker_animation",
            "parameters": {
                "sticker_type": "decorative",
                "position": "top_right",
                "animation": "bounce",
                "duration": 2.0
            }
        }
    },
    "选取第二个画面的人像，单独抠出并加上白边，作为贴纸放到第一个画面中，与撕纸特效一起消失": {
        "video": "4.mp4",
        "description": "已从第二个画面抠出人像，添加白边后作为贴纸放置在第一个画面，与撕纸特效同步消失",
        "function_call": {
            "functionName": "extract_person_as_sticker",
            "parameters": {
                "source_frame": 2,
                "target_frame": 1,
                "border_color": "white",
                "border_width": 3,
                "sync_with_transition": True
            }
        }
    },
    "将第二个画面的人物抠出来添加于开头视频左下角，给人物描一个白边": {
        "video": "4.mp4",
        "description": "已抠出人物并添加到左下角，添加了白边效果",
        "function_call": {
            "functionName": "extract_and_overlay_person",
            "parameters": {
                "source_frame": 2,
                "target_position": "bottom_left",
                "border_color": "white",
                "border_width": 3
            }
        }
    },
    "将第二个画面的人物抠出来添加于开头视频左下角": {
        "video": "4.mp4",
        "description": "已抠出人物并添加到左下角，添加了白边效果",
        "function_call": {
            "functionName": "extract_and_overlay_person",
            "parameters": {
                "source_frame": 2,
                "target_position": "bottom_left",
                "border_color": "white",
                "border_width": 3
            }
        }
    },
    "为视频添加符合旅行风格的有节奏感的纯音乐": {
        "video": "5.mp4",
        "description": "已为视频添加旅行风格的有节奏感纯音乐",
        "function_call": {
            "functionName": "add_travel_music",
            "parameters": {
                "music_style": "travel_rhythmic",
                "is_instrumental": True,
                "match_video_style": True,
                "volume": 0.3
            }
        }
    },
    "结合视频风格和转场添加一个背景纯音乐": {
        "video": "5.mp4",
        "description": "已添加符合视频风格的背景音乐",
        "function_call": {
            "functionName": "add_background_music",
            "parameters": {
                "music_style": "instrumental",
                "match_video_style": True,
                "volume": 0.3
            }
        }
    }
}

# 模糊匹配的关键词（用于更宽松的匹配）
# 注意：当指令包含多个关键词时，会选择匹配关键词数量最多的视频
DEMO_KEYWORD_MAPPING = {
    # 1.mp4 关键词（撕纸特效）
    "横向撕开": "1.mp4",
    "撕纸特效": "1.mp4",
    "开头风景": "1.mp4",
    
    # 2.mp4 关键词（天山牧歌字幕）
    "天山牧歌": "2.mp4",
    "画面中间": "2.mp4",
    "字幕": "2.mp4",
    "可爱字体": "2.mp4",
    
    # 3.mp4 关键词（旅游贴纸）
    "旅游风": "3.mp4",
    "可爱贴纸": "3.mp4",
    "上方和下方": "3.mp4",
    "不要重叠": "3.mp4",
    
    # 4.mp4 关键词（人像抠图）
    "第二个画面": "4.mp4",
    "人像": "4.mp4",
    "单独抠出": "4.mp4",
    "白边": "4.mp4",
    "第一个画面": "4.mp4",
    
    # 5.mp4 关键词（旅行音乐）
    "旅行风格": "5.mp4",
    "节奏感": "5.mp4",
    "纯音乐": "5.mp4",
    "背景音乐": "5.mp4"
}


def get_demo_video_path(instruction: str) -> tuple:
    """
    检查指令是否匹配demo模式，返回对应的视频路径和函数调用信息
    
    Args:
        instruction: 用户输入的指令
        
    Returns:
        (video_path, description, function_call) 如果匹配demo指令，否则返回 (None, None, None)
    """
    # 精确匹配
    for demo_instruction, config in DEMO_INSTRUCTIONS.items():
        if demo_instruction in instruction or instruction in demo_instruction:
            video_path = DEMO_VIDEO_DIR / config["video"]
            if video_path.exists():
                return str(video_path), config["description"], config.get("function_call")
    
    # 改进的模糊匹配：找到匹配最多关键词的视频
    matched_videos = {}  # {video_file: 匹配的关键词数量}
    
    for keyword, video_file in DEMO_KEYWORD_MAPPING.items():
        if keyword in instruction:
            if video_file not in matched_videos:
                matched_videos[video_file] = 0
            matched_videos[video_file] += 1
    
    # 如果有匹配，选择匹配关键词数量最多的视频
    if matched_videos:
        # 按匹配数量降序排序，取第一个
        best_match = max(matched_videos.items(), key=lambda x: x[1])
        video_file = best_match[0]
        
        video_path = DEMO_VIDEO_DIR / video_file
        if video_path.exists():
            # 尝试找到对应的完整配置以获取function_call
            function_call = None
            for demo_instruction, config in DEMO_INSTRUCTIONS.items():
                if config["video"] == video_file:
                    function_call = config.get("function_call")
                    break
            return str(video_path), f"已完成您的视频编辑请求", function_call
    
    return None, None, None


def get_demo_style_card_video(style_card_name: str) -> tuple:
    """
    检查风格卡是否为Demo风格卡，返回对应的视频路径
    
    Args:
        style_card_name: 风格卡名称
        
    Returns:
        (video_path, description) 如果匹配demo风格卡，否则返回 (None, None)
    """
    if style_card_name in DEMO_STYLE_CARDS:
        config = DEMO_STYLE_CARDS[style_card_name]
        video_path = DEMO_VIDEO_DIR / config["video"]
        if video_path.exists():
            return str(video_path), config["description"]
    
    return None, None


def is_demo_mode_enabled() -> bool:
    """
    检查是否启用demo模式
    可以通过环境变量控制
    """
    return os.getenv("ENABLE_DEMO_MODE", "true").lower() == "true"




