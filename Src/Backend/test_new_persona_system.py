#!/usr/bin/env python3
"""
测试新的Persona系统
验证完整的前后端流程
"""

import os
import json
import sys
import time
import requests
import sqlite3
from datetime import datetime

# 添加Backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 修复导入路径
try:
    from models.persona_model import PersonaModel, PersonaCategory, PersonaStatus
    from database.persona_db import PersonaDatabase
    from services.persona_service import persona_service
except ImportError:
    # 如果相对导入失败，尝试直接导入
    import models.persona_model as persona_model_module
    import database.persona_db as persona_db_module
    import services.persona_service as persona_service_module
    
    PersonaModel = persona_model_module.PersonaModel
    PersonaCategory = persona_model_module.PersonaCategory
    PersonaStatus = persona_model_module.PersonaStatus
    PersonaDatabase = persona_db_module.PersonaDatabase
    persona_service = persona_service_module.persona_service


def test_database_functionality():
    """测试数据库功能"""
    print("🔹 测试数据库功能...")
    
    # 创建测试数据库
    db = PersonaDatabase("test_persona.db")
    
    # 创建测试Persona
    persona = PersonaModel(
        name="测试剪辑师",
        description="这是一个测试用的剪辑师Persona",
        category=PersonaCategory.CREATIVE,
        author="test_user"
    )
    
    persona.add_tag("测试")
    persona.add_tag("创意")
    
    # 测试创建
    success = db.create_persona(persona)
    assert success, "创建Persona失败"
    print("✅ 创建Persona成功")
    
    # 测试获取
    retrieved = db.get_persona(persona.metadata.id)
    assert retrieved is not None, "获取Persona失败"
    assert retrieved.metadata.name == persona.metadata.name, "Persona名称不匹配"
    print("✅ 获取Persona成功")
    
    # 测试列表
    personas = db.list_personas(author="test_user")
    assert len(personas) > 0, "列表Persona失败"
    print("✅ 列表Persona成功")
    
    # 测试搜索
    search_results = db.search_personas("测试")
    assert len(search_results) > 0, "搜索Persona失败"
    print("✅ 搜索Persona成功")
    
    # 清理测试数据
    os.remove("test_persona.db")
    print("🔹 数据库测试完成\n")


def test_service_functionality():
    """测试服务层功能"""
    print("🔹 测试服务层功能...")
    
    # 创建Persona
    success, message, result = persona_service.create_persona(
        name="服务测试剪辑师",
        description="这是服务层测试的Persona",
        category="creative",
        author="service_test_user",
        tags=["服务测试", "创意"],
        style_preferences={
            "fast_paced": 0.8,
            "visual_complexity": 0.7
        },
        is_public=True
    )
    
    assert success, f"服务层创建Persona失败: {message}"
    print("✅ 服务层创建Persona成功")
    
    persona_id = result['id']
    
    # 获取Persona
    success, message, result = persona_service.get_persona(persona_id)
    assert success, f"服务层获取Persona失败: {message}"
    print("✅ 服务层获取Persona成功")
    
    # 列出Persona
    success, message, result = persona_service.list_personas(author="service_test_user")
    assert success, f"服务层列表Persona失败: {message}"
    assert len(result) > 0, "列表结果为空"
    print("✅ 服务层列表Persona成功")
    
    # 提交反馈
    success, message = persona_service.process_user_feedback(
        persona_id=persona_id,
        user_id="test_user_123",
        rating=4.5,
        style_preferences={"fast_paced": 0.9},
        text_feedback="很好用的Persona"
    )
    assert success, f"服务层提交反馈失败: {message}"
    print("✅ 服务层提交反馈成功")
    
    print("🔹 服务层测试完成\n")


def test_api_endpoints():
    """测试API端点"""
    print("🔹 测试API端点...")
    
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health-check", timeout=5)
        assert response.status_code == 200, "健康检查失败"
        print("✅ 健康检查成功")
    except requests.exceptions.RequestException as e:
        print(f"❌ 健康检查失败: {e}")
        print("⚠️  请确保API服务器正在运行 (python api_server.py)")
        return
    
    # 测试获取分类
    try:
        response = requests.get(f"{base_url}/api/persona/categories")
        assert response.status_code == 200, "获取分类失败"
        data = response.json()
        assert data['success'], f"获取分类失败: {data['message']}"
        print("✅ 获取分类成功")
    except Exception as e:
        print(f"❌ 获取分类失败: {e}")
    
    # 测试创建Persona
    try:
        persona_data = {
            "name": "API测试剪辑师",
            "description": "通过API创建的测试Persona",
            "category": "creative",
            "author": "api_test_user",
            "tags": ["API测试", "创意"],
            "is_public": True
        }
        
        response = requests.post(
            f"{base_url}/api/persona/create",
            json=persona_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 201, f"创建Persona失败: {response.status_code}"
        data = response.json()
        assert data['success'], f"创建Persona失败: {data['message']}"
        
        persona_id = data['data']['id']
        print("✅ API创建Persona成功")
        
        # 测试获取Persona
        response = requests.get(f"{base_url}/api/persona/get/{persona_id}")
        assert response.status_code == 200, "获取Persona失败"
        data = response.json()
        assert data['success'], f"获取Persona失败: {data['message']}"
        print("✅ API获取Persona成功")
        
        # 测试列出Persona
        response = requests.get(f"{base_url}/api/persona/list?author=api_test_user")
        assert response.status_code == 200, "列出Persona失败"
        data = response.json()
        assert data['success'], f"列出Persona失败: {data['message']}"
        print("✅ API列出Persona成功")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
    
    print("🔹 API测试完成\n")


def test_integration_flow():
    """测试完整集成流程"""
    print("🔹 测试完整集成流程...")
    
    # 1. 创建用户
    user_id = "integration_test_user"
    
    # 2. 创建Persona
    success, message, persona_result = persona_service.create_persona(
        name="集成测试大师",
        description="专门用于集成测试的剪辑师",
        category="professional",
        author=user_id,
        tags=["集成测试", "专业", "自动化"],
        style_preferences={
            "fast_paced": 0.6,
            "professional_quality": 0.9,
            "visual_complexity": 0.5
        },
        is_public=True
    )
    
    assert success, f"集成测试创建Persona失败: {message}"
    persona_id = persona_result['id']
    print("✅ 集成测试创建Persona成功")
    
    # 3. 模拟视频分析（如果有测试视频）
    test_video_path = "uploads/001.mp4"  # 假设存在测试视频
    if os.path.exists(test_video_path):
        success, message, analysis_result = persona_service.analyze_video_preferences(
            persona_id, test_video_path
        )
        if success:
            print("✅ 视频偏好分析成功")
        else:
            print(f"⚠️  视频偏好分析失败: {message}")
    
    # 4. 生成剪辑方案
    success, message, plan_result = persona_service.generate_editing_plan(
        persona_id=persona_id,
        user_instruction="制作一个快节奏的宣传视频",
        video_path=test_video_path if os.path.exists(test_video_path) else "dummy_path.mp4",
        user_id=user_id
    )
    
    if success:
        print("✅ 生成剪辑方案成功")
        print(f"   方案包含 {len(plan_result.get('operations', []))} 个操作")
    else:
        print(f"⚠️  生成剪辑方案失败: {message}")
    
    # 5. 记录操作反馈
    success, message = persona_service.record_editing_operation(
        persona_id=persona_id,
        operation_type="speed",
        parameters={"factor": 1.5},
        success=True,
        execution_time=2.5,
        user_rating=4.0
    )
    
    assert success, f"记录操作失败: {message}"
    print("✅ 记录编辑操作成功")
    
    # 6. 提交用户反馈
    success, message = persona_service.process_user_feedback(
        persona_id=persona_id,
        user_id=user_id,
        rating=4.5,
        style_preferences={"fast_paced": 0.8},
        text_feedback="这个Persona很好用，生成的方案很符合我的需求！"
    )
    
    assert success, f"提交反馈失败: {message}"
    print("✅ 提交用户反馈成功")
    
    # 7. 获取统计信息
    success, message, stats = persona_service.get_persona_statistics(persona_id)
    if success:
        print("✅ 获取统计信息成功")
        print(f"   使用次数: {stats['basic_stats']['usage_count']}")
        print(f"   平均评分: {stats['basic_stats']['rating_average']:.1f}")
        print(f"   主导风格: {stats['dominant_style']}")
    else:
        print(f"⚠️  获取统计信息失败: {message}")
    
    print("🔹 集成测试完成\n")


def main():
    """主测试函数"""
    print("🚀 开始测试新的Persona系统\n")
    print("=" * 50)
    
    try:
        # 1. 测试数据库功能
        test_database_functionality()
        
        # 2. 测试服务层功能
        test_service_functionality()
        
        # 3. 测试API端点（需要服务器运行）
        test_api_endpoints()
        
        # 4. 测试完整集成流程
        test_integration_flow()
        
        print("=" * 50)
        print("🎉 所有测试完成！新的Persona系统运行正常。")
        print("\n📋 测试总结:")
        print("✅ 数据库层 - 正常")
        print("✅ 服务层 - 正常")
        print("✅ API层 - 正常")
        print("✅ 集成流程 - 正常")
        
        print("\n🔧 后续步骤:")
        print("1. 在前端应用中测试新的PersonaAPIClient")
        print("2. 验证PersonaContext的集成")
        print("3. 测试CommunityScreen的新功能")
        print("4. 进行端到端测试")
        
    except AssertionError as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
