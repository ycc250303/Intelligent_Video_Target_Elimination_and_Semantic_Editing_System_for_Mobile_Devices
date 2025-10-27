#!/usr/bin/env python3
"""
并发任务执行器
支持多会话并发处理视频任务
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"          # 等待中
    RUNNING = "running"          # 运行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"      # 已取消


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    session_id: str
    status: TaskStatus
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConcurrentTaskExecutor:
    """并发任务执行器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, max_workers: int = 4):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, max_workers: int = 4):
        if not hasattr(self, '_initialized'):
            self.max_workers = max_workers
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.tasks: Dict[str, Future] = {}
            self.task_results: Dict[str, TaskResult] = {}
            self.task_metadata: Dict[str, Dict[str, Any]] = {}
            self._initialized = True
            logger.info(f"并发任务执行器已初始化，最大工作线程数: {max_workers}")
    
    def submit_task(
        self,
        session_id: str,
        task_func: Callable,
        *args,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        提交任务到执行器
        
        Args:
            session_id: 会话ID
            task_func: 任务函数
            *args: 位置参数
            task_id: 任务ID（可选，自动生成）
            metadata: 任务元数据
            **kwargs: 关键字参数
            
        Returns:
            任务ID
        """
        if task_id is None:
            task_id = f"task_{session_id}_{uuid.uuid4().hex[:8]}"
        
        # 创建初始任务结果
        self.task_results[task_id] = TaskResult(
            task_id=task_id,
            session_id=session_id,
            status=TaskStatus.PENDING
        )
        
        self.task_metadata[task_id] = metadata or {}
        
        # 包装任务函数以捕获结果
        def wrapped_task():
            start_time = time.time()
            try:
                # 更新状态为运行中
                self.task_results[task_id].status = TaskStatus.RUNNING
                
                # 执行任务
                result = task_func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                
                # 更新结果
                self.task_results[task_id].status = TaskStatus.COMPLETED
                self.task_results[task_id].execution_time = execution_time
                
                # 如果结果是字典，提取相关信息
                if isinstance(result, dict):
                    self.task_results[task_id].output_path = result.get('output_path')
                    self.task_results[task_id].metadata.update(result.get('metadata', {}))
                elif isinstance(result, str):
                    self.task_results[task_id].output_path = result
                
                logger.info(f"任务完成: {task_id}, 耗时: {execution_time:.2f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = str(e)
                
                self.task_results[task_id].status = TaskStatus.FAILED
                self.task_results[task_id].error_message = error_msg
                self.task_results[task_id].execution_time = execution_time
                
                logger.error(f"任务失败: {task_id}, 错误: {error_msg}")
                raise
        
        # 提交任务
        future = self.executor.submit(wrapped_task)
        self.tasks[task_id] = future
        
        logger.info(f"任务已提交: {task_id} for session {session_id}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        result = self.task_results.get(task_id)
        return result.status if result else None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.task_results.get(task_id)
    
    def is_task_done(self, task_id: str) -> bool:
        """检查任务是否完成"""
        future = self.tasks.get(task_id)
        return future.done() if future else False
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        future = self.tasks.get(task_id)
        if future and future.cancel():
            self.task_results[task_id].status = TaskStatus.CANCELLED
            logger.info(f"任务已取消: {task_id}")
            return True
        return False
    
    def get_session_tasks(self, session_id: str) -> Dict[str, TaskResult]:
        """获取会话的所有任务"""
        return {
            task_id: result 
            for task_id, result in self.task_results.items() 
            if result.session_id == session_id
        }
    
    def get_running_tasks(self) -> Dict[str, TaskResult]:
        """获取所有正在运行的任务"""
        return {
            task_id: result 
            for task_id, result in self.task_results.items() 
            if result.status == TaskStatus.RUNNING
        }
    
    def get_pending_tasks(self) -> Dict[str, TaskResult]:
        """获取所有等待中的任务"""
        return {
            task_id: result 
            for task_id, result in self.task_results.items() 
            if result.status == TaskStatus.PENDING
        }
    
    def clear_completed_tasks(self, session_id: Optional[str] = None) -> int:
        """
        清理已完成的任务
        
        Args:
            session_id: 会话ID（可选，仅清理特定会话）
            
        Returns:
            清理的任务数量
        """
        count = 0
        tasks_to_remove = []
        
        for task_id, result in self.task_results.items():
            if session_id and result.session_id != session_id:
                continue
            
            if result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            if task_id in self.tasks:
                del self.tasks[task_id]
            if task_id in self.task_results:
                del self.task_results[task_id]
            if task_id in self.task_metadata:
                del self.task_metadata[task_id]
            count += 1
        
        logger.info(f"清理了 {count} 个已完成的任务")
        return count
    
    def get_executor_stats(self) -> Dict[str, Any]:
        """获取执行器统计信息"""
        pending = len(self.get_pending_tasks())
        running = len(self.get_running_tasks())
        completed = sum(1 for r in self.task_results.values() if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.task_results.values() if r.status == TaskStatus.FAILED)
        
        return {
            "max_workers": self.max_workers,
            "total_tasks": len(self.task_results),
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "available_workers": self.max_workers - running
        }
    
    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        logger.info("正在关闭并发任务执行器...")
        self.executor.shutdown(wait=wait)
        logger.info("并发任务执行器已关闭")


# 全局单例
task_executor = ConcurrentTaskExecutor(max_workers=4)


