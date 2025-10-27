#!/usr/bin/env python3
"""
快速入门示例 - 多模态视频编辑系统
演示如何使用系统的基本功能
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.multimodal_processor import MultimodalProcessor
from core.qwen_nlp_parser import DialogueManager
from core.video_operation_executor import VideoOperationExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_text_only():
    """示例1: 纯文本指令"""
    print("\n" + "="*60)
    print("示例1: 纯文本指令")
    print("="*60)
    
    manager = DialogueManager()
    
    # 用户输入
    user_input = "把视频的前3秒剪掉"
    print(f"\n👤 用户: {user_input}")
    
    # AI处理
    result = manager.process_user_input(user_input)
    
    print(f"\n🤖 AI响应: {result.get('response', '')}")
    print(f"✅ 解析成功: {result.get('success')}")
    
    if result.get('action'):
        print(f"\n📋 生成的操作JSON:")
        action = result['action']
        if action.startswith("action:"):
            action = action[7:].strip()
        try:
            operation = json.loads(action)
            print(json.dumps(operation, ensure_ascii=False, indent=2))
        except:
            print(action)


def example_2_with_image():
    """示例2: 图片+文本"""
    print("\n" + "="*60)
    print("示例2: 图片+文本")
    print("="*60)
    
    # 检查测试图片
    test_image = "test_image.png"
    if not Path(test_image).exists():
        print(f"\n⚠️  测试图片 {test_image} 不存在")
        print("提示: 请准备一个图片文件用于测试")
        return
    
    manager = DialogueManager()
    
    # 用户输入
    user_input = "使用这张图片生成一段5秒的视频"
    print(f"\n👤 用户: {user_input}")
    print(f"📎 附件: {test_image}")
    
    # AI处理
    result = manager.process_multimodal_input(
        text=user_input,
        image_paths=[test_image]
    )
    
    print(f"\n🤖 AI响应: {result.get('response', '')}")
    print(f"🎯 模态类型: {result.get('modal_type')}")
    print(f"✅ 解析成功: {result.get('success')}")


def example_3_with_video():
    """示例3: 视频+文本"""
    print("\n" + "="*60)
    print("示例3: 视频+文本")
    print("="*60)
    
    # 检查测试视频
    test_video = "test_video.mp4"
    if not Path(test_video).exists():
        print(f"\n⚠️  测试视频 {test_video} 不存在")
        print("提示: 请准备一个视频文件用于测试")
        return
    
    manager = DialogueManager()
    
    # 用户输入
    user_input = "分析这个视频的内容，然后添加合适的字幕"
    print(f"\n👤 用户: {user_input}")
    print(f"📎 附件: {test_video}")
    
    # AI处理
    result = manager.process_multimodal_input(
        text=user_input,
        video_paths=[test_video]
    )
    
    print(f"\n🤖 AI响应: {result.get('response', '')}")
    print(f"🎯 模态类型: {result.get('modal_type')}")
    print(f"✅ 解析成功: {result.get('success')}")


def example_4_execute_operation():
    """示例4: 完整流程 - 从指令到执行"""
    print("\n" + "="*60)
    print("示例4: 完整流程 - 从指令到执行")
    print("="*60)
    
    # 检查测试视频
    test_video = "test_video.mp4"
    if not Path(test_video).exists():
        print(f"\n⚠️  测试视频 {test_video} 不存在")
        print("提示: 请准备一个名为 test_video.mp4 的视频文件")
        return
    
    print(f"\n📹 使用测试视频: {test_video}")
    
    # 初始化组件
    manager = DialogueManager()
    executor = VideoOperationExecutor(output_dir="Results/quick_start")
    
    # 步骤1: 用户输入
    user_input = "把视频速度调整为2倍"
    print(f"\n[步骤1] 用户输入")
    print(f"👤 {user_input}")
    
    # 步骤2: AI理解
    print(f"\n[步骤2] AI理解指令")
    result = manager.process_user_input(user_input)
    print(f"🤖 {result.get('response', '')}")
    
    if not result.get('success') or not result.get('action'):
        print("❌ 指令解析失败")
        return
    
    # 步骤3: 提取操作JSON
    print(f"\n[步骤3] 生成操作JSON")
    action = result['action']
    if action.startswith("action:"):
        action = action[7:].strip()
    
    try:
        operation_json = json.loads(action)
        print(json.dumps(operation_json, ensure_ascii=False, indent=2))
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return
    
    # 步骤4: 执行操作
    print(f"\n[步骤4] 执行视频操作")
    print("⏳ 处理中...")
    
    exec_result = executor.execute_from_json(operation_json, test_video)
    
    if exec_result.success:
        print(f"\n✅ 操作成功完成!")
        print(f"📁 输出文件: {exec_result.output_path}")
        print(f"⏱️  执行时间: {exec_result.execution_time:.2f}秒")
        
        # 验证文件
        if exec_result.output_path and Path(exec_result.output_path).exists():
            file_size = Path(exec_result.output_path).stat().st_size / (1024 * 1024)
            print(f"📊 文件大小: {file_size:.2f} MB")
    else:
        print(f"\n❌ 操作失败: {exec_result.error_message}")


def example_5_batch_operations():
    """示例5: 批量操作"""
    print("\n" + "="*60)
    print("示例5: 批量操作")
    print("="*60)
    
    # 检查测试视频
    test_video = "test_video.mp4"
    if not Path(test_video).exists():
        print(f"\n⚠️  测试视频 {test_video} 不存在")
        return
    
    executor = VideoOperationExecutor(output_dir="Results/batch")
    
    # 定义多个操作
    operations = [
        {
            "operations": {
                "operation": "adjust_speed",
                "params": {"factor": 1.5},
                "editor": "ffmpeg"
            }
        },
        {
            "operations": {
                "operation": "adjust_volume",
                "params": {"factor": 0.8},
                "editor": "ffmpeg"
            }
        }
    ]
    
    print(f"\n📝 准备执行 {len(operations)} 个连续操作:")
    for i, op in enumerate(operations, 1):
        op_name = op["operations"]["operation"]
        params = op["operations"]["params"]
        print(f"  {i}. {op_name}: {params}")
    
    print(f"\n⏳ 批量处理中...")
    results = executor.execute_batch(operations, test_video)
    
    print(f"\n✅ 批量操作完成")
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"  ✅ 操作 {i} ({result.operation_name}): 成功")
        else:
            print(f"  ❌ 操作 {i} ({result.operation_name}): 失败")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎬 多模态视频编辑系统 - 快速入门示例")
    print("="*60)
    
    print("\n📚 本示例将演示系统的基本功能:")
    print("  1. 纯文本指令处理")
    print("  2. 图片+文本处理")
    print("  3. 视频+文本处理")
    print("  4. 完整的编辑流程")
    print("  5. 批量操作")
    
    print("\n💡 提示:")
    print("  - 某些示例需要测试文件 (test_video.mp4, test_image.png)")
    print("  - 如果文件不存在，相应示例将被跳过")
    print("  - 确保已配置 QWEN_API_KEY")
    
    input("\n按 Enter 键开始演示...")
    
    try:
        # 运行示例
        example_1_text_only()
        input("\n按 Enter 键继续...")
        
        example_2_with_image()
        input("\n按 Enter 键继续...")
        
        example_3_with_video()
        input("\n按 Enter 键继续...")
        
        example_4_execute_operation()
        input("\n按 Enter 键继续...")
        
        example_5_batch_operations()
        
        print("\n" + "="*60)
        print("🎉 所有示例演示完成!")
        print("="*60)
        
        print("\n📖 更多信息:")
        print("  - 查看 MULTIMODAL_SYSTEM_README.md 了解详细文档")
        print("  - 运行 test_multimodal_system.py 进行完整测试")
        print("  - 启动 fastapi_server.py 使用 HTTP API")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
    except Exception as e:
        logger.exception("演示过程中出错")
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()

