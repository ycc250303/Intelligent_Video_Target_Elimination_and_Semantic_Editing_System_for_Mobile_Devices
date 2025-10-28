#!/usr/bin/env python3
"""
视频剪辑人格建模系统主程序
"""

import json
from core.persona_model import VideoEditingPersona
from utils.data_loader import load_operations_data
from utils.visualizer import visualize_persona, visualize_recommendations

def main():
    print("=== 视频剪辑人格建模系统 ===")
    
    # 加载测试数据
    operations_data = load_operations_data("data/sample_operations.json")
    print(f"加载了 {len(operations_data)} 条操作记录")
    
    # 创建并训练人格模型
    persona_model = VideoEditingPersona()
    persona_model.train(operations_data)
    
    # 获取用户人格
    user_persona = persona_model.get_persona()
    print("\n=== 用户剪辑人格分析 ===")
    
    # 可视化展示人格特征
    visualize_persona(user_persona)
    
    # 测试推荐功能
    test_videos = [
        {"duration": 60, "aspect_ratio": "16:9", "category": "vlog"},
        {"duration": 15, "aspect_ratio": "9:16", "category": "short"},
        {"duration": 180, "aspect_ratio": "16:9", "category": "tutorial"}
    ]
    
    print("\n=== 个性化推荐测试 ===")
    for i, video in enumerate(test_videos, 1):
        recommendations = persona_model.predict_operations(video)
        visualize_recommendations(video, recommendations, f"测试视频 {i}")
    
    # 保存用户人格
    persona_model.save_persona("data/user_personas/user_persona.json")
    print(f"\n用户人格已保存到: data/user_personas/user_persona.json")

if __name__ == "__main__":
    main()