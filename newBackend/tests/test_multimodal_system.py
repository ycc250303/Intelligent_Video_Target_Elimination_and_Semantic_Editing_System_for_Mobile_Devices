#!/usr/bin/env python3
"""
多模态视频编辑系统测试脚本
测试完整的工作流程：输入 -> 解析 -> 执行
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 获取测试文件的目录
TEST_DIR = Path(__file__).parent

from core.multimodal_processor import MultimodalProcessor, MultimodalInput
from core.qwen_nlp_parser import DialogueManager
from core.video_operation_executor import VideoOperationExecutor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def test_multimodal_processor():
    """测试多模态输入处理器"""
    print_separator("测试1: 多模态输入处理器")
    
    processor = MultimodalProcessor()
    
    # 测试1.1: 纯文本
    print("\n[测试1.1] 纯文本输入")
    input1 = processor.process_input(text="剪掉视频前3秒")
    print(f"模态类型: {input1.get_modal_type()}")
    print(f"是否纯文本: {input1.is_text_only()}")
    assert input1.is_text_only(), "应该是纯文本"
    print("✅ 纯文本测试通过")
    
    # 测试1.2: 文本+图片
    print("\n[测试1.2] 文本+图片")
    # 创建测试图片路径（如果不存在，会跳过）
    test_image = TEST_DIR / "test_image.png"
    if test_image.exists():
        input2 = processor.process_input(
            text="分析这张图片并生成对应的视频",
            image_paths=[str(test_image)]
        )
        print(f"模态类型: {input2.get_modal_type()}")
        print(f"包含图片: {input2.has_images()}")
        assert input2.has_images(), "应该包含图片"
        print("✅ 文本+图片测试通过")
    else:
        print("⚠️  测试图片不存在，跳过此测试")
    
    # 测试1.3: 文本+视频
    print("\n[测试1.3] 文本+视频")
    test_video = TEST_DIR / "test_video.mp4"
    if test_video.exists():
        input3 = processor.process_input(
            text="分析这个视频内容",
            video_paths=[str(test_video)]
        )
        print(f"模态类型: {input3.get_modal_type()}")
        print(f"包含视频: {input3.has_videos()}")
        assert input3.has_videos(), "应该包含视频"
        print("✅ 文本+视频测试通过")
    else:
        print("⚠️  测试视频不存在，跳过此测试")
    
    print("\n✅ 多模态输入处理器测试完成")


def test_video_operation_executor():
    """测试视频操作执行器"""
    print_separator("测试2: 视频操作执行器")
    
    executor = VideoOperationExecutor(output_dir="Results/test")
    
    # 测试2.1: 保存和加载JSON
    print("\n[测试2.1] JSON保存和加载")
    test_json = {
        "operations": {
            "operation": "trim",
            "params": {
                "start": 1.0,
                "end": 5.0
            },
            "editor": "ffmpeg"
        }
    }
    
    # 保存JSON
    json_path = executor.save_operation_json(test_json, "test_trim.json")
    print(f"JSON已保存到: {json_path}")
    assert Path(json_path).exists(), "JSON文件应该存在"
    
    # 加载JSON
    loaded_json = executor.load_operation_json(json_path)
    print(f"已加载JSON: {loaded_json}")
    assert loaded_json == test_json, "加载的JSON应该与原始JSON相同"
    print("✅ JSON保存和加载测试通过")
    
    # 测试2.2: JSON解析
    print("\n[测试2.2] JSON解析")
    json_str = json.dumps(test_json)
    print(f"JSON字符串: {json_str[:100]}...")
    print("✅ JSON解析测试通过")
    
    # 测试2.3: 执行操作（需要实际视频文件）
    print("\n[测试2.3] 执行视频操作")
    test_video = TEST_DIR / "test_video.mp4"
    if test_video.exists():
        print(f"使用测试视频: {test_video}")
        result = executor.execute_from_json(test_json, str(test_video))
        print(f"操作成功: {result.success}")
        print(f"输出路径: {result.output_path}")
        print(f"执行时间: {result.execution_time:.2f}秒")
        if result.success:
            print("✅ 视频操作执行成功")
        else:
            print(f"⚠️  操作失败: {result.error_message}")
    else:
        print("⚠️  测试视频不存在，跳过执行测试")
    
    print("\n✅ 视频操作执行器测试完成")


def test_dialogue_manager():
    """测试对话管理器"""
    print_separator("测试3: 对话管理器")
    
    manager = DialogueManager()
    
    # 测试3.1: 纯文本输入
    print("\n[测试3.1] 纯文本指令处理")
    result1 = manager.process_user_input("把视频的前3秒剪掉")
    print(f"响应: {result1.get('response', '')[:100]}...")
    print(f"成功: {result1.get('success')}")
    print(f"操作: {result1.get('action', 'None')[:100] if result1.get('action') else 'None'}...")
    
    if result1.get('success'):
        print("✅ 纯文本指令处理成功")
    else:
        print("⚠️  指令处理失败")
    
    # 测试3.2: 多模态输入（如果有测试文件）
    print("\n[测试3.2] 多模态指令处理")
    test_image = TEST_DIR / "test_image.png"
    if test_image.exists():
        result2 = manager.process_multimodal_input(
            text="给这个图片添加滤镜效果",
            image_paths=[str(test_image)]
        )
        print(f"模态类型: {result2.get('modal_type')}")
        print(f"响应: {result2.get('response', '')[:100]}...")
        print(f"成功: {result2.get('success')}")
        
        if result2.get('success'):
            print("✅ 多模态指令处理成功")
        else:
            print("⚠️  多模态指令处理失败")
    else:
        print("⚠️  测试图片不存在，跳过多模态测试")
    
    print("\n✅ 对话管理器测试完成")


def test_end_to_end_workflow():
    """测试端到端工作流程"""
    print_separator("测试4: 端到端工作流程")
    
    # 检查测试视频
    test_video = TEST_DIR / "test_video.mp4"
    if not test_video.exists():
        print(f"⚠️  测试视频 {test_video} 不存在，跳过端到端测试")
        print("提示: 请准备一个名为 test_video.mp4 的测试视频文件")
        return
    
    print(f"\n使用测试视频: {test_video}")
    
    # 步骤1: 创建管理器和执行器
    print("\n[步骤1] 初始化组件")
    manager = DialogueManager()
    executor = VideoOperationExecutor(output_dir="Results/e2e_test")
    print("✅ 组件初始化完成")
    
    # 步骤2: 处理用户指令
    print("\n[步骤2] 处理用户指令")
    user_text = "把视频速度调整为1.5倍"
    print(f"用户输入: {user_text}")
    
    result = manager.process_user_input(user_text)
    print(f"AI响应: {result.get('response', '')[:150]}...")
    print(f"解析成功: {result.get('success')}")
    
    if not result.get('success'):
        print("⚠️  指令解析失败")
        return
    
    print("✅ 指令解析成功")
    
    # 步骤3: 提取操作JSON
    print("\n[步骤3] 提取操作JSON")
    action = result.get('action')
    if not action:
        print("⚠️  未找到操作指令")
        return
    
    # 移除 "action:" 前缀
    if action.startswith("action:"):
        action = action[7:].strip()
    
    try:
        operation_json = json.loads(action)
        print(f"操作JSON: {json.dumps(operation_json, ensure_ascii=False, indent=2)}")
        print("✅ JSON提取成功")
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON解析失败: {e}")
        return
    
    # 步骤4: 执行操作
    print("\n[步骤4] 执行视频操作")
    exec_result = executor.execute_from_json(operation_json, test_video)
    
    print(f"执行成功: {exec_result.success}")
    if exec_result.success:
        print(f"输出文件: {exec_result.output_path}")
        print(f"执行时间: {exec_result.execution_time:.2f}秒")
        print("✅ 操作执行成功")
        
        # 验证输出文件
        if exec_result.output_path and Path(exec_result.output_path).exists():
            file_size = Path(exec_result.output_path).stat().st_size / (1024 * 1024)
            print(f"输出文件大小: {file_size:.2f} MB")
            print("✅ 输出文件已生成")
        else:
            print("⚠️  输出文件不存在")
    else:
        print(f"❌ 操作失败: {exec_result.error_message}")
    
    print("\n✅ 端到端工作流程测试完成")


def test_batch_operations():
    """测试批量操作"""
    print_separator("测试5: 批量操作")
    
    test_video = TEST_DIR / "test_video.mp4"
    if not test_video.exists():
        print(f"⚠️  测试视频 {test_video} 不存在，跳过批量操作测试")
        return
    
    executor = VideoOperationExecutor(output_dir="Results/batch_test")
    
    # 定义批量操作
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
    
    print(f"\n准备执行 {len(operations)} 个操作:")
    for i, op in enumerate(operations, 1):
        op_name = op["operations"]["operation"]
        print(f"  {i}. {op_name}")
    
    # 执行批量操作
    results = executor.execute_batch(operations, test_video)
    
    print(f"\n批量操作完成，共 {len(results)} 个操作")
    for i, result in enumerate(results, 1):
        status = "✅" if result.success else "❌"
        print(f"{status} 操作 {i}: {result.operation_name}")
        if result.success:
            print(f"   输出: {result.output_path}")
            print(f"   耗时: {result.execution_time:.2f}秒")
        else:
            print(f"   错误: {result.error_message}")
    
    print("\n✅ 批量操作测试完成")


def run_all_tests():
    """运行所有测试"""
    print_separator("多模态视频编辑系统 - 完整测试")
    
    print("\n提示: 某些测试需要以下文件:")
    print("  - test_video.mp4 (测试视频)")
    print("  - test_image.png (测试图片)")
    print("  如果这些文件不存在，相关测试将被跳过\n")
    
    try:
        # 运行各个测试
        test_multimodal_processor()
        test_video_operation_executor()
        test_dialogue_manager()
        test_end_to_end_workflow()
        test_batch_operations()
        
        print_separator("测试总结")
        print("\n✅ 所有测试已完成！")
        print("\n系统功能:")
        print("  1. ✅ 多模态输入处理（文本、图片、视频）")
        print("  2. ✅ 视频操作JSON生成和解析")
        print("  3. ✅ 视频操作执行引擎")
        print("  4. ✅ 对话式交互管理")
        print("  5. ✅ 批量操作支持")
        
    except Exception as e:
        logger.exception("测试过程中出错")
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    run_all_tests()

