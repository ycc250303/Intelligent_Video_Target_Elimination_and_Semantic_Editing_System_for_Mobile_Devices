"""
重构的Persona API端点
提供完整的RESTful API接口
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from typing import Dict, Any

from services.persona_service import persona_service


logger = logging.getLogger(__name__)
persona_bp = Blueprint('persona', __name__, url_prefix='/api/persona')


def validate_request_data(data: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
    """验证请求数据"""
    if not data:
        return False, "请求数据不能为空"
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"缺少必填字段: {', '.join(missing_fields)}"
    
    return True, ""


@persona_bp.route('/create', methods=['POST'])
def create_persona():
    """创建新的Persona"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        is_valid, error_msg = validate_request_data(data, ['name', 'description', 'category', 'author'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        # 提取参数
        name = data['name'].strip()
        description = data['description'].strip()
        category = data['category'].strip()
        author = data['author'].strip()
        tags = data.get('tags', [])
        style_preferences = data.get('style_preferences', {})
        is_public = data.get('is_public', False)
        
        # 调用服务
        success, message, result = persona_service.create_persona(
            name=name,
            description=description,
            category=category,
            author=author,
            tags=tags,
            style_preferences=style_preferences,
            is_public=is_public
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"创建Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/get/<persona_id>', methods=['GET'])
def get_persona(persona_id: str):
    """获取Persona详情"""
    try:
        if not persona_id:
            return jsonify({'success': False, 'message': 'Persona ID不能为空'}), 400
        
        success, message, result = persona_service.get_persona(persona_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 404
            
    except Exception as e:
        logger.error(f"获取Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/update/<persona_id>', methods=['PUT'])
def update_persona(persona_id: str):
    """更新Persona"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        is_valid, error_msg = validate_request_data(data, ['author'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        author = data['author'].strip()
        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        tags = data.get('tags')
        style_preferences = data.get('style_preferences')
        is_public = data.get('is_public')
        
        success, message, result = persona_service.update_persona(
            persona_id=persona_id,
            author=author,
            name=name,
            description=description,
            category=category,
            tags=tags,
            style_preferences=style_preferences,
            is_public=is_public
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"更新Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/delete/<persona_id>', methods=['DELETE'])
def delete_persona(persona_id: str):
    """删除Persona"""
    try:
        data = request.get_json() or {}
        author = data.get('author')
        
        if not author:
            return jsonify({'success': False, 'message': '缺少author字段'}), 400
        
        success, message = persona_service.delete_persona(persona_id, author)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"删除Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/list', methods=['GET'])
def list_personas():
    """列出Persona"""
    try:
        # 获取查询参数
        author = request.args.get('author')
        category = request.args.get('category')
        status = request.args.get('status')
        is_public = request.args.get('is_public')
        is_featured = request.args.get('is_featured')
        limit = min(int(request.args.get('limit', 50)), 100)  # 最大100
        offset = int(request.args.get('offset', 0))
        
        # 转换布尔值参数
        if is_public is not None:
            is_public = is_public.lower() == 'true'
        if is_featured is not None:
            is_featured = is_featured.lower() == 'true'
        
        success, message, result = persona_service.list_personas(
            author=author,
            category=category,
            status=status,
            is_public=is_public,
            is_featured=is_featured,
            limit=limit,
            offset=offset
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'count': len(result)
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"列出Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/featured', methods=['GET'])
def get_featured_personas():
    """获取推荐Persona"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        success, message, result = persona_service.get_featured_personas(limit)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"获取推荐Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/popular', methods=['GET'])
def get_popular_personas():
    """获取热门Persona"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        success, message, result = persona_service.get_popular_personas(limit)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"获取热门Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/search', methods=['GET'])
def search_personas():
    """搜索Persona"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 20)), 100)
        
        if not query:
            return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400
        
        success, message, result = persona_service.search_personas(query, limit)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result,
                'query': query
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"搜索Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/analyze-video', methods=['POST'])
def analyze_video_preferences():
    """分析视频偏好"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['persona_id', 'video_path'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        persona_id = data['persona_id']
        video_path = data['video_path']
        
        success, message, result = persona_service.analyze_video_preferences(persona_id, video_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"视频偏好分析API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/feedback', methods=['POST'])
def process_user_feedback():
    """处理用户反馈"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['persona_id', 'user_id', 'rating'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        persona_id = data['persona_id']
        user_id = data['user_id']
        rating = float(data['rating'])
        style_preferences = data.get('style_preferences')
        operation_feedback = data.get('operation_feedback')
        text_feedback = data.get('text_feedback')
        
        success, message = persona_service.process_user_feedback(
            persona_id=persona_id,
            user_id=user_id,
            rating=rating,
            style_preferences=style_preferences,
            operation_feedback=operation_feedback,
            text_feedback=text_feedback
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'评分格式错误: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"用户反馈API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/generate-plan', methods=['POST'])
def generate_editing_plan():
    """生成剪辑方案"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['persona_id', 'instruction', 'video_path'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        persona_id = data['persona_id']
        instruction = data['instruction']
        video_path = data['video_path']
        user_id = data.get('user_id')
        
        success, message, result = persona_service.generate_editing_plan(
            persona_id=persona_id,
            user_instruction=instruction,
            video_path=video_path,
            user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"生成剪辑方案API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/record-operation', methods=['POST'])
def record_editing_operation():
    """记录剪辑操作"""
    try:
        data = request.get_json()
        
        is_valid, error_msg = validate_request_data(data, ['persona_id', 'operation_type', 'parameters'])
        if not is_valid:
            return jsonify({'success': False, 'message': error_msg}), 400
        
        persona_id = data['persona_id']
        operation_type = data['operation_type']
        parameters = data['parameters']
        success = data.get('success', True)
        execution_time = data.get('execution_time')
        error_message = data.get('error_message')
        user_rating = data.get('user_rating')
        
        success_result, message = persona_service.record_editing_operation(
            persona_id=persona_id,
            operation_type=operation_type,
            parameters=parameters,
            success=success,
            execution_time=execution_time,
            error_message=error_message,
            user_rating=user_rating
        )
        
        if success_result:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"记录剪辑操作API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/recommendations', methods=['POST'])
def get_persona_recommendations():
    """获取个性化Persona推荐"""
    try:
        data = request.get_json() or {}
        
        user_id = data.get('user_id')
        user_preferences = data.get('user_preferences')
        limit = min(int(data.get('limit', 5)), 20)
        
        if not user_id:
            return jsonify({'success': False, 'message': '缺少user_id字段'}), 400
        
        success, message, result = persona_service.get_persona_recommendations(
            user_id=user_id,
            user_preferences=user_preferences,
            limit=limit
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"获取Persona推荐API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/user/<author>', methods=['GET'])
def get_user_personas(author: str):
    """获取用户创建的Persona"""
    try:
        if not author:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        limit = min(int(request.args.get('limit', 50)), 100)
        
        success, message, result = persona_service.get_user_personas(author, limit)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"获取用户Persona API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/statistics/<persona_id>', methods=['GET'])
def get_persona_statistics(persona_id: str):
    """获取Persona统计信息"""
    try:
        if not persona_id:
            return jsonify({'success': False, 'message': 'Persona ID不能为空'}), 400
        
        success, message, result = persona_service.get_persona_statistics(persona_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 404
            
    except Exception as e:
        logger.error(f"获取Persona统计API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@persona_bp.route('/categories', methods=['GET'])
def get_persona_categories():
    """获取Persona分类列表"""
    try:
        from ..models.persona_model import PersonaCategory
        
        categories = [
            {
                'value': category.value,
                'label': {
                    'zh': {
                        'creative': '创意类',
                        'professional': '专业类',
                        'entertainment': '娱乐类',
                        'educational': '教育类',
                        'commercial': '商业类',
                        'lifestyle': '生活类'
                    }.get(category.value, category.value),
                    'en': category.value.title()
                }
            }
            for category in PersonaCategory
        ]
        
        return jsonify({
            'success': True,
            'message': '获取成功',
            'data': categories
        }), 200
        
    except Exception as e:
        logger.error(f"获取Persona分类API错误: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


# 错误处理
@persona_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '接口不存在'
    }), 404


@persona_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': '请求方法不允许'
    }), 405


@persona_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500
