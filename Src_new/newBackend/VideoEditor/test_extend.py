"""
视频延展功能测试脚本
使用本地视频文件自动上传到OSS并进行延展
"""
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from VideoEditor.qwen_editor import QwenVideoEditor
from config.config import QWEN_API_KEY

def test_extend_video():
    """测试视频延展功能"""
    print("=" * 60)
    print("视频延展功能测试")
    print("=" * 60)
    print()
    
    # 初始化编辑器
    editor = QwenVideoEditor(api_key=QWEN_API_KEY, base_dir="Results")
    
    # 测试视频路径（本地文件会自动上传）
    video_path = r"Results\make_video_from_first_frame_001.mp4"
    
    # 检查文件是否存在
    if not os.path.exists(video_path):
        print(f"错误: 测试视频不存在: {video_path}")
        print("\n请先生成测试视频：")
        print("  python qwen_editor.py  # 设置 test_mode = 1")
        return
    
    # 延展提示词
    prompt = "延续视频内容，保持流畅的动作连贯性"
    
    print(f"输入视频: {video_path}")
    print(f"提示词: {prompt}")
    print()
    print("-" * 60)
    print()
    
    # 执行视频延展
    result = editor.extend_video(
        prompt=prompt,
        first_clip_url=video_path,
        prompt_extend=False
    )
    
    # 输出结果
    print()
    print("=" * 60)
    if result:
        print("✓ 测试成功！")
        print(f"延展后的视频: {result}")
        print(f"视频时长: 5秒")
    else:
        print("✗ 测试失败")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_extend_video()
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()

