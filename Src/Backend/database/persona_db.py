"""
Persona数据库管理
使用SQLite作为轻量级数据库存储Persona数据
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from models.persona_model import PersonaModel, PersonaCategory, PersonaStatus, UserFeedback, EditingOperation


class PersonaDatabase:
    """Persona数据库管理类"""
    
    def __init__(self, db_path: str = "persona_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            # 创建Persona主表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    author TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    is_public BOOLEAN DEFAULT 0,
                    is_featured BOOLEAN DEFAULT 0,
                    tags TEXT,  -- JSON格式存储标签数组
                    style_preferences TEXT,  -- JSON格式存储风格偏好
                    instruction_templates TEXT,  -- JSON格式存储指令模板
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version TEXT DEFAULT '1.0'
                )
            """)
            
            # 创建Persona统计表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS persona_stats (
                    persona_id TEXT PRIMARY KEY,
                    usage_count INTEGER DEFAULT 0,
                    download_count INTEGER DEFAULT 0,
                    rating_average REAL DEFAULT 0.0,
                    rating_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            """)
            
            # 创建剪辑操作历史表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editing_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    parameters TEXT,  -- JSON格式存储参数
                    user_rating REAL,
                    execution_time REAL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            """)
            
            # 创建用户反馈表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id TEXT PRIMARY KEY,
                    persona_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    rating REAL NOT NULL,
                    style_preferences TEXT,  -- JSON格式
                    operation_feedback TEXT,  -- JSON格式
                    text_feedback TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            """)
            
            # 创建训练数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,  -- 'video_analyzed', 'successful_operation', etc.
                    data_content TEXT,  -- JSON格式存储数据内容
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
                )
            """)
            
            # 创建用户表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    preferences TEXT  -- JSON格式存储用户偏好
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_author ON personas (author)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_category ON personas (category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_status ON personas (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_personas_featured ON personas (is_featured)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_operations_persona ON editing_operations (persona_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_persona ON user_feedback (persona_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user ON user_feedback (user_id)")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_persona(self, persona: PersonaModel) -> bool:
        """创建新的Persona"""
        try:
            with self.get_connection() as conn:
                # 插入主表数据
                conn.execute("""
                    INSERT INTO personas (
                        id, name, description, category, author, status, 
                        is_public, is_featured, tags, style_preferences, 
                        instruction_templates, created_at, updated_at, version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona.metadata.id,
                    persona.metadata.name,
                    persona.metadata.description,
                    persona.metadata.category.value,
                    persona.metadata.author,
                    persona.metadata.status.value,
                    persona.metadata.is_public,
                    persona.metadata.is_featured,
                    json.dumps(persona.metadata.tags, ensure_ascii=False),
                    json.dumps(persona.style_preferences.__dict__, ensure_ascii=False),
                    json.dumps(persona.instruction_templates, ensure_ascii=False),
                    persona.metadata.created_at.isoformat(),
                    persona.metadata.updated_at.isoformat(),
                    persona.metadata.version
                ))
                
                # 插入统计数据
                conn.execute("""
                    INSERT INTO persona_stats (
                        persona_id, usage_count, download_count, rating_average,
                        rating_count, share_count, view_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona.metadata.id,
                    persona.stats.usage_count,
                    persona.stats.download_count,
                    persona.stats.rating_average,
                    persona.stats.rating_count,
                    persona.stats.share_count,
                    persona.stats.view_count
                ))
                
                return True
        except Exception as e:
            print(f"创建Persona失败: {e}")
            return False
    
    def get_persona(self, persona_id: str) -> Optional[PersonaModel]:
        """获取Persona"""
        try:
            with self.get_connection() as conn:
                # 获取基础数据
                cursor = conn.execute("""
                    SELECT p.*, s.usage_count, s.download_count, s.rating_average,
                           s.rating_count, s.share_count, s.view_count
                    FROM personas p
                    LEFT JOIN persona_stats s ON p.id = s.persona_id
                    WHERE p.id = ?
                """, (persona_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # 重建PersonaModel
                persona = PersonaModel(
                    name=row['name'],
                    description=row['description'],
                    category=PersonaCategory(row['category']),
                    author=row['author'],
                    persona_id=row['id']
                )
                
                # 恢复元数据
                persona.metadata.status = PersonaStatus(row['status'])
                persona.metadata.is_public = bool(row['is_public'])
                persona.metadata.is_featured = bool(row['is_featured'])
                persona.metadata.tags = json.loads(row['tags'] or '[]')
                persona.metadata.created_at = datetime.fromisoformat(row['created_at'])
                persona.metadata.updated_at = datetime.fromisoformat(row['updated_at'])
                persona.metadata.version = row['version']
                
                # 恢复风格偏好
                if row['style_preferences']:
                    prefs_data = json.loads(row['style_preferences'])
                    for key, value in prefs_data.items():
                        if hasattr(persona.style_preferences, key):
                            setattr(persona.style_preferences, key, value)
                
                # 恢复指令模板
                if row['instruction_templates']:
                    persona.instruction_templates = json.loads(row['instruction_templates'])
                
                # 恢复统计数据
                if row['usage_count'] is not None:
                    persona.stats.usage_count = row['usage_count']
                    persona.stats.download_count = row['download_count']
                    persona.stats.rating_average = row['rating_average']
                    persona.stats.rating_count = row['rating_count']
                    persona.stats.share_count = row['share_count']
                    persona.stats.view_count = row['view_count']
                
                # 获取操作历史
                persona.editing_history = self._get_editing_history(persona_id)
                
                # 获取反馈历史
                persona.feedback_history = self._get_feedback_history(persona_id)
                
                return persona
                
        except Exception as e:
            print(f"获取Persona失败: {e}")
            return None
    
    def update_persona(self, persona: PersonaModel) -> bool:
        """更新Persona"""
        try:
            with self.get_connection() as conn:
                # 更新主表
                conn.execute("""
                    UPDATE personas SET
                        name = ?, description = ?, category = ?, status = ?,
                        is_public = ?, is_featured = ?, tags = ?,
                        style_preferences = ?, instruction_templates = ?,
                        updated_at = ?, version = ?
                    WHERE id = ?
                """, (
                    persona.metadata.name,
                    persona.metadata.description,
                    persona.metadata.category.value,
                    persona.metadata.status.value,
                    persona.metadata.is_public,
                    persona.metadata.is_featured,
                    json.dumps(persona.metadata.tags, ensure_ascii=False),
                    json.dumps(persona.style_preferences.__dict__, ensure_ascii=False),
                    json.dumps(persona.instruction_templates, ensure_ascii=False),
                    datetime.now().isoformat(),
                    persona.metadata.version,
                    persona.metadata.id
                ))
                
                # 更新统计数据
                conn.execute("""
                    UPDATE persona_stats SET
                        usage_count = ?, download_count = ?, rating_average = ?,
                        rating_count = ?, share_count = ?, view_count = ?
                    WHERE persona_id = ?
                """, (
                    persona.stats.usage_count,
                    persona.stats.download_count,
                    persona.stats.rating_average,
                    persona.stats.rating_count,
                    persona.stats.share_count,
                    persona.stats.view_count,
                    persona.metadata.id
                ))
                
                return True
        except Exception as e:
            print(f"更新Persona失败: {e}")
            return False
    
    def delete_persona(self, persona_id: str) -> bool:
        """删除Persona"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
                return True
        except Exception as e:
            print(f"删除Persona失败: {e}")
            return False
    
    def list_personas(self, 
                     author: Optional[str] = None,
                     category: Optional[PersonaCategory] = None,
                     status: Optional[PersonaStatus] = None,
                     is_public: Optional[bool] = None,
                     is_featured: Optional[bool] = None,
                     limit: int = 50,
                     offset: int = 0) -> List[Dict[str, Any]]:
        """列出Persona（支持筛选）"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT p.*, s.usage_count, s.download_count, s.rating_average,
                           s.rating_count, s.share_count, s.view_count
                    FROM personas p
                    LEFT JOIN persona_stats s ON p.id = s.persona_id
                    WHERE 1=1
                """
                params = []
                
                if author:
                    query += " AND p.author = ?"
                    params.append(author)
                
                if category:
                    query += " AND p.category = ?"
                    params.append(category.value)
                
                if status:
                    query += " AND p.status = ?"
                    params.append(status.value)
                
                if is_public is not None:
                    query += " AND p.is_public = ?"
                    params.append(is_public)
                
                if is_featured is not None:
                    query += " AND p.is_featured = ?"
                    params.append(is_featured)
                
                query += " ORDER BY p.updated_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    persona_data = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'category': row['category'],
                        'author': row['author'],
                        'status': row['status'],
                        'is_public': bool(row['is_public']),
                        'is_featured': bool(row['is_featured']),
                        'tags': json.loads(row['tags'] or '[]'),
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'version': row['version'],
                        'stats': {
                            'usage_count': row['usage_count'] or 0,
                            'download_count': row['download_count'] or 0,
                            'rating_average': row['rating_average'] or 0.0,
                            'rating_count': row['rating_count'] or 0,
                            'share_count': row['share_count'] or 0,
                            'view_count': row['view_count'] or 0
                        }
                    }
                    result.append(persona_data)
                
                return result
                
        except Exception as e:
            print(f"列出Persona失败: {e}")
            return []
    
    def add_editing_operation(self, persona_id: str, operation: EditingOperation) -> bool:
        """添加剪辑操作记录"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO editing_operations (
                        persona_id, operation_type, parameters, user_rating,
                        execution_time, success, error_message, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona_id,
                    operation.operation_type,
                    json.dumps(operation.parameters, ensure_ascii=False),
                    operation.user_rating,
                    operation.execution_time,
                    operation.success,
                    operation.error_message,
                    operation.timestamp.isoformat()
                ))
                
                # 更新使用统计
                conn.execute("""
                    UPDATE persona_stats 
                    SET usage_count = usage_count + 1
                    WHERE persona_id = ?
                """, (persona_id,))
                
                return True
        except Exception as e:
            print(f"添加操作记录失败: {e}")
            return False
    
    def add_user_feedback(self, feedback: UserFeedback) -> bool:
        """添加用户反馈"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO user_feedback (
                        id, persona_id, user_id, rating, style_preferences,
                        operation_feedback, text_feedback, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.feedback_id,
                    feedback.persona_id,
                    feedback.user_id,
                    feedback.rating,
                    json.dumps(feedback.style_preferences, ensure_ascii=False) if feedback.style_preferences else None,
                    json.dumps(feedback.operation_feedback, ensure_ascii=False) if feedback.operation_feedback else None,
                    feedback.text_feedback,
                    feedback.timestamp.isoformat()
                ))
                
                # 更新评分统计
                self._update_rating_stats(feedback.persona_id, feedback.rating)
                
                return True
        except Exception as e:
            print(f"添加用户反馈失败: {e}")
            return False
    
    def get_featured_personas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取推荐的Persona"""
        return self.list_personas(is_featured=True, is_public=True, limit=limit)
    
    def get_popular_personas(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门Persona（基于使用量和评分）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT p.*, s.usage_count, s.download_count, s.rating_average,
                           s.rating_count, s.share_count, s.view_count,
                           (s.usage_count * 0.3 + s.rating_average * s.rating_count * 0.4 + 
                            s.download_count * 0.2 + s.share_count * 0.1) as popularity_score
                    FROM personas p
                    LEFT JOIN persona_stats s ON p.id = s.persona_id
                    WHERE p.is_public = 1 AND p.status = 'active'
                    ORDER BY popularity_score DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    persona_data = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'category': row['category'],
                        'author': row['author'],
                        'tags': json.loads(row['tags'] or '[]'),
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'stats': {
                            'usage_count': row['usage_count'] or 0,
                            'download_count': row['download_count'] or 0,
                            'rating_average': row['rating_average'] or 0.0,
                            'rating_count': row['rating_count'] or 0,
                            'share_count': row['share_count'] or 0,
                            'view_count': row['view_count'] or 0
                        },
                        'popularity_score': row['popularity_score'] or 0
                    }
                    result.append(persona_data)
                
                return result
                
        except Exception as e:
            print(f"获取热门Persona失败: {e}")
            return []
    
    def search_personas(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索Persona"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT p.*, s.usage_count, s.download_count, s.rating_average,
                           s.rating_count, s.share_count, s.view_count
                    FROM personas p
                    LEFT JOIN persona_stats s ON p.id = s.persona_id
                    WHERE (p.name LIKE ? OR p.description LIKE ? OR p.tags LIKE ?)
                    ORDER BY COALESCE(s.rating_average, 0) DESC, COALESCE(s.usage_count, 0) DESC
                    LIMIT ?
                """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
                
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    persona_data = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'category': row['category'],
                        'author': row['author'],
                        'tags': json.loads(row['tags'] or '[]'),
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'stats': {
                            'usage_count': row['usage_count'] or 0,
                            'download_count': row['download_count'] or 0,
                            'rating_average': row['rating_average'] or 0.0,
                            'rating_count': row['rating_count'] or 0,
                            'share_count': row['share_count'] or 0,
                            'view_count': row['view_count'] or 0
                        }
                    }
                    result.append(persona_data)
                
                return result
                
        except Exception as e:
            print(f"搜索Persona失败: {e}")
            return []
    
    def _get_editing_history(self, persona_id: str) -> List[EditingOperation]:
        """获取剪辑历史"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM editing_operations 
                    WHERE persona_id = ? 
                    ORDER BY timestamp DESC
                """, (persona_id,))
                
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    operation = EditingOperation(
                        operation_type=row['operation_type'],
                        parameters=json.loads(row['parameters'] or '{}'),
                        user_rating=row['user_rating'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        execution_time=row['execution_time'],
                        success=bool(row['success']),
                        error_message=row['error_message']
                    )
                    history.append(operation)
                
                return history
                
        except Exception as e:
            print(f"获取剪辑历史失败: {e}")
            return []
    
    def _get_feedback_history(self, persona_id: str) -> List[UserFeedback]:
        """获取反馈历史"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM user_feedback 
                    WHERE persona_id = ? 
                    ORDER BY timestamp DESC
                """, (persona_id,))
                
                rows = cursor.fetchall()
                
                feedback_list = []
                for row in rows:
                    feedback = UserFeedback(
                        feedback_id=row['id'],
                        persona_id=row['persona_id'],
                        user_id=row['user_id'],
                        rating=row['rating'],
                        style_preferences=json.loads(row['style_preferences'] or '{}') if row['style_preferences'] else None,
                        operation_feedback=json.loads(row['operation_feedback'] or '{}') if row['operation_feedback'] else None,
                        text_feedback=row['text_feedback'],
                        timestamp=datetime.fromisoformat(row['timestamp'])
                    )
                    feedback_list.append(feedback)
                
                return feedback_list
                
        except Exception as e:
            print(f"获取反馈历史失败: {e}")
            return []
    
    def _update_rating_stats(self, persona_id: str, new_rating: float):
        """更新评分统计"""
        with self.get_connection() as conn:
            # 获取当前统计
            cursor = conn.execute("""
                SELECT rating_average, rating_count FROM persona_stats 
                WHERE persona_id = ?
            """, (persona_id,))
            
            row = cursor.fetchone()
            if row:
                current_avg = row['rating_average'] or 0.0
                current_count = row['rating_count'] or 0
                
                # 计算新的平均值
                total_rating = current_avg * current_count + new_rating
                new_count = current_count + 1
                new_avg = total_rating / new_count
                
                # 更新统计
                conn.execute("""
                    UPDATE persona_stats 
                    SET rating_average = ?, rating_count = ?
                    WHERE persona_id = ?
                """, (new_avg, new_count, persona_id))
