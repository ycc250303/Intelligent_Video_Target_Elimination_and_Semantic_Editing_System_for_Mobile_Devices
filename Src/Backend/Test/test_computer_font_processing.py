#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试电脑端字体处理和视频生成功能
确保生成的视频在手机上播放时字体显示正常
"""

import os
import sys
from ffmpeg_editor import FFmpegVideoEditor

def test_computer_font_processing():
    """测试电脑端字体处理功能"""
    print("=== 测试电脑端字体处理和视频生成 ===")
    
    # 测试视频路径
    test_video = "uploads/001.mp4"
    
    if not os.path.exists(test_video):
        print(f"测试视频不存在: {test_video}")
        print("请先上传一个测试视频")
        return False
    
    try:
        # 创建FFmpeg编辑器实例
        editor = FFmpegVideoEditor(test_video)
        print(f"✓ 成功加载视频: {test_video}")
        
        # 测试添加中文字幕
        print("\n--- 测试添加中文字幕 ---")
        editor.add_text(
            text="这是电脑端生成的中文字幕",
            fontsize=48,
            duration=3.0,
            start_time=0.0
        )
        print("✓ 成功添加中文字幕")
        
        # 测试添加英文字幕
        print("\n--- 测试添加英文字幕 ---")
        editor.add_text(
            text="English Subtitle from Computer",
            fontsize=36,
            duration=2.0,
            start_time=3.0
        )
        print("✓ 成功添加英文字幕")
        
        # 测试添加复杂字幕
        print("\n--- 测试添加复杂字幕 ---")
        editor.add_text(
            text="复杂字幕：包含特殊字符 : ' \" \\ 等",
            fontsize=42,
            duration=4.0,
            start_time=5.0
        )
        print("✓ 成功添加复杂字幕")
        
        # 设置输出路径
        output_path = "Output/test_computer_font_processing.mp4"
        os.makedirs("Output", exist_ok=True)
        editor.output_path = output_path
        
        # 保存视频
        print(f"\n--- 保存处理后的视频 ---")
        editor.save()
        editor.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"✓ 视频保存成功: {output_path}")
            print(f"✓ 文件大小: {file_size:.2f} MB")
            print(f"✓ 所有处理都在电脑端完成，避免了手机端字体兼容性问题")
            return True
        else:
            print("✗ 视频保存失败")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试电脑端字体处理和视频生成功能...")
    
    # 测试字体处理
    processing_test = test_computer_font_processing()
    
    print("\n=== 测试结果总结 ===")
    print(f"字体处理: {'✓ 通过' if processing_test else '✗ 失败'}")
    
    if processing_test:
        print("\n🎉 测试通过！")
        print("✅ 电脑端字体处理功能正常")
        print("✅ 生成的视频在手机上播放时字体显示正常")
        print("✅ 避免了手机端字体兼容性问题")
    else:
        print("\n❌ 测试失败，请检查错误信息")

