"""
Persona数据模型
定义所有与Persona相关的数据结构和验证逻辑
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class PersonaCategory(Enum):
    """Persona分类枚举"""
    CREATIVE = "creative"  # 创意类
    PROFESSIONAL = "professional"  # 专业类
    ENTERTAINMENT = "entertainment"  # 娱乐类
    EDUCATIONAL = "educational"  # 教育类
    COMMERCIAL = "commercial"  # 商业类
    LIFESTYLE = "lifestyle"  # 生活类


class PersonaStatus(Enum):
    """Persona状态枚举"""
    ACTIVE = "active"
    DRAFT = "draft"
    ARCHIVED = "archived"


@dataclass
class StylePreferences:
    """风格偏好配置"""
    # 节奏偏好 (0-1)
    fast_paced: float = 0.5
    slow_paced: float = 0.5
    dynamic: float = 0.5
    consistent: float = 0.5
    
    # 镜头偏好 (0-1) 
    close_up_frequency: float = 0.5
    wide_shot_frequency: float = 0.5
    transition_smoothness: float = 0.5
    cut_frequency: float = 0.5
    
    # 内容偏好 (0-1)
    narrative_style: float = 0.5
    emotional_intensity: float = 0.5
    visual_complexity: float = 0.5
    audio_emphasis: float = 0.5
    
    # 技术参数偏好 (0-1)
    brightness: float = 0.5
    contrast: float = 0.5
    saturation: float = 0.5
    sharpness: float = 0.5


@dataclass
class PersonaMetadata:
    """Persona元数据"""
    id: str
    name: str
    description: str
    category: PersonaCategory
    tags: List[str]
    author: str
    status: PersonaStatus
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    is_featured: bool = False
    version: str = "1.0"


@dataclass
class PersonaStats:
    """Persona统计数据"""
    usage_count: int = 0
    download_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    share_count: int = 0
    view_count: int = 0


@dataclass
class EditingOperation:
    """剪辑操作记录"""
    operation_type: str
    parameters: Dict[str, Any]
    user_rating: Optional[float] = None
    timestamp: Optional[datetime] = None
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class UserFeedback:
    """用户反馈"""
    persona_id: str
    user_id: str
    rating: float  # 1-5星评分
    feedback_id: Optional[str] = None
    style_preferences: Optional[Dict[str, Any]] = None
    operation_feedback: Optional[Dict[str, float]] = None
    text_feedback: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.feedback_id is None:
            self.feedback_id = str(uuid.uuid4())


class PersonaModel:
    """完整的Persona模型"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: PersonaCategory,
        author: str,
        persona_id: Optional[str] = None
    ):
        # 基础信息
        self.metadata = PersonaMetadata(
            id=persona_id or str(uuid.uuid4()),
            name=name,
            description=description,
            category=category,
            tags=[],
            author=author,
            status=PersonaStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 风格偏好
        self.style_preferences = StylePreferences()
        
        # 统计数据
        self.stats = PersonaStats()
        
        # 历史记录
        self.editing_history: List[EditingOperation] = []
        self.feedback_history: List[UserFeedback] = []
        
        # 学习数据
        self.training_data = {
            'videos_analyzed': [],
            'successful_operations': [],
            'failed_operations': [],
            'user_corrections': []
        }
        
        # 自定义指令模板
        self.instruction_templates = {
            'trim': "根据{style}风格进行视频裁剪",
            'speed': "调整视频速度，体现{style}节奏感",
            'transition': "添加{style}风格的转场效果",
            'text': "添加符合{style}风格的文字效果",
            'music': "添加{style}风格的背景音乐",
            'color': "进行{style}风格的调色处理"
        }
    
    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
            self.metadata.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """移除标签"""
        if tag in self.metadata.tags:
            self.metadata.tags.remove(tag)
            self.metadata.updated_at = datetime.now()
    
    def update_style_preferences(self, preferences: Dict[str, float]):
        """更新风格偏好"""
        for key, value in preferences.items():
            if hasattr(self.style_preferences, key):
                setattr(self.style_preferences, key, max(0.0, min(1.0, value)))
        self.metadata.updated_at = datetime.now()
    
    def add_editing_operation(self, operation: EditingOperation):
        """添加剪辑操作记录"""
        self.editing_history.append(operation)
        self.stats.usage_count += 1
        
        # 根据操作结果更新风格偏好
        if operation.success and operation.user_rating is not None:
            self._update_preferences_from_operation(operation)
        
        self.metadata.updated_at = datetime.now()
    
    def add_feedback(self, feedback: UserFeedback):
        """添加用户反馈"""
        self.feedback_history.append(feedback)
        
        # 更新评分统计
        self.stats.rating_count += 1
        total_rating = self.stats.rating_average * (self.stats.rating_count - 1) + feedback.rating
        self.stats.rating_average = total_rating / self.stats.rating_count
        
        # 根据反馈更新风格偏好
        if feedback.style_preferences:
            self.update_style_preferences(feedback.style_preferences)
        
        self.metadata.updated_at = datetime.now()
    
    def get_dominant_style(self) -> str:
        """获取主导风格描述"""
        prefs = self.style_preferences
        
        # 节奏特征
        if prefs.fast_paced > 0.7:
            rhythm = "快节奏"
        elif prefs.slow_paced > 0.7:
            rhythm = "慢节奏"
        else:
            rhythm = "中等节奏"
        
        # 视觉特征
        if prefs.visual_complexity > 0.7:
            visual = "复杂视觉"
        elif prefs.visual_complexity < 0.3:
            visual = "简洁视觉"
        else:
            visual = "平衡视觉"
        
        # 情感特征
        if prefs.emotional_intensity > 0.7:
            emotion = "高情感强度"
        elif prefs.emotional_intensity < 0.3:
            emotion = "低情感强度"
        else:
            emotion = "中等情感"
        
        return f"{rhythm}·{visual}·{emotion}"
    
    def get_recommendation_score(self, operation_type: str) -> float:
        """获取操作推荐分数"""
        # 基于历史成功率和用户偏好计算推荐分数
        successful_ops = [op for op in self.editing_history 
                         if op.operation_type == operation_type and op.success]
        total_ops = [op for op in self.editing_history 
                    if op.operation_type == operation_type]
        
        if not total_ops:
            return 0.5  # 默认分数
        
        success_rate = len(successful_ops) / len(total_ops)
        avg_rating = sum(op.user_rating for op in successful_ops 
                        if op.user_rating) / len(successful_ops) if successful_ops else 0.5
        
        return (success_rate * 0.6 + (avg_rating / 5.0) * 0.4)
    
    def generate_instruction(self, operation_type: str, **kwargs) -> str:
        """生成个性化指令"""
        template = self.instruction_templates.get(operation_type, "执行{operation}操作")
        style_desc = self.get_dominant_style()
        
        return template.format(
            style=style_desc,
            operation=operation_type,
            **kwargs
        )
    
    def _update_preferences_from_operation(self, operation: EditingOperation):
        """根据操作结果更新偏好"""
        learning_rate = 0.05
        rating_factor = (operation.user_rating - 3.0) / 2.0  # 转换为-1到1的范围
        
        # 根据操作类型调整相关偏好
        if operation.operation_type == "speed":
            if "factor" in operation.parameters:
                factor = operation.parameters["factor"]
                if factor > 1.0:  # 加速
                    self.style_preferences.fast_paced += learning_rate * rating_factor
                else:  # 减速
                    self.style_preferences.slow_paced += learning_rate * rating_factor
        
        elif operation.operation_type == "add_transition":
            self.style_preferences.transition_smoothness += learning_rate * rating_factor
        
        # 确保值在[0,1]范围内
        for attr in ['fast_paced', 'slow_paced', 'transition_smoothness']:
            if hasattr(self.style_preferences, attr):
                value = getattr(self.style_preferences, attr)
                setattr(self.style_preferences, attr, max(0.0, min(1.0, value)))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'metadata': asdict(self.metadata),
            'style_preferences': asdict(self.style_preferences),
            'stats': asdict(self.stats),
            'editing_history': [asdict(op) for op in self.editing_history],
            'feedback_history': [asdict(fb) for fb in self.feedback_history],
            'training_data': self.training_data,
            'instruction_templates': self.instruction_templates,
            'dominant_style': self.get_dominant_style()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaModel':
        """从字典创建实例"""
        metadata = data['metadata']
        persona = cls(
            name=metadata['name'],
            description=metadata['description'],
            category=PersonaCategory(metadata['category']),
            author=metadata['author'],
            persona_id=metadata['id']
        )
        
        # 恢复元数据
        persona.metadata = PersonaMetadata(**metadata)
        
        # 恢复风格偏好
        persona.style_preferences = StylePreferences(**data['style_preferences'])
        
        # 恢复统计数据
        persona.stats = PersonaStats(**data['stats'])
        
        # 恢复历史记录
        persona.editing_history = [EditingOperation(**op) for op in data.get('editing_history', [])]
        persona.feedback_history = [UserFeedback(**fb) for fb in data.get('feedback_history', [])]
        
        # 恢复其他数据
        persona.training_data = data.get('training_data', {})
        persona.instruction_templates = data.get('instruction_templates', {})
        
        return persona
    
    def save_to_file(self, base_dir: str = "persona_models"):
        """保存到文件"""
        persona_dir = os.path.join(base_dir, f"{self.metadata.author}_{self.metadata.name}")
        os.makedirs(persona_dir, exist_ok=True)
        
        # 保存JSON数据
        with open(os.path.join(persona_dir, "persona.json"), 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        
        return persona_dir
    
    @classmethod
    def load_from_file(cls, persona_dir: str) -> 'PersonaModel':
        """从文件加载"""
        with open(os.path.join(persona_dir, "persona.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


# 预定义的默认Persona模板
DEFAULT_PERSONAS = {
    "creative_editor": PersonaModel(
        name="创意剪辑师",
        description="专注于创意表达和艺术性的剪辑风格",
        category=PersonaCategory.CREATIVE,
        author="system"
    ),
    "professional_editor": PersonaModel(
        name="专业剪辑师", 
        description="注重技术精度和专业标准的剪辑风格",
        category=PersonaCategory.PROFESSIONAL,
        author="system"
    ),
    "entertainment_editor": PersonaModel(
        name="娱乐剪辑师",
        description="轻松有趣、注重娱乐效果的剪辑风格", 
        category=PersonaCategory.ENTERTAINMENT,
        author="system"
    )
}

# 为默认Persona设置初始偏好
DEFAULT_PERSONAS["creative_editor"].style_preferences.visual_complexity = 0.8
DEFAULT_PERSONAS["creative_editor"].style_preferences.emotional_intensity = 0.9
DEFAULT_PERSONAS["creative_editor"].add_tag("创意")
DEFAULT_PERSONAS["creative_editor"].add_tag("艺术")

DEFAULT_PERSONAS["professional_editor"].style_preferences.consistent = 0.9
DEFAULT_PERSONAS["professional_editor"].style_preferences.transition_smoothness = 0.8
DEFAULT_PERSONAS["professional_editor"].add_tag("专业")
DEFAULT_PERSONAS["professional_editor"].add_tag("精确")

DEFAULT_PERSONAS["entertainment_editor"].style_preferences.fast_paced = 0.8
DEFAULT_PERSONAS["entertainment_editor"].style_preferences.dynamic = 0.9
DEFAULT_PERSONAS["entertainment_editor"].add_tag("娱乐")
DEFAULT_PERSONAS["entertainment_editor"].add_tag("有趣")
