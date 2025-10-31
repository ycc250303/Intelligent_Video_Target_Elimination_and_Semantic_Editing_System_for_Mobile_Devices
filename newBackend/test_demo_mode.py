"""
测试Demo模式配置
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置UTF-8编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from config.demo_config import get_demo_video_path, is_demo_mode_enabled, DEMO_VIDEO_DIR

def test_demo_mode():
    """测试demo模式功能"""
    
    print("=" * 60)
    print("测试Demo模式配置")
    print("=" * 60)
    
    # 检查demo模式是否启用
    enabled = "已启用" if is_demo_mode_enabled() else "未启用"
    print(f"\n1. Demo模式状态: {enabled}")
    
    # 检查demo视频目录
    print(f"\n2. Demo视频目录: {DEMO_VIDEO_DIR}")
    exists_text = "OK" if DEMO_VIDEO_DIR.exists() else "NOT FOUND"
    print(f"   目录存在: {exists_text}")
    
    if DEMO_VIDEO_DIR.exists():
        video_files = list(DEMO_VIDEO_DIR.glob("*.mp4"))
        print(f"   视频文件数量: {len(video_files)}")
        for video in sorted(video_files):
            print(f"      - {video.name}")
    
    # 测试各个指令
    print("\n3. 测试指令匹配:")
    test_instructions = [
        "为开头风景添加撕纸特效",
        "给视频开头添加标题'天山牧歌'，字体可爱一点",
        "给视频开头添加标题'天山牧歌'",
        "给视频开头添加贴纸动画",
        "将第二个画面的人物抠出来添加于开头视频左下角，给人物描一个白边",
        "将第二个画面的人物抠出来添加于开头视频左下角",
        "结合视频风格和转场添加一个背景纯音乐",
        # 测试模糊匹配
        "帮我添加一个撕纸效果",
        "添加标题天山牧歌",
        "给视频添加贴纸",
        "抠出人物并添加白边",
        "添加背景音乐"
    ]
    
    for instruction in test_instructions:
        video_path, description = get_demo_video_path(instruction)
        if video_path:
            video_name = Path(video_path).name
            exists = Path(video_path).exists()
            status = "[OK]" if exists else "[FAIL]"
            print(f"\n   指令: \"{instruction}\"")
            print(f"   {status} 匹配到: {video_name}")
            print(f"      描述: {description}")
            if not exists:
                print(f"      警告: 文件不存在: {video_path}")
        else:
            print(f"\n   指令: \"{instruction}\"")
            print(f"   [FAIL] 未匹配")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_demo_mode()

