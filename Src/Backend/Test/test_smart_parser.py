#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能语言指令解析器
演示各种自然语言表达方式如何被理解和转换
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_smart_parser():
    """测试智能指令解析器"""
    
    try:
        from Src.Backend.Unused.enhanced_nlp_parser import SmartVideoEditor
        
        print("=== 智能语言指令系统测试 ===\n")
        
        # 创建智能视频编辑器实例
        editor = SmartVideoEditor()
        
        # 模拟视频上下文
        video_context = {
            'duration': 30.0,
            'resolution': (1920, 1080),
            'fps': 30,
            'format': 'mp4'
        }
        
        # 测试用例
        test_cases = [
            # 裁剪操作
            "剪掉开头5秒",
            "前3秒不要了",
            "删除开头2.5秒",
            "保留10秒到20秒",
            
            # 速度调整
            "视频快一点",
            "播放慢点",
            "速度调到1.5倍",
            "2倍速播放",
            
            # 亮度调整
            "亮度调高",
            "视频暗一点",
            "亮度1.3倍",
            "调亮一点",
            
            # 对比度调整
            "对比度增强",
            "对比度调低",
            
            # 音量调整
            "静音",
            "声音小一点",
            "音量提高",
            
            # 文字字幕
            "添加字幕Hello",
            "在5秒打字幕你好",
            "加文字标题",
            
            # 转场效果
            "加转场",
            "在3秒添加转场",
            "淡入淡出",
            
            # 黑白效果
            "变成黑白",
            "前5秒变黑白",
            "黑白效果",
            
            # 旋转
            "顺时针转90度",
            "向左转180度",
            
            # 复合指令
            "应用persona",
            "使用persona",
            "应用风格",
            
            # 复杂指令
            "剪掉开头3秒，然后快一点",
            "亮度调高，对比度增强",
            "前5秒变黑白，然后加转场"
        ]
        
        print("测试各种自然语言表达方式：\n")
        
        for i, instruction in enumerate(test_cases, 1):
            print(f"测试 {i}: {instruction}")
            
            # 处理指令
            result = editor.process_instruction(instruction, video_context)
            
            if result['success']:
                print(f"  ✓ 成功解析")
                print(f"  操作: {result['action']}")
                print(f"  说明: {result['explanation']}")
                
                # 显示复合指令的详细信息
                if result.get('is_composite', False):
                    print(f"  类型: 复合指令")
                    print(f"  包含操作:")
                    for i, action in enumerate(result.get('composite_actions', []), 1):
                        print(f"    {i}. {action}")
                
                if result['suggestions']:
                    print(f"  建议: {', '.join(result['suggestions'])}")
            else:
                print(f"  ✗ 解析失败")
                print(f"  说明: {result['explanation']}")
                if result['suggestions']:
                    print(f"  建议: {', '.join(result['suggestions'])}")
            
            print()
        
        # 测试操作历史
        print("=== 操作历史 ===")
        history = editor.get_history()
        for i, record in enumerate(history, 1):
            print(f"{i}. 输入: {record['input']}")
            print(f"   操作: {record['action']}")
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


def test_pattern_matching():
    """测试模式匹配功能"""
    
    print("=== 模式匹配测试 ===\n")
    
    try:
        from Src.Backend.Unused.enhanced_nlp_parser import SmartInstructionParser
        
        parser = SmartInstructionParser()
        
        # 测试各种模式
        test_patterns = [
            ("剪掉开头5秒", "trim"),
            ("前3秒不要了", "trim"),
            ("视频快一点", "speed"),
            ("亮度调高", "brightness"),
            ("静音", "volume"),
            ("添加字幕Hello", "text"),
            ("加转场", "transition"),
            ("变成黑白", "black_and_white"),
            ("顺时针转90度", "rotate")
        ]
        
        for instruction, expected_operation in test_patterns:
            action = parser.parse_instruction(instruction)
            if action:
                print(f"✓ '{instruction}' → {action}")
            else:
                print(f"✗ '{instruction}' → 无法解析")
        
    except Exception as e:
        print(f"模式匹配测试失败: {e}")


if __name__ == "__main__":
    print("开始测试智能语言指令系统...\n")
    
    # 运行测试
    test_smart_parser()
    print("\n" + "="*50 + "\n")
    test_pattern_matching()
