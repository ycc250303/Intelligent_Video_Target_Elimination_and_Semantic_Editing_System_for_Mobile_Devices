#!/usr/bin/env python3
"""
测试千问模型版本的视频编辑器
"""

import os
import sys
from qwen_nlp_parser import process_instruction, DialogueManager

def test_qwen_parser():
    """
    测试千问模型 NLP 解析器
    """
    print("=== 测试千问模型 NLP 解析器 ===")
    
    test_instructions = [
        "把开头 1 秒剪掉",
        "片头加 1.5 秒淡入效果", 
        "整体速度调到 1.5 倍",
        "打字幕 Hello 3 秒放左下",
        "声音小一半",
        "亮一点",
        "对比度增强",
        "把视频变成黑白的"
    ]
    
    for i, instruction in enumerate(test_instructions, 1):
        print(f"\n测试 {i}: {instruction}")
        try:
            content, confirmation, history = process_instruction(instruction)
            print(f"解析结果: {content}")
            print(f"确认消息: {confirmation}")
            if content and content.startswith("action:"):
                print("✅ 成功解析为操作指令")
            else:
                print("❌ 未能解析为操作指令")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def test_dialogue_manager():
    """
    测试对话管理器
    """
    print("\n=== 测试对话管理器 ===")
    
    manager = DialogueManager()
    
    test_inputs = [
        "把开头 1 秒剪掉",
        "片头加淡入效果",
        "速度调快一点"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n对话 {i}: {user_input}")
        try:
            result = manager.process_user_input(user_input)
            print(f"响应: {result['response']}")
            print(f"成功: {result['success']}")
            print(f"操作: {result['action']}")
        except Exception as e:
            print(f"❌ 对话失败: {e}")

def test_multi_turn_conversation():
    """
    测试多轮对话
    """
    print("\n=== 测试多轮对话 ===")
    
    manager = DialogueManager()
    
    conversation = [
        "把开头 1 秒剪掉",
        "然后片头加淡入效果",
        "最后速度调快一点"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n第 {i} 轮: {user_input}")
        try:
            result = manager.process_user_input(user_input)
            print(f"响应: {result['response']}")
            print(f"操作: {result['action']}")
        except Exception as e:
            print(f"❌ 对话失败: {e}")

if __name__ == "__main__":
    print("开始测试千问模型版本的视频编辑器...")
    
    # 测试 NLP 解析器
    test_qwen_parser()
    
    # 测试对话管理器
    test_dialogue_manager()
    
    # 测试多轮对话
    test_multi_turn_conversation()
    
    print("\n=== 测试完成 ===")
