"""
Persona业务逻辑服务
处理所有与Persona相关的业务逻辑
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from models.persona_model import (
    PersonaModel, PersonaCategory, PersonaStatus, 
    UserFeedback, EditingOperation, DEFAULT_PERSONAS
)
from database.persona_db import PersonaDatabase
from clip_persona_studio import ClipPersonaStudio


logger = logging.getLogger(__name__)


class PersonaService:
    """Persona业务服务类"""
    
    def __init__(self, db_path: str = "Backend/persona_data.db"):
        self.db = PersonaDatabase(db_path)
        self.clip_studio = ClipPersonaStudio()
        self.init_default_personas()
    
    def init_default_personas(self):
        """初始化默认Persona"""
        try:
            for persona_key, persona in DEFAULT_PERSONAS.items():
                # 检查是否已存在
                existing = self.db.get_persona(persona.metadata.id)
                if not existing:
                    persona.metadata.status = PersonaStatus.ACTIVE
                    persona.metadata.is_public = True
                    persona.metadata.is_featured = True
                    self.db.create_persona(persona)
                    logger.info(f"初始化默认Persona: {persona.metadata.name}")
        except Exception as e:
            logger.error(f"初始化默认Persona失败: {e}")
    
    def create_persona(self, 
                      name: str, 
                      description: str, 
                      category: str,
                      author: str,
                      tags: List[str] = None,
                      style_preferences: Dict[str, float] = None,
                      is_public: bool = False) -> Tuple[bool, str, Optional[Dict]]:
        """创建新的Persona"""
        try:
            # 验证输入
            if not name or not description or not author:
                return False, "名称、描述和作者为必填项", None
            
            try:
                category_enum = PersonaCategory(category)
            except ValueError:
                return False, f"无效的分类: {category}", None
            
            # 创建Persona模型
            persona = PersonaModel(
                name=name,
                description=description,
                category=category_enum,
                author=author
            )
            
            # 设置标签
            if tags:
                for tag in tags:
                    persona.add_tag(tag)
            
            # 设置风格偏好
            if style_preferences:
                persona.update_style_preferences(style_preferences)
            
            # 设置公开状态
            persona.metadata.is_public = is_public
            persona.metadata.status = PersonaStatus.ACTIVE
            
            # 保存到数据库
            if self.db.create_persona(persona):
                logger.info(f"成功创建Persona: {name} by {author}")
                return True, "Persona创建成功", {
                    'id': persona.metadata.id,
                    'name': persona.metadata.name,
                    'description': persona.metadata.description,
                    'category': persona.metadata.category.value,
                    'author': persona.metadata.author,
                    'tags': persona.metadata.tags,
                    'created_at': persona.metadata.created_at.isoformat()
                }
            else:
                return False, "数据库保存失败", None
                
        except Exception as e:
            logger.error(f"创建Persona失败: {e}")
            return False, f"创建失败: {str(e)}", None
    
    def get_persona(self, persona_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """获取Persona详情"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在", None
            
            # 增加查看次数
            persona.stats.view_count += 1
            self.db.update_persona(persona)
            
            return True, "获取成功", persona.to_dict()
            
        except Exception as e:
            logger.error(f"获取Persona失败: {e}")
            return False, f"获取失败: {str(e)}", None
    
    def update_persona(self, 
                      persona_id: str,
                      author: str,
                      name: str = None,
                      description: str = None,
                      category: str = None,
                      tags: List[str] = None,
                      style_preferences: Dict[str, float] = None,
                      is_public: bool = None) -> Tuple[bool, str, Optional[Dict]]:
        """更新Persona"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在", None
            
            # 验证权限（只有创建者可以修改）
            if persona.metadata.author != author:
                return False, "无权限修改此Persona", None
            
            # 更新字段
            if name:
                persona.metadata.name = name
            if description:
                persona.metadata.description = description
            if category:
                try:
                    persona.metadata.category = PersonaCategory(category)
                except ValueError:
                    return False, f"无效的分类: {category}", None
            
            if tags is not None:
                persona.metadata.tags = tags
            
            if style_preferences:
                persona.update_style_preferences(style_preferences)
            
            if is_public is not None:
                persona.metadata.is_public = is_public
            
            # 保存更新
            if self.db.update_persona(persona):
                logger.info(f"成功更新Persona: {persona_id}")
                return True, "更新成功", persona.to_dict()
            else:
                return False, "数据库更新失败", None
                
        except Exception as e:
            logger.error(f"更新Persona失败: {e}")
            return False, f"更新失败: {str(e)}", None
    
    def delete_persona(self, persona_id: str, author: str) -> Tuple[bool, str]:
        """删除Persona"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在"
            
            # 验证权限
            if persona.metadata.author != author:
                return False, "无权限删除此Persona"
            
            # 系统默认Persona不能删除
            if persona.metadata.author == "system":
                return False, "系统默认Persona不能删除"
            
            if self.db.delete_persona(persona_id):
                logger.info(f"成功删除Persona: {persona_id}")
                return True, "删除成功"
            else:
                return False, "数据库删除失败"
                
        except Exception as e:
            logger.error(f"删除Persona失败: {e}")
            return False, f"删除失败: {str(e)}"
    
    def list_personas(self,
                     author: str = None,
                     category: str = None,
                     status: str = None,
                     is_public: bool = None,
                     is_featured: bool = None,
                     limit: int = 50,
                     offset: int = 0) -> Tuple[bool, str, List[Dict]]:
        """列出Persona"""
        try:
            # 转换枚举参数
            category_enum = None
            if category:
                try:
                    category_enum = PersonaCategory(category)
                except ValueError:
                    return False, f"无效的分类: {category}", []
            
            status_enum = None
            if status:
                try:
                    status_enum = PersonaStatus(status)
                except ValueError:
                    return False, f"无效的状态: {status}", []
            
            personas = self.db.list_personas(
                author=author,
                category=category_enum,
                status=status_enum,
                is_public=is_public,
                is_featured=is_featured,
                limit=limit,
                offset=offset
            )
            
            return True, "获取成功", personas
            
        except Exception as e:
            logger.error(f"列出Persona失败: {e}")
            return False, f"获取失败: {str(e)}", []
    
    def get_featured_personas(self, limit: int = 10) -> Tuple[bool, str, List[Dict]]:
        """获取推荐Persona"""
        try:
            personas = self.db.get_featured_personas(limit)
            return True, "获取成功", personas
        except Exception as e:
            logger.error(f"获取推荐Persona失败: {e}")
            return False, f"获取失败: {str(e)}", []
    
    def get_popular_personas(self, limit: int = 10) -> Tuple[bool, str, List[Dict]]:
        """获取热门Persona"""
        try:
            personas = self.db.get_popular_personas(limit)
            return True, "获取成功", personas
        except Exception as e:
            logger.error(f"获取热门Persona失败: {e}")
            return False, f"获取失败: {str(e)}", []
    
    def search_personas(self, query: str, limit: int = 20) -> Tuple[bool, str, List[Dict]]:
        """搜索Persona"""
        try:
            if not query.strip():
                return False, "搜索关键词不能为空", []
            
            personas = self.db.search_personas(query, limit)
            return True, "搜索成功", personas
        except Exception as e:
            logger.error(f"搜索Persona失败: {e}")
            return False, f"搜索失败: {str(e)}", []
    
    def analyze_video_preferences(self, 
                                 persona_id: str, 
                                 video_path: str) -> Tuple[bool, str, Optional[Dict]]:
        """分析视频偏好"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在", None
            
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                return False, "视频文件不存在", None
            
            # 使用ClipPersona Studio分析
            clip_persona = self.clip_studio.get_persona(persona.metadata.author, persona.metadata.name)
            if not clip_persona:
                # 如果不存在，创建一个
                clip_persona = self.clip_studio.create_persona(persona.metadata.author, persona.metadata.name)
            
            # 分析视频
            analysis_result = self.clip_studio.analyze_video_preferences(clip_persona, video_path)
            
            # 更新Persona的训练数据
            persona.training_data['videos_analyzed'].append({
                'video_path': video_path,
                'analysis': analysis_result,
                'timestamp': datetime.now().isoformat()
            })
            
            # 保存更新
            self.db.update_persona(persona)
            
            logger.info(f"完成视频偏好分析: {persona_id}")
            return True, "分析完成", analysis_result
            
        except Exception as e:
            logger.error(f"视频偏好分析失败: {e}")
            return False, f"分析失败: {str(e)}", None
    
    def process_user_feedback(self,
                             persona_id: str,
                             user_id: str,
                             rating: float,
                             style_preferences: Dict[str, Any] = None,
                             operation_feedback: Dict[str, float] = None,
                             text_feedback: str = None) -> Tuple[bool, str]:
        """处理用户反馈"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在"
            
            # 验证评分范围
            if not (1.0 <= rating <= 5.0):
                return False, "评分必须在1-5之间"
            
            # 创建反馈对象
            feedback = UserFeedback(
                feedback_id=None,  # 将自动生成
                persona_id=persona_id,
                user_id=user_id,
                rating=rating,
                style_preferences=style_preferences,
                operation_feedback=operation_feedback,
                text_feedback=text_feedback
            )
            
            # 保存反馈到数据库
            if self.db.add_user_feedback(feedback):
                # 使用ClipPersona Studio处理反馈
                clip_persona = self.clip_studio.get_persona(persona.metadata.author, persona.metadata.name)
                if clip_persona:
                    feedback_data = {
                        'style_preferences': style_preferences,
                        'operation_feedback': operation_feedback,
                        'rating': rating
                    }
                    self.clip_studio.process_user_feedback(clip_persona, feedback_data)
                
                logger.info(f"成功处理用户反馈: {persona_id} from {user_id}")
                return True, "反馈处理成功"
            else:
                return False, "反馈保存失败"
                
        except Exception as e:
            logger.error(f"处理用户反馈失败: {e}")
            return False, f"处理失败: {str(e)}"
    
    def generate_editing_plan(self,
                             persona_id: str,
                             user_instruction: str,
                             video_path: str,
                             user_id: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """生成剪辑方案"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在", None
            
            if not user_instruction.strip():
                return False, "用户指令不能为空", None
            
            # 检查视频文件
            if not os.path.exists(video_path):
                return False, "视频文件不存在", None
            
            # 使用ClipPersona Studio生成方案
            clip_persona = self.clip_studio.get_persona(persona.metadata.author, persona.metadata.name)
            if not clip_persona:
                clip_persona = self.clip_studio.create_persona(persona.metadata.author, persona.metadata.name)
                # 同步风格偏好
                self._sync_style_preferences(persona, clip_persona)
            
            # 生成剪辑方案
            editing_plan = self.clip_studio.generate_editing_plan(
                clip_persona, 
                user_instruction, 
                video_path
            )
            
            # 记录生成的方案
            persona.training_data.setdefault('generated_clips', []).append({
                'instruction': user_instruction,
                'plan': editing_plan,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # 更新使用统计
            persona.stats.usage_count += 1
            self.db.update_persona(persona)
            
            logger.info(f"生成剪辑方案: {persona_id} for instruction: {user_instruction[:50]}")
            return True, "方案生成成功", editing_plan
            
        except Exception as e:
            logger.error(f"生成剪辑方案失败: {e}")
            return False, f"生成失败: {str(e)}", None
    
    def record_editing_operation(self,
                                persona_id: str,
                                operation_type: str,
                                parameters: Dict[str, Any],
                                success: bool = True,
                                execution_time: float = None,
                                error_message: str = None,
                                user_rating: float = None) -> Tuple[bool, str]:
        """记录剪辑操作"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在"
            
            # 创建操作记录
            operation = EditingOperation(
                operation_type=operation_type,
                parameters=parameters,
                user_rating=user_rating,
                execution_time=execution_time,
                success=success,
                error_message=error_message
            )
            
            # 保存到数据库
            if self.db.add_editing_operation(persona_id, operation):
                logger.info(f"记录剪辑操作: {persona_id} - {operation_type}")
                return True, "操作记录成功"
            else:
                return False, "操作记录失败"
                
        except Exception as e:
            logger.error(f"记录剪辑操作失败: {e}")
            return False, f"记录失败: {str(e)}"
    
    def get_persona_recommendations(self, 
                                   user_id: str,
                                   user_preferences: Dict[str, Any] = None,
                                   limit: int = 5) -> Tuple[bool, str, List[Dict]]:
        """获取个性化Persona推荐"""
        try:
            # 简单的推荐算法：基于热门度和评分
            popular_personas = self.db.get_popular_personas(limit * 2)
            
            # 如果有用户偏好，可以进一步过滤和排序
            if user_preferences:
                # 这里可以实现更复杂的推荐算法
                # 比如基于用户的历史使用记录、偏好标签等
                pass
            
            # 返回前N个
            recommendations = popular_personas[:limit]
            
            return True, "推荐获取成功", recommendations
            
        except Exception as e:
            logger.error(f"获取Persona推荐失败: {e}")
            return False, f"推荐失败: {str(e)}", []
    
    def get_user_personas(self, author: str, limit: int = 50) -> Tuple[bool, str, List[Dict]]:
        """获取用户创建的Persona"""
        try:
            personas = self.db.list_personas(
                author=author,
                limit=limit
            )
            return True, "获取成功", personas
        except Exception as e:
            logger.error(f"获取用户Persona失败: {e}")
            return False, f"获取失败: {str(e)}", []
    
    def get_persona_statistics(self, persona_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """获取Persona统计信息"""
        try:
            persona = self.db.get_persona(persona_id)
            if not persona:
                return False, "Persona不存在", None
            
            # 计算统计信息
            stats = {
                'basic_stats': {
                    'usage_count': persona.stats.usage_count,
                    'download_count': persona.stats.download_count,
                    'rating_average': persona.stats.rating_average,
                    'rating_count': persona.stats.rating_count,
                    'share_count': persona.stats.share_count,
                    'view_count': persona.stats.view_count
                },
                'editing_stats': {
                    'total_operations': len(persona.editing_history),
                    'successful_operations': len([op for op in persona.editing_history if op.success]),
                    'average_rating': sum(op.user_rating for op in persona.editing_history 
                                        if op.user_rating) / len([op for op in persona.editing_history if op.user_rating]) 
                                       if [op for op in persona.editing_history if op.user_rating] else 0,
                    'operation_types': {}
                },
                'feedback_stats': {
                    'total_feedback': len(persona.feedback_history),
                    'average_feedback_rating': sum(fb.rating for fb in persona.feedback_history) / len(persona.feedback_history) 
                                              if persona.feedback_history else 0
                },
                'dominant_style': persona.get_dominant_style(),
                'recommendation_scores': {}
            }
            
            # 统计操作类型
            for operation in persona.editing_history:
                op_type = operation.operation_type
                if op_type not in stats['editing_stats']['operation_types']:
                    stats['editing_stats']['operation_types'][op_type] = 0
                stats['editing_stats']['operation_types'][op_type] += 1
            
            # 计算各种操作的推荐分数
            operation_types = ['trim', 'speed', 'transition', 'text', 'music', 'color']
            for op_type in operation_types:
                stats['recommendation_scores'][op_type] = persona.get_recommendation_score(op_type)
            
            return True, "统计获取成功", stats
            
        except Exception as e:
            logger.error(f"获取Persona统计失败: {e}")
            return False, f"统计获取失败: {str(e)}", None
    
    def _sync_style_preferences(self, persona_model: PersonaModel, clip_persona):
        """同步风格偏好到ClipPersona Studio"""
        try:
            # 将PersonaModel的风格偏好同步到ClipPersona的风格向量
            prefs = persona_model.style_preferences
            
            # 更新语言节奏
            clip_persona.style_vector.language_rhythm['fast_paced'] = prefs.fast_paced
            clip_persona.style_vector.language_rhythm['slow_paced'] = prefs.slow_paced
            clip_persona.style_vector.language_rhythm['dynamic'] = prefs.dynamic
            clip_persona.style_vector.language_rhythm['consistent'] = prefs.consistent
            
            # 更新镜头选择
            clip_persona.style_vector.shot_selection['close_up_frequency'] = prefs.close_up_frequency
            clip_persona.style_vector.shot_selection['wide_shot_frequency'] = prefs.wide_shot_frequency
            clip_persona.style_vector.shot_selection['transition_smoothness'] = prefs.transition_smoothness
            clip_persona.style_vector.shot_selection['cut_frequency'] = prefs.cut_frequency
            
            # 更新内容结构
            clip_persona.style_vector.content_structure['narrative_style'] = prefs.narrative_style
            clip_persona.style_vector.content_structure['emotional_intensity'] = prefs.emotional_intensity
            clip_persona.style_vector.content_structure['visual_complexity'] = prefs.visual_complexity
            clip_persona.style_vector.content_structure['audio_emphasis'] = prefs.audio_emphasis
            
            # 更新技术参数
            clip_persona.style_vector.technical_params['brightness'] = prefs.brightness
            clip_persona.style_vector.technical_params['contrast'] = prefs.contrast
            clip_persona.style_vector.technical_params['saturation'] = prefs.saturation
            clip_persona.style_vector.technical_params['sharpness'] = prefs.sharpness
            
            # 保存更新
            clip_persona.save_persona()
            
        except Exception as e:
            logger.error(f"同步风格偏好失败: {e}")


# 创建全局服务实例
persona_service = PersonaService()
