#!/usr/bin/env python3
"""
测试黑白效果功能
"""

import os
import sys
from ffmpeg_editor import FFmpegVideoEditor

def test_black_and_white():
    """测试黑白效果功能"""
    
    # 测试视频路径
    test_video = "uploads/001.mp4"
    
    if not os.path.exists(test_video):
        print(f"测试视频 {test_video} 不存在，请确保有可用的测试视频")
        return
    
    print("开始测试黑白效果功能...")
    
    try:
        # 创建编辑器实例
        editor = FFmpegVideoEditor(test_video)
        print(f"成功加载视频: {test_video}")
        
        # 测试1: 默认参数（从0秒开始，持续1秒）
        print("\n测试1: 默认参数黑白效果")
        editor.make_black_and_white()
        
        # 测试2: 自定义参数（从2秒开始，持续3秒）
        print("\n测试2: 自定义参数黑白效果")
        editor.make_black_and_white(start_time=2.0, duration=3.0)
        
        # 测试3: 前5秒变黑白
        print("\n测试3: 前5秒变黑白")
        editor.make_black_and_white(start_time=0.0, duration=5.0)
        
        # 保存结果
        output_path = "Output/test_black_and_white.mp4"
        editor.output_path = output_path
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n正在保存到: {output_path}")
        editor.save()
        
        print("✅ 黑白效果测试完成！")
        print(f"输出文件: {output_path}")
        
        # 清理资源
        editor.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_execute_action():
    """测试通过execute_action调用黑白效果"""
    
    test_video = "uploads/001.mp4"
    
    if not os.path.exists(test_video):
        print(f"测试视频 {test_video} 不存在")
        return
    
    print("\n开始测试execute_action黑白效果...")
    
    try:
        editor = FFmpegVideoEditor(test_video)
        
        # 测试通过execute_action调用
        action_str = "action: make_black_and_white start_time=1.0 duration=2.0 editor=ffmpeg"
        operations = {}  # 这里不需要实际的operations字典
        
        success = editor.execute_action(action_str, operations)
        
        if success:
            print("✅ execute_action黑白效果测试成功！")
            
            # 保存结果
            output_path = "Output/test_execute_action_bw.mp4"
            editor.output_path = output_path
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            editor.save()
            print(f"输出文件: {output_path}")
        else:
            print("❌ execute_action黑白效果测试失败")
        
        editor.close()
        
    except Exception as e:
        print(f"❌ execute_action测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 50)
    print("黑白效果功能测试")
    print("=" * 50)
    
    # 测试基本功能
    test_black_and_white()
    
    # 测试execute_action接口
    test_execute_action()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
