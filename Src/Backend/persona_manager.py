"""
Persona管理器 - 统一管理所有Persona相关功能
包括内置预设、用户创建的Persona、人格卡等
"""
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from user_personality_card import UserPersonalityCard

class PersonaManager:
    """统一的Persona管理器"""
    
    def __init__(self):
        self.personas_dir = "personas"
        self.personality_cards_dir = "personality_cards"
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.personas_dir, self.personality_cards_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    # =================== 内置预设 ===================
    def get_builtin_presets(self) -> List[Dict[str, Any]]:
        """获取所有内置预设"""
        return [
            {
                "id": "builtin_rational_lecturer",
                "name": "理性讲师",
                "tag": "理性",
                "type": "builtin",
                "description": "严谨讲解，信息密度高，字幕清晰稳重。",
                "coverImage": "https://example.com/covers/rational.jpg",
                "downloads": 2847,
                "likes": 892,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "rational",
                    "subtitle": {
                        "fontFamily": "PingFang SC",
                        "fontSize": 28,
                        "color": "#FFFFFF",
                        "position": "bottom",
                        "animation": "none"
                    },
                    "cut": {
                        "pace": "medium",
                        "jumpCut": False,
                        "zoomPan": False
                    },
                    "transitions": "smooth",
                    "overlay": {
                        "captions": True,
                        "stickers": False,
                        "barrage": False
                    },
                    "bgm": {
                        "mood": "cinematic",
                        "volume": 0.2
                    }
                }
            },
            {
                "id": "builtin_humorous_barrage",
                "name": "搞笑弹幕",
                "tag": "搞笑",
                "type": "builtin",
                "description": "快节奏剪辑，弹幕式文案与适当贴纸。",
                "coverImage": "https://example.com/covers/funny.jpg",
                "downloads": 5691,
                "likes": 1542,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "humorous",
                    "subtitle": {
                        "fontFamily": "DIN Alternate",
                        "fontSize": 30,
                        "color": "#FFD700",
                        "position": "top",
                        "animation": "pop"
                    },
                    "cut": {
                        "pace": "fast",
                        "jumpCut": True,
                        "zoomPan": True
                    },
                    "transitions": "flashy",
                    "overlay": {
                        "captions": True,
                        "stickers": True,
                        "barrage": True
                    },
                    "bgm": {
                        "mood": "upbeat",
                        "volume": 0.5
                    }
                }
            },
            {
                "id": "builtin_romantic_lyrical",
                "name": "抒情浪漫",
                "tag": "浪漫",
                "type": "builtin",
                "description": "温柔的色调，慢节奏剪辑，适合情感表达。",
                "coverImage": "https://example.com/covers/romantic.jpg",
                "downloads": 3124,
                "likes": 756,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "romantic",
                    "subtitle": {
                        "fontFamily": "Noto Sans",
                        "fontSize": 26,
                        "color": "#FFB6C1",
                        "position": "bottom",
                        "animation": "gentle"
                    },
                    "cut": {
                        "pace": "slow",
                        "jumpCut": False,
                        "zoomPan": True
                    },
                    "transitions": "smooth",
                    "overlay": {
                        "captions": True,
                        "stickers": False,
                        "barrage": False
                    },
                    "bgm": {
                        "mood": "romantic",
                        "volume": 0.3
                    }
                }
            },
            {
                "id": "builtin_tech_review",
                "name": "科技测评",
                "tag": "科技",
                "type": "builtin",
                "description": "专业的科技产品评测风格，清晰简洁。",
                "coverImage": "https://example.com/covers/tech.jpg",
                "downloads": 4267,
                "likes": 1089,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "professional",
                    "subtitle": {
                        "fontFamily": "Helvetica",
                        "fontSize": 32,
                        "color": "#00D4FF",
                        "position": "bottom",
                        "animation": "slide"
                    },
                    "cut": {
                        "pace": "medium",
                        "jumpCut": True,
                        "zoomPan": True
                    },
                    "transitions": "tech",
                    "overlay": {
                        "captions": True,
                        "stickers": False,
                        "barrage": False
                    },
                    "bgm": {
                        "mood": "electronic",
                        "volume": 0.25
                    }
                }
            },
            {
                "id": "builtin_cinematic_drama",
                "name": "电影预告",
                "tag": "电影",
                "type": "builtin",
                "description": "电影级的视觉效果，戏剧性的转场和配乐。",
                "coverImage": "https://example.com/covers/cinematic.jpg",
                "downloads": 6892,
                "likes": 2156,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "dramatic",
                    "subtitle": {
                        "fontFamily": "Trajan Pro",
                        "fontSize": 34,
                        "color": "#FFFFFF",
                        "position": "center",
                        "animation": "cinematic"
                    },
                    "cut": {
                        "pace": "variable",
                        "jumpCut": True,
                        "zoomPan": True
                    },
                    "transitions": "cinematic",
                    "overlay": {
                        "captions": True,
                        "stickers": False,
                        "barrage": False
                    },
                    "bgm": {
                        "mood": "epic",
                        "volume": 0.6
                    }
                }
            },
            {
                "id": "builtin_vlog_lifestyle",
                "name": "游戏在线",
                "tag": "游戏",
                "type": "builtin",
                "description": "高能游戏剪辑，快速节奏，突出精彩时刻。",
                "coverImage": "https://example.com/covers/gaming.jpg",
                "downloads": 8756,
                "likes": 2834,
                "created_at": "2024-01-01T00:00:00Z",
                "stylePreset": {
                    "tone": "energetic",
                    "subtitle": {
                        "fontFamily": "Futura",
                        "fontSize": 36,
                        "color": "#FF6B35",
                        "position": "top",
                        "animation": "glitch"
                    },
                    "cut": {
                        "pace": "fast",
                        "jumpCut": True,
                        "zoomPan": True
                    },
                    "transitions": "gaming",
                    "overlay": {
                        "captions": True,
                        "stickers": True,
                        "barrage": True
                    },
                    "bgm": {
                        "mood": "gaming",
                        "volume": 0.7
                    }
                }
            }
        ]
    
    # =================== 用户Persona ===================
    def create_user_persona(self, name: str, description: str, tag: str, user_id: str = "default") -> Dict[str, Any]:
        """创建新的用户Persona"""
        persona_id = f"user_{uuid.uuid4().hex[:8]}"
        persona = {
            "id": persona_id,
            "name": name,
            "description": description,
            "tag": tag,
            "type": "user",
            "user_id": user_id,
            "downloads": 0,
            "likes": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "coverImage": f"https://example.com/user_covers/{persona_id}.jpg",
            "stylePreset": self._generate_default_style_preset(tag)
        }
        
        # 保存到文件
        file_path = os.path.join(self.personas_dir, f"{persona_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(persona, f, ensure_ascii=False, indent=2)
        
        return persona
    
    def get_user_personas(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """获取用户创建的所有Persona"""
        personas = []
        if not os.path.exists(self.personas_dir):
            return personas
            
        for filename in os.listdir(self.personas_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.personas_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        persona = json.load(f)
                        if persona.get('user_id') == user_id:
                            personas.append(persona)
                except Exception as e:
                    print(f"Error loading persona {filename}: {e}")
        
        return sorted(personas, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def update_user_persona(self, persona_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户Persona"""
        file_path = os.path.join(self.personas_dir, f"{persona_id}.json")
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                persona = json.load(f)
            
            persona.update(updates)
            persona['updated_at'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(persona, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating persona {persona_id}: {e}")
            return False
    
    def delete_user_persona(self, persona_id: str) -> bool:
        """删除用户Persona"""
        file_path = os.path.join(self.personas_dir, f"{persona_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error deleting persona {persona_id}: {e}")
                return False
        return False
    
    # =================== 人格卡集成 ===================
    def get_personality_card(self, card_name: str) -> Dict[str, Any]:
        """获取人格卡数据"""
        card = UserPersonalityCard(card_name)
        return {
            "name": card_name,
            "operations": card.operations,
            "most_frequent": card.get_most_frequent_operations()
        }
    
    def generate_persona_from_card(self, card_name: str, persona_name: str) -> Dict[str, Any]:
        """基于人格卡生成Persona"""
        card = UserPersonalityCard(card_name)
        frequent_ops = card.get_most_frequent_operations()
        
        # 基于常用操作生成风格预设
        style_preset = self._generate_style_from_operations(frequent_ops)
        
        persona = self.create_user_persona(
            name=persona_name,
            description=f"基于人格卡 {card_name} 自动生成的个性化剪辑风格",
            tag="个性化",
            user_id="default"
        )
        
        persona['stylePreset'] = style_preset
        persona['source'] = 'personality_card'
        persona['card_name'] = card_name
        
        # 更新保存
        self.update_user_persona(persona['id'], persona)
        
        return persona
    
    # =================== 综合查询 ===================
    def get_all_personas(self, user_id: str = "default") -> Dict[str, List[Dict[str, Any]]]:
        """获取所有Persona（内置+用户创建）"""
        return {
            "builtin": self.get_builtin_presets(),
            "user": self.get_user_personas(user_id)
        }
    
    def search_personas(self, query: str, user_id: str = "default") -> List[Dict[str, Any]]:
        """搜索Persona"""
        all_personas = self.get_all_personas(user_id)
        results = []
        
        query_lower = query.lower()
        
        for persona_list in all_personas.values():
            for persona in persona_list:
                if (query_lower in persona['name'].lower() or 
                    query_lower in persona['description'].lower() or 
                    query_lower in persona['tag'].lower()):
                    results.append(persona)
        
        return results
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取Persona"""
        # 先查找内置预设
        builtin = self.get_builtin_presets()
        for persona in builtin:
            if persona['id'] == persona_id:
                return persona
        
        # 再查找用户Persona
        file_path = os.path.join(self.personas_dir, f"{persona_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading persona {persona_id}: {e}")
        
        return None
    
    # =================== 辅助方法 ===================
    def _generate_default_style_preset(self, tag: str) -> Dict[str, Any]:
        """根据标签生成默认风格预设"""
        presets = {
            "搞笑": {
                "tone": "humorous",
                "subtitle": {"fontFamily": "DIN Alternate", "fontSize": 30, "color": "#FFD700"},
                "cut": {"pace": "fast", "jumpCut": True},
                "bgm": {"mood": "upbeat", "volume": 0.5}
            },
            "理性": {
                "tone": "rational",
                "subtitle": {"fontFamily": "PingFang SC", "fontSize": 28, "color": "#FFFFFF"},
                "cut": {"pace": "medium", "jumpCut": False},
                "bgm": {"mood": "cinematic", "volume": 0.2}
            },
            "浪漫": {
                "tone": "romantic",
                "subtitle": {"fontFamily": "Noto Sans", "fontSize": 26, "color": "#FFB6C1"},
                "cut": {"pace": "slow", "jumpCut": False},
                "bgm": {"mood": "romantic", "volume": 0.3}
            }
        }
        
        return presets.get(tag, presets["理性"])  # 默认使用理性风格
    
    def _generate_style_from_operations(self, operations: List[tuple]) -> Dict[str, Any]:
        """基于操作历史生成风格预设"""
        # 分析用户的剪辑习惯
        has_fast_cuts = any("speed" in op[0] and float(op[1]["params"].get("factor", 1)) > 1 for op in operations)
        has_text_overlay = any("add_text" in op[0] for op in operations)
        
        if has_fast_cuts:
            pace = "fast"
            tone = "energetic"
        else:
            pace = "medium"
            tone = "balanced"
        
        return {
            "tone": tone,
            "subtitle": {
                "fontFamily": "PingFang SC",
                "fontSize": 28,
                "color": "#FFFFFF",
                "position": "bottom"
            },
            "cut": {
                "pace": pace,
                "jumpCut": has_fast_cuts,
                "zoomPan": has_text_overlay
            },
            "bgm": {
                "mood": "adaptive",
                "volume": 0.3
            }
        }
