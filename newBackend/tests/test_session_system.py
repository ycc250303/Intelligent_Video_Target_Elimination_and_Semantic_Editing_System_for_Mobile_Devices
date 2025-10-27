#!/usr/bin/env python3
"""
多会话管理系统测试脚本
演示会话创建、任务提交、并发处理等功能
"""

import time
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_manager import session_manager, MessageType, MessageSender, SessionStatus
from core.concurrent_task_executor import task_executor


def test_basic_session_management():
    """测试基础会话管理"""
    print("\n" + "="*60)
    print("测试1: 基础会话管理")
    print("="*60)
    
    # 创建会话
    user_id = "test_user_001"
    session1 = session_manager.create_session(user_id, title="视频剪辑项目1")
    session2 = session_manager.create_session(user_id, title="图片生成视频项目")
    session3 = session_manager.create_session(user_id, title="批量处理项目")
    
    print(f"✓ 创建了3个会话")
    print(f"  - {session1.title} (ID: {session1.id})")
    print(f"  - {session2.title} (ID: {session2.id})")
    print(f"  - {session3.title} (ID: {session3.id})")
    
    # 添加消息
    session_manager.add_message_to_session(
        session1.id,
        content="请帮我剪掉视频前3秒",
        message_type=MessageType.TEXT,
        sender=MessageSender.USER
    )
    
    session_manager.add_message_to_session(
        session1.id,
        content="好的,我会帮你剪掉视频的前3秒",
        message_type=MessageType.TEXT,
        sender=MessageSender.ASSISTANT
    )
    
    print(f"\n✓ 添加了消息到会话1")
    
    # 获取用户所有会话
    sessions = session_manager.get_user_sessions(user_id)
    print(f"\n✓ 用户共有 {len(sessions)} 个会话")
    
    # 更新会话状态
    session_manager.update_session(
        session1.id,
        status=SessionStatus.COMPLETED,
        current_video="/path/to/output.mp4"
    )
    print(f"✓ 更新了会话1的状态为: COMPLETED")
    
    return session1.id, session2.id, session3.id


def test_concurrent_tasks():
    """测试并发任务处理"""
    print("\n" + "="*60)
    print("测试2: 并发任务处理")
    print("="*60)
    
    # 创建测试会话
    user_id = "test_user_002"
    sessions = []
    for i in range(3):
        session = session_manager.create_session(
            user_id, 
            title=f"并发任务测试 {i+1}"
        )
        sessions.append(session)
    
    print(f"✓ 创建了 {len(sessions)} 个会话用于并发测试")
    
    # 定义模拟任务函数
    def mock_video_task(task_session_id, duration):
        """模拟视频处理任务"""
        print(f"  开始处理会话 {task_session_id} 的任务...")
        time.sleep(duration)  # 模拟处理时间
        result_path = f"/output/session_{task_session_id}_result.mp4"
        print(f"  完成会话 {task_session_id} 的任务")
        return {
            "output_path": result_path,
            "metadata": {"duration": duration}
        }
    
    # 提交并发任务
    task_ids = []
    for i, session in enumerate(sessions):
        # 修复：使用位置参数传递给 mock_video_task
        task_id = task_executor.submit_task(
            session_id=session.id,
            task_func=mock_video_task,
            task_session_id=session.id,  # 通过 **kwargs 传递
            duration=2 + i,              # 通过 **kwargs 传递
            metadata={"task_name": f"Task {i+1}"}
        )
        task_ids.append(task_id)
        print(f"✓ 提交任务 {i+1}: {task_id}")
    
    # 监控任务执行
    print("\n监控任务执行状态...")
    start_time = time.time()
    
    while True:
        stats = task_executor.get_executor_stats()
        running = stats["running"]
        completed = stats["completed"]
        
        print(f"  [+{time.time()-start_time:.1f}s] 运行中: {running}, 已完成: {completed}/{len(task_ids)}")
        
        if completed >= len(task_ids):
            break
        
        time.sleep(1)
    
    # 显示结果
    print("\n任务执行结果:")
    for task_id in task_ids:
        result = task_executor.get_task_result(task_id)
        print(f"  - 任务 {result.task_id[:20]}...")
        print(f"    状态: {result.status.value}")
        print(f"    耗时: {result.execution_time:.2f}s")
        print(f"    输出: {result.output_path}")
    
    total_time = time.time() - start_time
    print(f"\n✓ 总耗时: {total_time:.2f}s (并发执行)")
    print(f"  如果串行执行需要: {sum(range(2, 2+len(sessions)))}s")


def test_session_persistence():
    """测试会话持久化"""
    print("\n" + "="*60)
    print("测试3: 会话持久化")
    print("="*60)
    
    user_id = "test_user_003"
    
    # 创建会话并添加消息
    session = session_manager.create_session(user_id, title="持久化测试")
    original_id = session.id
    
    # 添加多条消息
    for i in range(5):
        session_manager.add_message_to_session(
            session.id,
            content=f"测试消息 {i+1}",
            message_type=MessageType.TEXT,
            sender=MessageSender.USER if i % 2 == 0 else MessageSender.ASSISTANT
        )
    
    print(f"✓ 创建会话并添加了5条消息")
    print(f"  会话ID: {original_id}")
    
    # 模拟重新加载（从文件加载）
    loaded_session = session_manager.get_session(original_id)
    
    if loaded_session:
        print(f"✓ 成功加载会话")
        print(f"  标题: {loaded_session.title}")
        print(f"  消息数: {len(loaded_session.messages)}")
        print(f"  进度: {loaded_session.progress*100:.0f}%")
    else:
        print("✗ 加载会话失败")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试4: 错误处理")
    print("="*60)
    
    # 测试获取不存在的会话
    session = session_manager.get_session("nonexistent_session")
    print(f"✓ 获取不存在的会话: {session is None}")
    
    # 测试删除不存在的会话
    success = session_manager.delete_session("nonexistent_session")
    print(f"✓ 删除不存在的会话: {not success}")
    
    # 测试添加消息到不存在的会话
    message = session_manager.add_message_to_session(
        "nonexistent_session",
        content="test",
        message_type=MessageType.TEXT,
        sender=MessageSender.USER
    )
    print(f"✓ 向不存在的会话添加消息: {message is None}")


def test_cleanup():
    """测试清理功能"""
    print("\n" + "="*60)
    print("测试5: 清理功能")
    print("="*60)
    
    user_id = "test_user_cleanup"
    
    # 创建多个会话
    for i in range(5):
        session_manager.create_session(user_id, title=f"清理测试 {i+1}")
    
    sessions = session_manager.get_user_sessions(user_id)
    print(f"✓ 创建了 {len(sessions)} 个会话")
    
    # 删除所有会话
    count = session_manager.delete_all_user_sessions(user_id)
    print(f"✓ 删除了 {count} 个会话")
    
    # 验证
    remaining = session_manager.get_user_sessions(user_id)
    print(f"✓ 剩余会话数: {len(remaining)}")
    
    # 清理已完成的任务
    cleared = task_executor.clear_completed_tasks()
    print(f"✓ 清理了 {cleared} 个已完成的任务")


def print_system_stats():
    """打印系统统计信息"""
    print("\n" + "="*60)
    print("系统统计信息")
    print("="*60)
    
    # 会话统计
    total_sessions = session_manager.get_session_count()
    print(f"总会话数: {total_sessions}")
    
    # 任务统计
    stats = task_executor.get_executor_stats()
    print(f"\n执行器统计:")
    print(f"  最大工作线程: {stats['max_workers']}")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  等待中: {stats['pending']}")
    print(f"  运行中: {stats['running']}")
    print(f"  已完成: {stats['completed']}")
    print(f"  失败: {stats['failed']}")
    print(f"  可用线程: {stats['available_workers']}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("CoEdit 多会话管理系统测试")
    print("="*60)
    
    try:
        # 运行所有测试
        test_basic_session_management()
        test_concurrent_tasks()
        test_session_persistence()
        test_error_handling()
        test_cleanup()
        
        # 显示统计
        print_system_stats()
        
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭执行器
        print("\n正在关闭系统...")
        task_executor.shutdown(wait=True)
        print("系统已关闭\n")


if __name__ == "__main__":
    main()

