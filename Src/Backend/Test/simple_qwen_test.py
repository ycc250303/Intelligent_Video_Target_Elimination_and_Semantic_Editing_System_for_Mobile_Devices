#!/usr/bin/env python3
"""
简单的千问模型测试
"""

import os
from openai import OpenAI

# 千问模型配置
QWEN_API_KEY = "sk-20b4e293dc524e6ca819d9b37e2cadd2"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-plus"

def test_qwen_basic():
    """
    测试千问模型基本功能
    """
    print("=== 测试千问模型基本功能 ===")
    
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
        )
        
        # 测试消息
        messages = [
            {"role": "user", "content": "你好，请简单介绍一下自己"}
        ]
        
        print("正在调用千问模型...")
        
        # 调用千问模型
        completion = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        response = completion.choices[0].message.content
        print(f"千问模型响应: {response}")
        print("✅ 千问模型测试成功！")
        
    except Exception as e:
        print(f"❌ 千问模型测试失败: {e}")

def test_qwen_video_instruction():
    """
    测试千问模型处理视频指令
    """
    print("\n=== 测试千问模型处理视频指令 ===")
    
    try:
        # 初始化客户端
        client = OpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
        )
        
        # 系统提示词
        system_prompt = (
            "你是我的视频剪辑小帮手。你需要判断能否对收到的指令进行视频剪辑操作，收到任何中文指令，如果可以处理，则回复："
            "action: <操作> [参数] editor=<编辑器类型>。\n\n"
            "例子：\n"
            "- '把开头 1 秒剪掉' → action: trim start=1.0 editor=moviepy\n"
            "- '片头加淡入效果' → action: add_transition type=fade duration=1.0 start_time=0.0 editor=moviepy\n"
        )
        
        # 测试指令
        test_instructions = [
            "把开头 1 秒剪掉",
            "片头加淡入效果",
            "速度调快一点"
        ]
        
        for i, instruction in enumerate(test_instructions, 1):
            print(f"\n测试指令 {i}: {instruction}")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ]
            
            completion = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages,
                temperature=0.9,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content
            print(f"解析结果: {response}")
            
            if "action:" in response:
                print("✅ 成功解析为操作指令")
            else:
                print("❌ 未能解析为操作指令")
                
    except Exception as e:
        print(f"❌ 视频指令测试失败: {e}")

if __name__ == "__main__":
    print("开始测试千问模型...")
    
    # 基本功能测试
    test_qwen_basic()
    
    # 视频指令测试
    test_qwen_video_instruction()
    
    print("\n=== 测试完成 ===")
