#!/usr/bin/env python3
"""
简化的Persona系统测试
仅测试基础数据模型和数据库功能
"""

import os
import json
import sys
import sqlite3
from datetime import datetime

# 添加Backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.persona_model import PersonaModel, PersonaCategory, PersonaStatus
from database.persona_db import PersonaDatabase


def test_persona_model():
    """测试Persona模型"""
    print("🔹 测试Persona模型...")
    
    # 创建测试Persona
    persona = PersonaModel(
        name="测试剪辑师",
        description="这是一个测试用的剪辑师Persona",
        category=PersonaCategory.CREATIVE,
        author="test_user"
    )
    
    # 测试基本属性
    assert persona.metadata.name == "测试剪辑师"
    assert persona.metadata.category == PersonaCategory.CREATIVE
    assert persona.metadata.author == "test_user"
    print("✅ 基本属性测试通过")
    
    # 测试添加标签
    persona.add_tag("测试")
    persona.add_tag("创意")
    assert len(persona.metadata.tags) == 2
    assert "测试" in persona.metadata.tags
    print("✅ 标签功能测试通过")
    
    # 测试风格偏好更新
    persona.update_style_preferences({
        "fast_paced": 0.8,
        "visual_complexity": 0.7
    })
    assert persona.style_preferences.fast_paced == 0.8
    assert persona.style_preferences.visual_complexity == 0.7
    print("✅ 风格偏好更新测试通过")
    
    # 测试序列化
    persona_dict = persona.to_dict()
    assert isinstance(persona_dict, dict)
    assert persona_dict['metadata']['name'] == "测试剪辑师"
    print("✅ 序列化测试通过")
    
    print("🔹 Persona模型测试完成\n")


def test_database_functionality():
    """测试数据库功能"""
    print("🔹 测试数据库功能...")
    
    # 创建测试数据库
    test_db_path = "test_persona.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = PersonaDatabase(test_db_path)
    
    # 创建测试Persona
    persona = PersonaModel(
        name="数据库测试剪辑师",
        description="这是数据库测试用的Persona",
        category=PersonaCategory.PROFESSIONAL,
        author="db_test_user"
    )
    
    persona.add_tag("数据库测试")
    persona.add_tag("专业")
    persona.update_style_preferences({
        "fast_paced": 0.6,
        "professional_quality": 0.9
    })
    
    # 测试创建
    success = db.create_persona(persona)
    assert success, "创建Persona失败"
    print("✅ 创建Persona测试通过")
    
    # 测试获取
    retrieved = db.get_persona(persona.metadata.id)
    assert retrieved is not None, "获取Persona失败"
    assert retrieved.metadata.name == persona.metadata.name, "Persona名称不匹配"
    assert retrieved.metadata.category == persona.metadata.category, "Persona分类不匹配"
    assert len(retrieved.metadata.tags) == 2, "标签数量不匹配"
    print("✅ 获取Persona测试通过")
    
    # 测试更新
    persona.metadata.description = "更新后的描述"
    persona.add_tag("更新测试")
    success = db.update_persona(persona)
    assert success, "更新Persona失败"
    
    updated = db.get_persona(persona.metadata.id)
    assert updated.metadata.description == "更新后的描述", "描述更新失败"
    assert len(updated.metadata.tags) == 3, "标签更新失败"
    print("✅ 更新Persona测试通过")
    
    # 测试列表
    personas = db.list_personas(author="db_test_user")
    assert len(personas) >= 1, "列表Persona失败"
    assert personas[0]['name'] == "数据库测试剪辑师", "列表结果不正确"
    print("✅ 列表Persona测试通过")
    
    # 测试搜索
    search_results = db.search_personas("数据库")
    assert len(search_results) >= 1, "搜索Persona失败"
    assert search_results[0]['name'] == "数据库测试剪辑师", "搜索结果不正确"
    print("✅ 搜索Persona测试通过")
    
    # 测试添加反馈
    from models.persona_model import UserFeedback
    feedback = UserFeedback(
        persona_id=persona.metadata.id,
        user_id="test_feedback_user",
        rating=4.5,
        text_feedback="很棒的Persona！"
    )
    
    success = db.add_user_feedback(feedback)
    assert success, "添加反馈失败"
    print("✅ 添加反馈测试通过")
    
    # 测试删除
    success = db.delete_persona(persona.metadata.id)
    assert success, "删除Persona失败"
    
    deleted = db.get_persona(persona.metadata.id)
    assert deleted is None, "Persona未被正确删除"
    print("✅ 删除Persona测试通过")
    
    # 清理测试数据
    os.remove(test_db_path)
    print("🔹 数据库功能测试完成\n")


def test_default_personas():
    """测试默认Persona"""
    print("🔹 测试默认Persona...")
    
    from models.persona_model import DEFAULT_PERSONAS
    
    assert len(DEFAULT_PERSONAS) > 0, "没有默认Persona"
    
    for key, persona in DEFAULT_PERSONAS.items():
        assert isinstance(persona, PersonaModel), f"默认Persona {key} 类型不正确"
        assert persona.metadata.name is not None, f"默认Persona {key} 缺少名称"
        assert persona.metadata.description is not None, f"默认Persona {key} 缺少描述"
        assert persona.metadata.author == "system", f"默认Persona {key} 作者应为system"
        print(f"✅ 默认Persona {key} ({persona.metadata.name}) 验证通过")
    
    print("🔹 默认Persona测试完成\n")


def test_persona_categories():
    """测试Persona分类"""
    print("🔹 测试Persona分类...")
    
    # 测试所有分类都可以正常创建
    categories = [
        PersonaCategory.CREATIVE,
        PersonaCategory.PROFESSIONAL,
        PersonaCategory.ENTERTAINMENT,
        PersonaCategory.EDUCATIONAL,
        PersonaCategory.COMMERCIAL,
        PersonaCategory.LIFESTYLE
    ]
    
    for category in categories:
        persona = PersonaModel(
            name=f"{category.value}_测试",
            description=f"测试{category.value}分类",
            category=category,
            author="category_test"
        )
        assert persona.metadata.category == category, f"分类 {category} 设置失败"
        print(f"✅ 分类 {category.value} 测试通过")
    
    print("🔹 Persona分类测试完成\n")


def main():
    """主测试函数"""
    print("🚀 开始简化的Persona系统测试\n")
    print("=" * 50)
    
    try:
        # 1. 测试Persona模型
        test_persona_model()
        
        # 2. 测试数据库功能
        test_database_functionality()
        
        # 3. 测试默认Persona
        test_default_personas()
        
        # 4. 测试Persona分类
        test_persona_categories()
        
        print("=" * 50)
        print("🎉 所有基础测试完成！Persona数据层运行正常。")
        print("\n📋 测试总结:")
        print("✅ Persona模型 - 正常")
        print("✅ 数据库操作 - 正常")
        print("✅ 默认Persona - 正常")
        print("✅ 分类系统 - 正常")
        
        print("\n🔧 后续步骤:")
        print("1. 安装完整依赖 (pip install opencv-python scikit-learn)")
        print("2. 运行完整的测试脚本")
        print("3. 启动API服务器测试")
        print("4. 进行前端集成测试")
        
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