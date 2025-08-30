#!/usr/bin/env python3
"""
简单的中文字幕测试，避免复杂参数问题
"""

import os
import subprocess
import shlex

def test_simple_chinese_subtitle():
    """测试简单的中文字幕"""
    
    # 测试视频路径
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("开始测试简单中文字幕...")
    
    # 输出路径
    output_path = "Output/test_simple_chinese.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 使用最简单的FFmpeg命令，只添加一个中文字幕
    # 避免复杂的参数组合
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vf', 'drawtext=text=测试:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-text_h-40',
        '-c:a', 'copy',
        output_path
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行FFmpeg命令
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            encoding='utf-8',
            errors='ignore'
        )
        print("✅ 简单中文字幕测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        else:
            print("没有错误输出")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_english_subtitle():
    """测试英文字幕作为对比"""
    
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("\n开始测试英文字幕...")
    
    output_path = "Output/test_english.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 测试英文字幕
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vf', 'drawtext=text=Hello:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-text_h-40',
        '-c:a', 'copy',
        output_path
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            encoding='utf-8',
            errors='ignore'
        )
        print("✅ 英文字幕测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        else:
            print("没有错误输出")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("简单中文字幕测试")
    print("=" * 50)
    
    # 测试简单中文字幕
    success1 = test_simple_chinese_subtitle()
    
    # 测试英文字幕作为对比
    success2 = test_english_subtitle()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ 所有测试通过！")
    elif success2:
        print("⚠️ 英文字幕正常，中文字幕有问题")
        print("可能的原因：")
        print("1. FFmpeg版本不支持中文字体")
        print("2. 系统缺少中文字体支持")
        print("3. 编码问题")
    else:
        print("❌ 所有测试失败")
    print("=" * 50)
