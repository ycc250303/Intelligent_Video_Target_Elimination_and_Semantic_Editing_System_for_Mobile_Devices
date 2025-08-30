import json
import numpy as np
import cv2
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StyleVector:
    """风格向量类，用于表示用户的剪辑风格偏好"""
    
    def __init__(self):
        # 语言节奏偏好 (0-1)
        self.language_rhythm = {
            'fast_paced': 0.5,      # 快节奏
            'slow_paced': 0.5,      # 慢节奏
            'dynamic': 0.5,         # 动态变化
            'consistent': 0.5       # 一致性
        }
        
        # 镜头节选逻辑偏好 (0-1)
        self.shot_selection = {
            'close_up_frequency': 0.5,    # 特写频率
            'wide_shot_frequency': 0.5,   # 远景频率
            'transition_smoothness': 0.5, # 转场平滑度
            'cut_frequency': 0.5          # 剪辑频率
        }
        
        # 内容结构偏好 (0-1)
        self.content_structure = {
            'narrative_style': 0.5,       # 叙事风格
            'emotional_intensity': 0.5,   # 情感强度
            'visual_complexity': 0.5,     # 视觉复杂度
            'audio_emphasis': 0.5         # 音频强调
        }
        
        # 技术参数偏好
        self.technical_params = {
            'brightness': 0.5,            # 亮度
            'contrast': 0.5,              # 对比度
            'saturation': 0.5,            # 饱和度
            'sharpness': 0.5              # 锐度
        }
        
        # 剪辑操作偏好权重
        self.operation_weights = {
            'trim': 1.0,
            'speed': 1.0,
            'add_transition': 1.0,
            'add_text': 1.0,
            'add_background_music': 1.0,
            'concatenate': 1.0,
            'color_correction': 1.0
        }
    
    def to_vector(self) -> np.ndarray:
        """将风格向量转换为numpy数组"""
        vector = []
        
        # 添加语言节奏向量
        vector.extend(self.language_rhythm.values())
        
        # 添加镜头节选向量
        vector.extend(self.shot_selection.values())
        
        # 添加内容结构向量
        vector.extend(self.content_structure.values())
        
        # 添加技术参数向量
        vector.extend(self.technical_params.values())
        
        # 添加操作权重向量
        vector.extend(self.operation_weights.values())
        
        return np.array(vector)
    
    def from_vector(self, vector: np.ndarray):
        """从numpy数组恢复风格向量"""
        if len(vector) != 28:  # 4+4+4+4+7 = 23个参数
            raise ValueError(f"向量维度不匹配，期望28，实际{len(vector)}")
        
        idx = 0
        
        # 恢复语言节奏
        for key in self.language_rhythm.keys():
            self.language_rhythm[key] = vector[idx]
            idx += 1
        
        # 恢复镜头节选
        for key in self.shot_selection.keys():
            self.shot_selection[key] = vector[idx]
            idx += 1
        
        # 恢复内容结构
        for key in self.content_structure.keys():
            self.content_structure[key] = vector[idx]
            idx += 1
        
        # 恢复技术参数
        for key in self.technical_params.keys():
            self.technical_params[key] = vector[idx]
            idx += 1
        
        # 恢复操作权重
        for key in self.operation_weights.keys():
            self.operation_weights[key] = vector[idx]
            idx += 1
    
    def update_from_feedback(self, feedback: Dict[str, Any], learning_rate: float = 0.1):
        """根据用户反馈更新风格向量"""
        for category, values in feedback.items():
            if category == 'language_rhythm' and hasattr(self, 'language_rhythm'):
                for key, value in values.items():
                    if key in self.language_rhythm:
                        self.language_rhythm[key] = np.clip(
                            self.language_rhythm[key] + learning_rate * (value - self.language_rhythm[key]), 0, 1
                        )
            
            elif category == 'shot_selection' and hasattr(self, 'shot_selection'):
                for key, value in values.items():
                    if key in self.shot_selection:
                        self.shot_selection[key] = np.clip(
                            self.shot_selection[key] + learning_rate * (value - self.shot_selection[key]), 0, 1
                        )
            
            elif category == 'content_structure' and hasattr(self, 'content_structure'):
                for key, value in values.items():
                    if key in self.content_structure:
                        self.content_structure[key] = np.clip(
                            self.content_structure[key] + learning_rate * (value - self.content_structure[key]), 0, 1
                        )
            
            elif category == 'technical_params' and hasattr(self, 'technical_params'):
                for key, value in values.items():
                    if key in self.technical_params:
                        self.technical_params[key] = np.clip(
                            self.technical_params[key] + learning_rate * (value - self.technical_params[key]), 0, 1
                        )

class ClipPersona:
    """剪辑人格类，包含用户的完整剪辑风格和偏好"""
    
    def __init__(self, user_id: str, persona_name: str):
        self.user_id = user_id
        self.persona_name = persona_name
        self.style_vector = StyleVector()
        self.creation_date = datetime.now()
        self.last_updated = datetime.now()
        
        # 历史剪辑记录
        self.editing_history = []
        
        # 偏好标签
        self.preference_tags = []
        
        # 训练数据
        self.training_data = {
            'videos_analyzed': [],
            'user_feedback': [],
            'generated_clips': []
        }
    
    def add_editing_record(self, video_path: str, operations: List[Dict], user_rating: float):
        """添加剪辑记录"""
        record = {
            'video_path': video_path,
            'operations': operations,
            'user_rating': user_rating,
            'timestamp': datetime.now().isoformat()
        }
        self.editing_history.append(record)
        self.last_updated = datetime.now()
    
    def add_preference_tag(self, tag: str, weight: float = 1.0):
        """添加偏好标签"""
        self.preference_tags.append({
            'tag': tag,
            'weight': weight,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_style_summary(self) -> Dict[str, Any]:
        """获取风格摘要"""
        return {
            'persona_name': self.persona_name,
            'dominant_style': self._get_dominant_style(),
            'preference_tags': [tag['tag'] for tag in self.preference_tags],
            'total_edits': len(self.editing_history),
            'average_rating': np.mean([record['user_rating'] for record in self.editing_history]) if self.editing_history else 0,
            'last_updated': self.last_updated.isoformat()
        }
    
    def _get_dominant_style(self) -> str:
        """获取主导风格"""
        # 分析风格向量的主导特征
        rhythm_avg = np.mean(list(self.style_vector.language_rhythm.values()))
        shot_avg = np.mean(list(self.style_vector.shot_selection.values()))
        content_avg = np.mean(list(self.style_vector.content_structure.values()))
        
        if rhythm_avg > 0.7:
            return "快节奏动态风格"
        elif shot_avg > 0.7:
            return "视觉导向风格"
        elif content_avg > 0.7:
            return "内容深度风格"
        else:
            return "平衡综合风格"

class ClipPersonaStudio:
    """ClipPersona Studio主系统"""
    
    def __init__(self):
        self.personas = {}  # 用户人格字典
        self.video_analyzer = VideoAnalyzer()
        self.style_learner = StyleLearner()
    
    def create_persona(self, user_id: str, persona_name: str) -> ClipPersona:
        """创建新的人格"""
        persona = ClipPersona(user_id, persona_name)
        self.personas[f"{user_id}_{persona_name}"] = persona
        return persona
    
    def get_persona(self, user_id: str, persona_name: str) -> Optional[ClipPersona]:
        """获取人格"""
        key = f"{user_id}_{persona_name}"
        if key not in self.personas:
            persona = ClipPersona(user_id, persona_name)
        return self.personas.get(key, persona)
    
    def analyze_video_preferences(self, persona: ClipPersona, video_path: str) -> Dict[str, Any]:
        """分析视频偏好"""
        logger.info(f"开始分析视频偏好: {video_path}")
        
        # 视频分析
        video_analysis = self.video_analyzer.analyze_video(video_path)
        
        # 风格学习
        style_insights = self.style_learner.learn_from_video(video_analysis)
        
        # 更新人格
        persona.training_data['videos_analyzed'].append({
            'video_path': video_path,
            'analysis': video_analysis,
            'style_insights': style_insights,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'video_analysis': video_analysis,
            'style_insights': style_insights,
            'recommended_tags': self._generate_recommended_tags(style_insights)
        }
    
    def process_user_feedback(self, persona: ClipPersona, feedback: Dict[str, Any]):
        """处理用户反馈"""
        logger.info(f"处理用户反馈: {feedback}")
        
        # 记录反馈
        persona.training_data['user_feedback'].append({
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        # 更新风格向量
        if 'style_preferences' in feedback:
            persona.style_vector.update_from_feedback(feedback['style_preferences'])
        
        # 添加偏好标签
        if 'tags' in feedback:
            for tag in feedback['tags']:
                persona.add_preference_tag(tag)
        
        # 保存更新
        # persona.save_persona() # This line is removed as per the edit hint
    
    def generate_editing_plan(self, persona: ClipPersona, user_instruction: str, video_path: str) -> Dict[str, Any]:
        """根据人格和用户指令生成剪辑方案"""
        logger.info(f"生成剪辑方案: {user_instruction}")
        
        # 分析用户指令
        instruction_analysis = self._analyze_instruction(user_instruction)
        
        # 结合人格风格生成方案
        editing_plan = self._create_editing_plan(persona, instruction_analysis, video_path)
        
        # 记录生成的方案
        persona.training_data['generated_clips'].append({
            'instruction': user_instruction,
            'plan': editing_plan,
            'timestamp': datetime.now().isoformat()
        })
        
        return editing_plan
    
    def _analyze_instruction(self, instruction: str) -> Dict[str, Any]:
        """分析用户指令"""
        # 这里可以集成更复杂的NLP分析
        analysis = {
            'intent': self._extract_intent(instruction),
            'target_elements': self._extract_target_elements(instruction),
            'style_preferences': self._extract_style_preferences(instruction),
            'technical_requirements': self._extract_technical_requirements(instruction)
        }
        return analysis
    
    def _extract_intent(self, instruction: str) -> str:
        """提取用户意图"""
        intent_keywords = {
            'trim': ['剪', '裁', '缩短', '删除'],
            'speed': ['加速', '减速', '快', '慢'],
            'transition': ['转场', '过渡', '切换'],
            'text': ['文字', '字幕', '标题'],
            'music': ['音乐', '背景音乐', '配乐'],
            'color': ['颜色', '调色', '滤镜'],
            'effect': ['特效', '效果', '动画']
        }
        
        for intent, keywords in intent_keywords.items():
            if any(keyword in instruction for keyword in keywords):
                return intent
        
        return 'general_editing'
    
    def _extract_target_elements(self, instruction: str) -> List[str]:
        """提取目标元素"""
        # 简单的关键词提取
        elements = []
        if '人' in instruction or '人物' in instruction:
            elements.append('person')
        if '物体' in instruction or '物品' in instruction:
            elements.append('object')
        if '背景' in instruction:
            elements.append('background')
        return elements
    
    def _extract_style_preferences(self, instruction: str) -> Dict[str, float]:
        """提取风格偏好"""
        preferences = {}
        
        if any(word in instruction for word in ['快', '快速', '动感']):
            preferences['fast_paced'] = 0.8
        if any(word in instruction for word in ['慢', '缓慢', '舒缓']):
            preferences['slow_paced'] = 0.8
        if any(word in instruction for word in ['特写', '近景']):
            preferences['close_up_frequency'] = 0.8
        if any(word in instruction for word in ['远景', '全景']):
            preferences['wide_shot_frequency'] = 0.8
        
        return preferences
    
    def _extract_technical_requirements(self, instruction: str) -> Dict[str, Any]:
        """提取技术要求"""
        requirements = {}
        
        if '高清' in instruction or '高质量' in instruction:
            requirements['quality'] = 'high'
        if '压缩' in instruction or '小文件' in instruction:
            requirements['quality'] = 'compressed'
        
        return requirements
    
    def _create_editing_plan(self, persona: ClipPersona, instruction_analysis: Dict, video_path: str) -> Dict[str, Any]:
        """创建剪辑方案"""
        plan = {
            'operations': [],
            'estimated_duration': 0,
            'style_notes': [],
            'confidence_score': 0.8
        }
        
        # 根据意图生成操作
        intent = instruction_analysis['intent']
        if intent == 'trim':
            plan['operations'].append({
                'type': 'trim',
                'params': {'start': 0.0, 'end': None},
                'description': '根据用户指令进行视频裁剪'
            })
        elif intent == 'speed':
            plan['operations'].append({
                'type': 'speed',
                'params': {'factor': 1.5},
                'description': '调整视频播放速度'
            })
        elif intent == 'transition':
            plan['operations'].append({
                'type': 'add_transition',
                'params': {'type': 'fade', 'duration': 1.0},
                'description': '添加转场效果'
            })
        
        # 应用人格风格
        self._apply_persona_style(plan, persona)
        
        return plan
    
    def _apply_persona_style(self, plan: Dict, persona: ClipPersona):
        """应用人格风格到剪辑方案"""
        style = persona.style_vector
        
        # 根据风格调整操作参数
        for operation in plan['operations']:
            if operation['type'] == 'speed':
                # 根据节奏偏好调整速度
                if style.language_rhythm['fast_paced'] > 0.7:
                    operation['params']['factor'] = max(operation['params']['factor'], 1.5)
                elif style.language_rhythm['slow_paced'] > 0.7:
                    operation['params']['factor'] = min(operation['params']['factor'], 0.8)
            
            elif operation['type'] == 'add_transition':
                # 根据转场偏好调整
                if style.shot_selection['transition_smoothness'] > 0.7:
                    operation['params']['duration'] = max(operation['params']['duration'], 1.5)
        
        # 添加风格说明
        plan['style_notes'].append(f"应用{persona.persona_name}的剪辑风格")
    
    def _generate_recommended_tags(self, style_insights: Dict) -> List[str]:
        """生成推荐标签"""
        tags = []
        
        if style_insights.get('rhythm_score', 0) > 0.7:
            tags.append('快节奏')
        elif style_insights.get('rhythm_score', 0) < 0.3:
            tags.append('慢节奏')
        
        if style_insights.get('visual_complexity', 0) > 0.7:
            tags.append('视觉复杂')
        elif style_insights.get('visual_complexity', 0) < 0.3:
            tags.append('简洁风格')
        
        return tags

class VideoAnalyzer:
    """视频分析器"""
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """分析视频特征"""
        cap = cv2.VideoCapture(video_path)
        
        analysis = {
            'basic_info': self._get_basic_info(cap),
            'rhythm_analysis': self._analyze_rhythm(cap),
            'visual_analysis': self._analyze_visual_features(cap),
            'content_analysis': self._analyze_content(cap)
        }
        
        cap.release()
        return analysis
    
    def _get_basic_info(self, cap) -> Dict[str, Any]:
        """获取基本信息"""
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        return {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration,
            'aspect_ratio': width / height if height > 0 else 0
        }
    
    def _analyze_rhythm(self, cap) -> Dict[str, float]:
        """分析节奏特征"""
        # 简化的节奏分析
        return {
            'rhythm_score': 0.5,
            'cut_frequency': 0.5,
            'motion_intensity': 0.5
        }
    
    def _analyze_visual_features(self, cap) -> Dict[str, float]:
        """分析视觉特征"""
        return {
            'brightness': 0.5,
            'contrast': 0.5,
            'saturation': 0.5,
            'visual_complexity': 0.5
        }
    
    def _analyze_content(self, cap) -> Dict[str, Any]:
        """分析内容特征"""
        return {
            'scene_changes': [],
            'dominant_colors': [],
            'texture_features': []
        }

class StyleLearner:
    """风格学习器"""
    
    def learn_from_video(self, video_analysis: Dict) -> Dict[str, float]:
        """从视频分析中学习风格"""
        insights = {}
        
        # 从节奏分析学习
        rhythm = video_analysis.get('rhythm_analysis', {})
        insights['rhythm_score'] = rhythm.get('rhythm_score', 0.5)
        insights['motion_preference'] = rhythm.get('motion_intensity', 0.5)
        
        # 从视觉分析学习
        visual = video_analysis.get('visual_analysis', {})
        insights['visual_complexity'] = visual.get('visual_complexity', 0.5)
        insights['color_preference'] = visual.get('saturation', 0.5)
        
        return insights
