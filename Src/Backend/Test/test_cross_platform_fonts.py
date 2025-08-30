#!/usr/bin/env python3
"""
跨平台字体检测测试
帮助诊断电脑和手机端的字体问题
"""

import os
import platform
import subprocess
import shlex

def detect_system_info():
    """检测系统信息"""
    print("=" * 50)
    print("系统信息检测")
    print("=" * 50)
    
    print(f"操作系统: {platform.system()}")
    print(f"系统版本: {platform.version()}")
    print(f"机器类型: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    print(f"Python版本: {platform.python_version()}")
    
    # 检测是否为移动设备
    if platform.system() == "Linux":
        # 检查是否为Android
        if os.path.exists("/system"):
            print("检测到Android系统")
        elif os.path.exists("/usr/share/fonts"):
            print("检测到Linux桌面系统")
    elif platform.system() == "Darwin":
        if os.path.exists("/System/Library/Fonts"):
            print("检测到macOS/iOS系统")

def check_fonts_by_platform():
    """根据平台检查字体"""
    print("\n" + "=" * 50)
    print("字体检测")
    print("=" * 50)
    
    font_candidates = []
    
    if os.name == 'nt':  # Windows
        print("Windows系统字体检测:")
        font_candidates = [
            r"C:\Windows\Fonts\msyh.ttc",      # 微软雅黑
            r"C:\Windows\Fonts\msyhbd.ttc",    # 微软雅黑粗体
            r"C:\Windows\Fonts\simhei.ttf",    # 黑体
            r"C:\Windows\Fonts\simsun.ttc",    # 宋体
        ]
    elif platform.system() == "Linux":
        if os.path.exists("/system"):  # Android
            print("Android系统字体检测:")
            font_candidates = [
                "/system/fonts/DroidSansFallback.ttf",
                "/system/fonts/NotoSansCJK-Regular.ttc",
                "/system/fonts/Roboto-Regular.ttf",
            ]
        else:  # Linux桌面
            print("Linux桌面系统字体检测:")
            font_candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
    elif platform.system() == "Darwin":  # macOS/iOS
        print("macOS/iOS系统字体检测:")
        font_candidates = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    
    # 检查字体文件
    available_fonts = []
    for font_path in font_candidates:
        if os.path.exists(font_path):
            available_fonts.append(font_path)
            print(f"✅ 可用字体: {font_path}")
        else:
            print(f"❌ 字体不存在: {font_path}")
    
    return available_fonts

def test_ffmpeg_font_support():
    """测试FFmpeg字体支持"""
    print("\n" + "=" * 50)
    print("FFmpeg字体支持检测")
    print("=" * 50)
    
    try:
        # 检查FFmpeg版本
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("✅ FFmpeg可用")
            # 检查是否支持字体功能
            if "drawtext" in result.stdout or "font" in result.stdout:
                print("✅ 支持drawtext过滤器")
            else:
                print("⚠️ 可能不支持drawtext过滤器")
        else:
            print("❌ FFmpeg不可用")
            return False
            
    except FileNotFoundError:
        print("❌ 未找到FFmpeg，请确保已安装")
        return False
    except Exception as e:
        print(f"❌ FFmpeg检测失败: {e}")
        return False
    
    return True

def test_simple_subtitle():
    """测试简单字幕功能"""
    print("\n" + "=" * 50)
    print("简单字幕功能测试")
    print("=" * 50)
    
    # 检查测试视频
    test_video = "uploads/001.mp4"
    if not os.path.exists(test_video):
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    # 输出路径
    output_path = "Output/test_cross_platform.mp4"
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 测试命令（不指定字体文件）
    cmd = [
        'ffmpeg', '-y',
        '-i', test_video,
        '-vf', 'drawtext=text=测试字幕:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-text_h-40:borderw=2:bordercolor=black',
        '-c:a', 'copy',
        output_path
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("✅ 字幕测试成功！")
            print(f"输出文件: {output_path}")
            return True
        else:
            print(f"❌ 字幕测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return False

def generate_font_solution():
    """生成字体解决方案建议"""
    print("\n" + "=" * 50)
    print("字体问题解决方案建议")
    print("=" * 50)
    
    system = platform.system()
    
    if system == "Windows":
        print("Windows系统:")
        print("1. 确保安装了微软雅黑字体")
        print("2. 检查字体文件是否完整")
        print("3. 使用系统默认字体作为备选")
        
    elif system == "Linux":
        if os.path.exists("/system"):
            print("Android系统:")
            print("1. 安装支持中文的字体应用")
            print("2. 使用系统内置的Droid字体")
            print("3. 考虑使用Noto字体")
            print("4. 在FFmpeg编译时包含字体支持")
        else:
            print("Linux桌面系统:")
            print("1. 安装中文字体包: sudo apt-get install fonts-noto-cjk")
            print("2. 使用系统字体管理器安装字体")
            print("3. 确保FFmpeg支持字体功能")
            
    elif system == "Darwin":
        print("macOS/iOS系统:")
        print("1. 使用系统内置的PingFang字体")
        print("2. 确保字体文件权限正确")
        print("3. 考虑使用通用字体名称")

if __name__ == "__main__":
    print("跨平台字体检测和诊断工具")
    
    # 系统信息检测
    detect_system_info()
    
    # 字体检测
    available_fonts = check_fonts_by_platform()
    
    # FFmpeg支持检测
    ffmpeg_ok = test_ffmpeg_font_support()
    
    # 简单字幕测试
    if ffmpeg_ok:
        subtitle_ok = test_simple_subtitle()
    else:
        subtitle_ok = False
    
    # 生成解决方案
    generate_font_solution()
    
    print("\n" + "=" * 50)
    print("检测结果总结")
    print("=" * 50)
    
    if available_fonts:
        print(f"✅ 找到 {len(available_fonts)} 个可用字体")
    else:
        print("❌ 未找到可用字体")
    
    if ffmpeg_ok:
        print("✅ FFmpeg可用")
    else:
        print("❌ FFmpeg不可用")
    
    if subtitle_ok:
        print("✅ 字幕功能正常")
    else:
        print("❌ 字幕功能异常")
    
    print("=" * 50)

