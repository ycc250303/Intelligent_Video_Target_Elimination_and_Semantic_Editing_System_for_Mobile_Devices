#!/usr/bin/env python3
"""
测试动态编辑器切换功能
"""

import os
import sys
from video_editor import DialogueVideoEditor

def test_dynamic_editor_switching():
    """
    测试动态编辑器切换功能
    """
    print("=== 测试动态编辑器切换功能 ===")
    
    # 测试视频文件路径
    input_video = "D:\\test1\\video001.mp4"
    
    # 检查视频文件是否存在
    if not os.path.exists(input_video):
        print(f"❌ 测试视频文件不存在: {input_video}")
        print("请确保测试视频文件存在")
        return
    
    # 创建视频编辑器实例
    editor = DialogueVideoEditor(input_video, editor_type='moviepy')
    
    # 测试命令序列 - 这些命令应该会触发不同的编辑器
    test_commands = [
        {
            "command": "增大视频对比度",
            "expected_editor": "moviepy",
            "description": "对比度调整 - 应该使用 moviepy"
        },
        {
            "command": "在视频第一秒添加一个转场",
            "expected_editor": "moviepy", 
            "description": "转场效果 - 应该使用 moviepy"
        },
        {
            "command": "第一秒变为黑白",
            "expected_editor": "ffmpeg",
            "description": "黑白效果 - 应该使用 ffmpeg"
        },
        {
            "command": "添加字幕'测试字幕'", 
            "expected_editor": "ffmpeg",
            "description": "字幕添加 - 应该使用 ffmpeg"
        }
    ]
    
    print(f"开始测试，输入视频: {input_video}")
    print()
    
    for i, test_case in enumerate(test_commands, 1):
        print(f"测试 {i}: {test_case['description']}")
        print(f"命令: {test_case['command']}")
        print(f"期望编辑器: {test_case['expected_editor']}")
        
        try:
            result = editor.process_command(test_case['command'])
            
            print(f"执行结果: {result['success']}")
            print(f"响应: {result['response']}")
            print(f"操作: {result['action']}")
            
            # 检查是否使用了正确的编辑器
            if result['success'] and result['action']:
                action_parts = result['action'].split()
                actual_editor = None
                for part in action_parts:
                    if part.startswith('editor='):
                        actual_editor = part.split('=')[1]
                        break
                
                if actual_editor == test_case['expected_editor']:
                    print(f"✅ 编辑器选择正确: {actual_editor}")
                else:
                    print(f"❌ 编辑器选择错误: 期望 {test_case['expected_editor']}, 实际 {actual_editor}")
            else:
                print("❌ 操作执行失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print("-" * 50)
    
    # 保存最终结果
    try:
        output_dir = "Output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_path = os.path.join(output_dir, "dynamic_editor_test.mp4")
        editor.save_final(output_path)
        print(f"✅ 测试视频已保存: {output_path}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
    
    # 清理资源
    editor.close()
    print("测试完成")

if __name__ == "__main__":
    test_dynamic_editor_switching()
