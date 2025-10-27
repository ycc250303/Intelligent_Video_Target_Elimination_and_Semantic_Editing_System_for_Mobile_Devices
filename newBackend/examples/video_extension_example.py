#!/usr/bin/env python3
"""
视频延展功能使用示例

演示如何使用 extend_video 功能将短视频延长到 5 秒
"""

import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from VideoEditor.qwen_editor import QwenVideoEditor
from config import QWEN_API_KEY

def example_extend_video_basic():
    """
    基础示例：使用公网视频 URL 进行延展
    """
    print("=" * 70)
    print("示例 1：基础视频延展（使用公网 URL）")
    print("=" * 70)
    
    # 初始化编辑器
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")
    
    # 使用公网视频 URL（示例来自官方文档）
    video_url = "http://wanx.alicdn.com/material/20250318/video_extension_1.mp4"
    prompt = "一只戴着墨镜的狗在街道上滑滑板，3D卡通。"
    
    print(f"📹 输入视频: {video_url}")
    print(f"💬 提示词: {prompt}")
    print(f"⚙️  智能改写: 关闭（推荐）\n")
    
    # 调用视频延展功能
    result = editor.extend_video(
        prompt=prompt,
        first_clip_url=video_url,
        prompt_extend=False  # 关闭智能改写（推荐）
    )
    
    if result:
        print(f"\n✅ 视频延展成功！")
        print(f"📁 生成文件: {result}")
        print(f"🎥 视频时长: 5 秒（固定）")
    else:
        print("\n❌ 视频延展失败")
    
    print("\n" + "=" * 70)


def example_extend_video_with_prompt_extend():
    """
    高级示例：开启智能改写
    """
    print("\n示例 2：开启 Prompt 智能改写")
    print("=" * 70)
    
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")
    
    video_url = "http://wanx.alicdn.com/material/20250318/video_extension_1.mp4"
    prompt = "狗滑滑板"  # 简短的 prompt
    
    print(f"📹 输入视频: {video_url}")
    print(f"💬 提示词: {prompt}（简短版）")
    print(f"⚙️  智能改写: 开启（会增加耗时）\n")
    
    result = editor.extend_video(
        prompt=prompt,
        first_clip_url=video_url,
        prompt_extend=True  # 开启智能改写
    )
    
    if result:
        print(f"\n✅ 视频延展成功！")
        print(f"📁 生成文件: {result}")
        print(f"💡 提示: 智能改写可以将简短的 prompt 扩展为更详细的描述")
    else:
        print("\n❌ 视频延展失败")
    
    print("\n" + "=" * 70)


def example_local_file_error():
    """
    错误示例：使用本地文件路径（会失败）
    """
    print("\n示例 3：本地文件路径（演示错误处理）")
    print("=" * 70)
    
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")
    
    # 尝试使用本地文件路径（会失败）
    local_video = "C:/videos/test.mp4"
    prompt = "继续视频内容"
    
    print(f"📹 输入视频: {local_video}（本地文件路径）")
    print(f"💬 提示词: {prompt}\n")
    
    result = editor.extend_video(
        prompt=prompt,
        first_clip_url=local_video,
        prompt_extend=False
    )
    
    if result:
        print(f"\n✅ 视频延展成功！")
        print(f"📁 生成文件: {result}")
    else:
        print("\n❌ 视频延展失败（预期结果）")
        print("💡 提示: 视频延展功能要求使用公网可访问的 HTTP/HTTPS URL")
        print("   请将视频上传到云存储服务（如阿里云 OSS、腾讯云 COS）获取 URL")
    
    print("\n" + "=" * 70)


def example_using_json():
    """
    通过 JSON 配置使用视频延展功能
    """
    print("\n示例 4：通过 JSON 配置使用（与系统集成）")
    print("=" * 70)
    
    from core.video_operation_executor import VideoOperationExecutor
    
    # 创建执行器
    executor = VideoOperationExecutor(output_dir="Results")
    
    # JSON 配置
    operation_json = {
        "operations": {
            "operation": "extend_video",
            "params": {
                "prompt": "一只戴着墨镜的狗在街道上滑滑板，3D卡通。",
                "first_clip_url": "http://wanx.alicdn.com/material/20250318/video_extension_1.mp4",
                "prompt_extend": False
            },
            "editor": "qwen"
        }
    }
    
    print("📄 JSON 配置:")
    import json
    print(json.dumps(operation_json, indent=2, ensure_ascii=False))
    print()
    
    # 执行操作
    result = executor.execute_from_json(operation_json)
    
    if result.success:
        print(f"\n✅ 视频延展成功！")
        print(f"📁 生成文件: {result.output_path}")
        print(f"⏱️  执行时间: {result.execution_time:.2f} 秒")
    else:
        print(f"\n❌ 视频延展失败")
        print(f"❌ 错误信息: {result.error_message}")
    
    print("\n" + "=" * 70)


def show_usage_tips():
    """
    显示使用提示
    """
    print("\n" + "=" * 70)
    print("📚 视频延展功能使用提示")
    print("=" * 70)
    print("""
1. 🌐 视频 URL 要求
   - 必须是公网可访问的 HTTP/HTTPS URL
   - 不支持本地文件路径
   - 建议上传到云存储服务获取 URL

2. 📹 视频格式要求
   - 格式: MP4
   - 帧率: ≥ 16 FPS
   - 大小: ≤ 50 MB
   - 长度: ≤ 3 秒（超过取前 3 秒）

3. ⏱️  输出时长
   - 固定 5 秒（这是最终输出视频的完整时长）

4. 💬 Prompt 建议
   - 详细描述期望的延展内容
   - 保持与输入视频内容一致
   - 通常不建议开启智能改写（除非 prompt 非常简短）

5. 🚀 云存储服务推荐
   - 阿里云 OSS
   - 腾讯云 COS
   - 七牛云 Kodo
   - AWS S3

6. 📖 详细文档
   - 查看 docs/VIDEO_EXTENSION_GUIDE.md
   - 包含完整的参数说明、使用场景、错误处理等
    """)
    print("=" * 70)


def main():
    """
    主函数
    """
    print("\n🎬 视频延展功能使用示例\n")
    print("本示例演示如何使用 extend_video 功能将短视频延长到 5 秒")
    print("注意: 需要有效的 Qwen API Key 和公网视频 URL\n")
    
    # 检查 API Key
    if not QWEN_API_KEY or QWEN_API_KEY == "your-api-key-here":
        print("⚠️  警告: 请先在 config/config.py 中配置有效的 QWEN_API_KEY")
        print("示例将继续运行，但实际 API 调用可能失败\n")
    
    # 显示使用提示
    show_usage_tips()
    
    print("\n" + "=" * 70)
    print("选择要运行的示例:")
    print("=" * 70)
    print("1. 基础视频延展（推荐）")
    print("2. 开启智能改写")
    print("3. 错误处理演示（本地文件路径）")
    print("4. JSON 配置方式（系统集成）")
    print("5. 运行所有示例")
    print("0. 退出")
    print("=" * 70)
    
    try:
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == "1":
            example_extend_video_basic()
        elif choice == "2":
            example_extend_video_with_prompt_extend()
        elif choice == "3":
            example_local_file_error()
        elif choice == "4":
            example_using_json()
        elif choice == "5":
            # 运行所有示例（但跳过实际 API 调用以节省配额）
            print("\n⚠️  运行所有示例仅显示代码和说明，不进行实际 API 调用")
            print("如需测试实际功能，请单独运行示例 1 或 2\n")
            
            example_local_file_error()  # 这个不会调用 API
            # example_extend_video_basic()
            # example_extend_video_with_prompt_extend()
            # example_using_json()
        elif choice == "0":
            print("\n👋 退出示例")
        else:
            print("\n❌ 无效的选项")
    
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出示例")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()


