#!/usr/bin/env python3
"""
会话管理系统
支持多用户、多会话管理，用于并发任务处理
"""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import threading
import logging

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"          # 活跃
    IDLE = "idle"             # 空闲
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    ERROR = "error"           # 错误


class MessageType(Enum):
    """消息类型"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MULTIMODAL = "multimodal"
    SYSTEM = "system"


class MessageSender(Enum):
    """消息发送者"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """消息模型"""
    id: str
    content: str
    type: MessageType
    sender: MessageSender
    timestamp: str
    media_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "sender": self.sender.value if isinstance(self.sender, Enum) else self.sender,
            "timestamp": self.timestamp,
            "media_path": self.media_path,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建"""
        return cls(
            id=data["id"],
            content=data["content"],
            type=MessageType(data["type"]) if isinstance(data["type"], str) else data["type"],
            sender=MessageSender(data["sender"]) if isinstance(data["sender"], str) else data["sender"],
            timestamp=data["timestamp"],
            media_path=data.get("media_path"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Session:
    """会话模型（单用户模式）"""
    id: str
    title: str
    icon: str
    status: SessionStatus
    created_at: str
    updated_at: str
    messages: List[Message] = field(default_factory=list)
    progress: float = 0.0
    current_video: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        self._update_progress()
    
    def _update_progress(self):
        """更新进度"""
        user_messages = sum(1 for m in self.messages if m.sender == MessageSender.USER)
        # 每10条用户消息增加10%进度，最大100%
        self.progress = min(user_messages * 0.1, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "icon": self.icon,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self.messages],
            "progress": self.progress,
            "current_video": self.current_video,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建（兼容旧数据，忽略user_id）"""
        return cls(
            id=data["id"],
            title=data["title"],
            icon=data["icon"],
            status=SessionStatus(data["status"]) if isinstance(data["status"], str) else data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=[Message.from_dict(m) for m in data.get("messages", [])],
            progress=data.get("progress", 0.0),
            current_video=data.get("current_video"),
            metadata=data.get("metadata", {})
        )


class SessionManager:
    """会话管理器（单用户模式）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            # 使用项目根目录的data文件夹
            base_dir = Path(__file__).parent.parent.parent / "data" / "sessions"
            self.sessions_dir = base_dir
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
            self.sessions: Dict[str, Session] = {}
            self._load_all_sessions()
            self._initialized = True
    
    def _load_all_sessions(self):
        """加载所有会话"""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = Session.from_dict(data)
                    self.sessions[session.id] = session
            
            logger.info(f"加载了 {len(self.sessions)} 个会话")
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
    
    def _save_session(self, session: Session):
        """保存会话到文件"""
        try:
            session_file = self.sessions_dir / f"{session.id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"会话已保存: {session.id}")
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            raise
    
    def create_session(
        self, 
        title: Optional[str] = None,
        icon: str = "🎬"
    ) -> Session:
        """
        创建新会话（单用户模式）
        
        Args:
            title: 会话标题（可选）
            icon: 会话图标
            
        Returns:
            创建的会话对象
        """
        now = datetime.now()
        session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        if title is None:
            title = f"新对话 {now.strftime('%m-%d %H:%M')}"
        
        session = Session(
            id=session_id,
            title=title,
            icon=icon,
            status=SessionStatus.ACTIVE,
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
        
        # 保存到内存和文件
        self.sessions[session_id] = session
        
        self._save_session(session)
        
        logger.info(f"创建新会话: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[Session]:
        """获取所有会话（单用户模式）"""
        sessions = list(self.sessions.values())
        # 按更新时间排序，最新的在前
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions
    
    def add_message_to_session(
        self, 
        session_id: str, 
        content: str,
        message_type: MessageType,
        sender: MessageSender,
        media_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Message]:
        """
        向会话添加消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            message_type: 消息类型
            sender: 发送者
            media_path: 媒体文件路径
            metadata: 额外元数据
            
        Returns:
            创建的消息对象
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"会话不存在: {session_id}")
            return None
        
        message = Message(
            id=f"msg_{uuid.uuid4().hex}",
            content=content,
            type=message_type,
            sender=sender,
            timestamp=datetime.now().isoformat(),
            media_path=media_path,
            metadata=metadata or {}
        )
        
        session.add_message(message)
        self._save_session(session)
        
        return message
    
    def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        current_video: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新会话信息
        
        Args:
            session_id: 会话ID
            title: 新标题
            status: 新状态
            current_video: 当前视频路径
            metadata: 元数据更新
            
        Returns:
            是否更新成功
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        if title:
            session.title = title
        if status:
            session.status = status
        if current_video is not None:
            session.current_video = current_video
        if metadata:
            session.metadata.update(metadata)
        
        session.updated_at = datetime.now().isoformat()
        self._save_session(session)
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            # 从内存中删除
            del self.sessions[session_id]
            
            # 删除文件
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            logger.info(f"会话已删除: {session_id}")
            return True
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    def delete_all_sessions(self) -> int:
        """
        删除所有会话（单用户模式）
        
        Returns:
            删除的会话数量
        """
        session_ids = list(self.sessions.keys())
        count = 0
        
        for session_id in session_ids:
            if self.delete_session(session_id):
                count += 1
        
        return count
    
    def get_session_count(self) -> int:
        """获取会话数量（单用户模式）"""
        return len(self.sessions)
    
    def clear_old_sessions(self, days: int = 30) -> int:
        """
        清理超过指定天数的会话
        
        Args:
            days: 天数阈值
            
        Returns:
            清理的会话数量
        """
        from datetime import timedelta
        
        threshold = datetime.now() - timedelta(days=days)
        count = 0
        
        for session in list(self.sessions.values()):
            updated = datetime.fromisoformat(session.updated_at)
            if updated < threshold:
                if self.delete_session(session.id):
                    count += 1
        
        return count


# 全局单例
session_manager = SessionManager()


