#!/usr/bin/env python3
"""
简单测试黑白效果功能
"""

import os
import subprocess
import shlex

def test_ffmpeg_black_and_white():
    """测试FFmpeg黑白效果命令"""
    
    # 测试视频路径
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("开始测试FFmpeg黑白效果...")
    
    # 输出路径
    output_path = "Output/test_bw_simple.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # FFmpeg命令：将前1秒变为黑白
    cmd = f'ffmpeg -y -i "{input_video}" -vf "hue=s=0:enable=between(t,0,1)" -c:a copy "{output_path}"'
    
    print(f"执行命令: {cmd}")
    
    try:
        # 执行FFmpeg命令
        result = subprocess.run(shlex.split(cmd), check=True, capture_output=True, text=True)
        print("✅ FFmpeg黑白效果测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_ffmpeg_black_and_white_custom():
    """测试自定义时间的黑白效果"""
    
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("\n开始测试自定义时间黑白效果...")
    
    output_path = "Output/test_bw_custom.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # FFmpeg命令：从第2秒开始，持续3秒变为黑白
    cmd = f'ffmpeg -y -i "{input_video}" -vf "hue=s=0:enable=between(t,2,5)" -c:a copy "{output_path}"'
    
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(shlex.split(cmd), check=True, capture_output=True, text=True)
        print("✅ 自定义时间黑白效果测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("FFmpeg黑白效果简单测试")
    print("=" * 50)
    
    # 测试基本黑白效果
    success1 = test_ffmpeg_black_and_white()
    
    # 测试自定义时间黑白效果
    success2 = test_ffmpeg_black_and_white_custom()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 50)
