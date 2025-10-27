#!/usr/bin/env python3
"""
多模态视频工具演示脚本
展示如何使用 multimodal_video_tool.py 进行视频编辑和生成
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multimodal_video_tool import MultimodalVideoTool


def demo_1_edit_video():
    """演示1: 编辑现有视频"""
    print("\n" + "="*70)
    print("📹 演示1: 编辑现有视频 (FFmpeg)")
    print("="*70)
    
    tool = MultimodalVideoTool(output_dir="Results/demo")
    
    # 检查测试视频是否存在
    test_video = "tests/test_video.mp4"
    if not Path(test_video).exists():
        test_video = "test_video.mp4"
        if not Path(test_video).exists():
            print(f"⚠️  测试视频不存在，跳过此演示")
            print(f"   请准备一个名为 test_video.mp4 的视频文件")
            return
    
    print(f"\n使用测试视频: {test_video}")
    
    # 示例 1: 裁剪视频
    print("\n--- 示例 1.1: 裁剪视频 ---")
    result1 = tool.process(
        text="剪掉前3秒",
        video_path=test_video
    )
    
    # 示例 2: 调整速度
    print("\n--- 示例 1.2: 调整速度 ---")
    result2 = tool.process(
        text="加速2倍播放",
        video_path=test_video
    )
    
    # 示例 3: 添加字幕
    print("\n--- 示例 1.3: 添加字幕 ---")
    result3 = tool.process(
        text="在第1秒添加字幕'Hello World'",
        video_path=test_video
    )
    
    print("\n✅ 演示1完成")


def demo_2_generate_from_text():
    """演示2: 文本生成视频"""
    print("\n" + "="*70)
    print("✍️  演示2: 文本生成视频 (Qwen)")
    print("="*70)
    
    tool = MultimodalVideoTool(output_dir="Results/demo")
    
    # 示例 1: 生成自然场景
    print("\n--- 示例 2.1: 生成自然场景 ---")
    result1 = tool.process(
        text="生成一段海边日落的视频，波浪拍打沙滩，天空橙红色"
    )
    
    # 示例 2: 生成城市场景
    print("\n--- 示例 2.2: 生成城市场景 ---")
    result2 = tool.process(
        text="城市夜景，车流穿梭，霓虹灯闪烁"
    )
    
    print("\n✅ 演示2完成")


def demo_3_generate_from_image():
    """演示3: 图片生成视频"""
    print("\n" + "="*70)
    print("🖼️  演示3: 图片生成视频 (Qwen)")
    print("="*70)
    
    tool = MultimodalVideoTool(output_dir="Results/demo")
    
    # 检查测试图片是否存在
    test_image = "tests/test_image.png"
    if not Path(test_image).exists():
        test_image = "test_image.png"
        if not Path(test_image).exists():
            print(f"⚠️  测试图片不存在，跳过此演示")
            print(f"   请准备一个名为 test_image.png 的图片文件")
            return
    
    print(f"\n使用测试图片: {test_image}")
    
    # 示例 1: 添加动态效果
    print("\n--- 示例 3.1: 添加动态效果 ---")
    result1 = tool.process(
        text="让这张图片动起来",
        image_path=test_image
    )
    
    # 示例 2: 根据图片生成故事
    print("\n--- 示例 3.2: 根据图片生成视频 ---")
    result2 = tool.process(
        text="基于这张图片生成一段5秒的视频，添加镜头推进效果",
        image_path=test_image
    )
    
    print("\n✅ 演示3完成")


def demo_4_batch_processing():
    """演示4: 批量处理"""
    print("\n" + "="*70)
    print("📦 演示4: 批量处理多个任务")
    print("="*70)
    
    tool = MultimodalVideoTool(output_dir="Results/demo")
    
    # 准备任务列表
    tasks = [
        {
            "text": "生成一段森林小径的视频，阳光透过树叶",
            "auto_execute": True
        },
        {
            "text": "生成一段雨天街景的视频，雨滴打在地面",
            "auto_execute": True
        }
    ]
    
    # 如果有测试视频，添加编辑任务
    test_video = "tests/test_video.mp4"
    if Path(test_video).exists():
        tasks.append({
            "text": "剪掉前2秒并调整音量为1.5倍",
            "video_path": test_video,
            "auto_execute": True
        })
    
    print(f"\n准备处理 {len(tasks)} 个任务")
    
    results = tool.batch_process(tasks, verbose=False)
    
    print("\n✅ 演示4完成")


def demo_5_only_parse():
    """演示5: 仅解析不执行"""
    print("\n" + "="*70)
    print("🔍 演示5: 仅生成操作 JSON，不执行")
    print("="*70)
    
    tool = MultimodalVideoTool(output_dir="Results/demo")
    
    # 示例: 只解析指令，查看生成的 JSON
    print("\n--- 解析指令但不执行 ---")
    result = tool.process(
        text="剪掉前5秒，然后加速2倍，最后添加字幕",
        video_path="dummy.mp4",  # 假设的路径
        auto_execute=False  # 不执行
    )
    
    if result.get('success'):
        print("\n生成的操作 JSON 可以保存下来，稍后执行")
    
    print("\n✅ 演示5完成")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎬 多模态视频工具 - 完整演示")
    print("="*70)
    print("\n本演示将展示工具的各种使用方式")
    print("\n提示: 某些演示需要测试文件 (test_video.mp4, test_image.png)")
    print("      如果文件不存在，相关演示将被跳过")
    
    input("\n按 Enter 开始演示...")
    
    try:
        # 运行所有演示
        #demo_1_edit_video()
        #input("\n按 Enter 继续下一个演示...")
        
        #demo_2_generate_from_text()
        #input("\n按 Enter 继续下一个演示...")
        
        demo_3_generate_from_image()
        input("\n按 Enter 继续下一个演示...")
        
        demo_4_batch_processing()
        input("\n按 Enter 继续下一个演示...")
        
        demo_5_only_parse()
        
        print("\n" + "="*70)
        print("🎉 所有演示完成!")
        print("="*70)
        print("\n生成的文件在: Results/demo/")
        print("\n更多使用方法，请参考:")
        print("  - USER_GUIDE.md (完整使用指南)")
        print("  - QUICK_REFERENCE.md (快速参考)")
        
    except KeyboardInterrupt:
        print("\n\n⏸️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

