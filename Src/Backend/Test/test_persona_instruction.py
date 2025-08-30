#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试"应用persona"复合指令
验证四个操作步骤是否正确生成
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_persona_instruction():
    """测试应用persona指令"""
    
    try:
        from Src.Backend.Unused.enhanced_nlp_parser import SmartVideoEditor
        
        print("=== 测试'应用persona'复合指令 ===\n")
        
        # 创建智能视频编辑器实例
        editor = SmartVideoEditor()
        
        # 模拟视频上下文
        video_context = {
            'duration': 30.0,
            'resolution': (1920, 1080),
            'fps': 30,
            'format': 'mp4'
        }
        
        # 测试各种表达方式
        test_instructions = [
            "应用persona",
            "使用persona",
            "应用风格",
            "使用风格",
            "应用预设",
            "使用预设"
        ]
        
        print("测试各种表达方式：\n")
        
        for instruction in test_instructions:
            print(f"输入: {instruction}")
            
            # 处理指令
            result = editor.process_instruction(instruction, video_context)
            
            if result['success']:
                print(f"  ✓ 成功解析")
                print(f"  操作: {result['action']}")
                print(f"  说明: {result['explanation']}")
                
                if result.get('is_composite', False):
                    print(f"  类型: 复合指令")
                    print(f"  包含操作:")
                    for i, action in enumerate(result.get('composite_actions', []), 1):
                        print(f"    {i}. {action}")
                    
                    # 验证操作步骤
                    composite_actions = result.get('composite_actions', [])
                    if len(composite_actions) == 4:
                        print(f"  ✓ 包含4个操作步骤")
                        
                        # 验证具体操作
                        expected_actions = [
                            'action: adjust_contrast factor=1.3 editor=moviepy',
                            'action: make_black_and_white start_time=0.0 duration=1.0 editor=ffmpeg',
                            'action: add_transition type=fade duration=1.0 start_time=0.0 editor=ffmpeg',
                            'action: add_text text=智能字幕 duration=3.0 start_time=1.0 editor=ffmpeg'
                        ]
                        
                        for i, (expected, actual) in enumerate(zip(expected_actions, composite_actions), 1):
                            if expected == actual:
                                print(f"    ✓ 步骤{i}正确: {actual}")
                            else:
                                print(f"    ✗ 步骤{i}不匹配:")
                                print(f"      期望: {expected}")
                                print(f"      实际: {actual}")
                    else:
                        print(f"  ✗ 操作步骤数量不正确，期望4个，实际{len(composite_actions)}个")
                else:
                    print(f"  ✗ 不是复合指令")
                
                if result['suggestions']:
                    print(f"  建议: {', '.join(result['suggestions'])}")
            else:
                print(f"  ✗ 解析失败")
                print(f"  说明: {result['explanation']}")
            
            print()
        
        # 测试操作历史
        print("=== 操作历史 ===")
        history = editor.get_history()
        for i, record in enumerate(history, 1):
            print(f"{i}. 输入: {record['input']}")
            print(f"   操作: {record['action']}")
            if 'composite_actions' in record:
                print(f"   复合操作: {len(record['composite_actions'])}个步骤")
            print(f"   时间: {record['timestamp']}")
            print()
        
        print("=== 测试完成 ===")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保enhanced_nlp_parser.py文件存在且依赖正确")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def test_individual_operations():
    """测试各个单独的操作"""
    
    print("=== 测试各个单独的操作 ===\n")
    
    try:
        from Src.Backend.Unused.enhanced_nlp_parser import SmartInstructionParser
        
        parser = SmartInstructionParser()
        
        # 测试各个操作
        test_operations = [
            ("增大视频对比度", "对比度增强"),
            ("第一秒变成黑白", "第一秒变成黑白"),
            ("第一秒添加转场效果", "在1秒加转场"),
            ("第二秒开始时添加智能字幕", "第2秒开始添加智能字幕智能字幕")
        ]
        
        for description, instruction in test_operations:
            print(f"描述: {description}")
            print(f"指令: {instruction}")
            
            action = parser.parse_instruction(instruction)
            if action:
                print(f"  ✓ 解析成功: {action}")
            else:
                print(f"  ✗ 解析失败")
            print()
        
    except Exception as e:
        print(f"测试单独操作时出错: {e}")


if __name__ == "__main__":
    print("开始测试'应用persona'复合指令...\n")
    
    # 运行测试
    test_persona_instruction()
    print("\n" + "="*50 + "\n")
    test_individual_operations()
