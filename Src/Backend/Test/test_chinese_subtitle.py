#!/usr/bin/env python3
"""
测试中文字幕功能，验证乱码问题是否解决
"""

import os
import subprocess
import shlex

def test_chinese_subtitle():
    """测试中文字幕功能"""
    
    # 测试视频路径
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("开始测试中文字幕功能...")
    
    # 输出路径
    output_path = "Output/test_chinese_subtitle.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 测试中文字幕
    chinese_text = "测试中文字幕"
    
    # 使用微软雅黑字体（如果存在）
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    if os.path.exists(font_path):
        font_path_ff = font_path.replace("\\", "/")
        font_param = f"fontfile='{font_path_ff}':"
        print(f"使用字体: {font_path}")
    else:
        font_param = ""
        print("使用默认字体")
    
    # FFmpeg命令：添加中文字幕
    cmd = f'ffmpeg -y -i "{input_video}" -vf "{font_param}drawtext=text=\'{chinese_text}\':fontsize=48:fontcolor=white:borderw=2:bordercolor=black@0.7:x=(w-text_w)/2:y=h-text_h-40:enable=between(t,0,5)" -c:a copy "{output_path}"'
    
    print(f"执行命令: {cmd}")
    
    try:
        # 执行FFmpeg命令，设置编码为utf-8，避免中文解码错误
        result = subprocess.run(
            shlex.split(cmd), 
            check=True, 
            capture_output=True, 
            encoding='utf-8',
            errors='ignore'  # 忽略无法解码的字符
        )
        print("✅ 中文字幕测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        else:
            print("没有错误输出，可能是编码问题")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_multiple_chinese_subtitles():
    """测试多个中文字幕"""
    
    input_video = "uploads/001.mp4"
    
    if not os.path.exists(input_video):
        print(f"测试视频 {input_video} 不存在")
        return False
    
    print("\n开始测试多个中文字幕...")
    
    output_path = "Output/test_multiple_chinese_subtitles.mp4"
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 使用微软雅黑字体
    font_path = r"C:\Windows\Fonts\msyh.ttc"
    if os.path.exists(font_path):
        font_path_ff = font_path.replace("\\", "/")
        font_param = f"fontfile='{font_path_ff}':"
    else:
        font_param = ""
    
    # 多个中文字幕
    subtitle1 = "第一个中文字幕"
    subtitle2 = "第二个中文字幕"
    subtitle3 = "第三个中文字幕"
    
    # 复杂的FFmpeg命令，包含多个字幕
    vf_filter = f"{font_param}drawtext=text='{subtitle1}':fontsize=36:fontcolor=white:borderw=2:bordercolor=black@0.7:x=(w-text_w)/2:y=h-text_h-40:enable=between(t,0,2),{font_param}drawtext=text='{subtitle2}':fontsize=36:fontcolor=white:borderw=2:bordercolor=black@0.7:x=(w-text_w)/2:y=h-text_h-40:enable=between(t,2,4),{font_param}drawtext=text='{subtitle3}':fontsize=36:fontcolor=white:borderw=2:bordercolor=black@0.7:x=(w-text_w)/2:y=h-text_h-40:enable=between(t,4,6)"
    
    cmd = f'ffmpeg -y -i "{input_video}" -vf "{vf_filter}" -c:a copy "{output_path}"'
    
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(
            shlex.split(cmd), 
            check=True, 
            capture_output=True, 
            encoding='utf-8',
            errors='ignore'
        )
        print("✅ 多个中文字幕测试成功！")
        print(f"输出文件: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg执行失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        else:
            print("没有错误输出，可能是编码问题")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_fonts():
    """检查可用的字体文件"""
    print("\n检查可用的字体文件...")
    
    font_candidates = [
        r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
        r"C:\Windows\Fonts\msyhbd.ttc",    # 微软雅黑粗体
        r"C:\Windows\Fonts\simhei.ttf",    # 黑体
        r"C:\Windows\Fonts\simsun.ttc",    # 宋体
        r"C:\Windows\Fonts\simkai.ttf",    # 楷体
        r"C:\Windows\Fonts\simfang.ttf",   # 仿宋
        r"C:\Windows\Fonts\arial.ttf",     # Arial
    ]
    
    available_fonts = []
    for font_path in font_candidates:
        if os.path.exists(font_path):
            available_fonts.append(font_path)
            print(f"✅ 可用字体: {font_path}")
        else:
            print(f"❌ 字体不存在: {font_path}")
    
    return available_fonts

if __name__ == "__main__":
    print("=" * 50)
    print("中文字幕功能测试")
    print("=" * 50)
    
    # 检查字体
    available_fonts = check_fonts()
    
    if not available_fonts:
        print("❌ 没有找到可用的字体文件！")
        exit(1)
    
    # 测试基本中文字幕
    success1 = test_chinese_subtitle()
    
    # 测试多个中文字幕
    success2 = test_multiple_chinese_subtitles()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ 所有中文字幕测试通过！")
        print("如果仍有乱码，请检查：")
        print("1. 字体文件是否正确安装")
        print("2. FFmpeg版本是否支持中文字体")
        print("3. 系统编码设置")
    else:
        print("❌ 部分测试失败")

    print("=" * 50)
