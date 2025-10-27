#!/usr/bin/env python3
"""
测试 multimodal_video_tool.py 的基本功能（不需要API调用）
"""

import sys
from pathlib import Path

def test_import():
    """测试导入"""
    print("📦 测试导入...")
    try:
        from multimodal_video_tool import MultimodalVideoTool
        print("✅ MultimodalVideoTool 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_init():
    """测试初始化"""
    print("\n🔧 测试初始化...")
    try:
        from multimodal_video_tool import MultimodalVideoTool
        tool = MultimodalVideoTool(output_dir="Results/test")
        print("✅ 工具初始化成功")
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_modal_type():
    """测试模态类型判断"""
    print("\n🎯 测试模态类型判断...")
    try:
        from multimodal_video_tool import MultimodalVideoTool
        tool = MultimodalVideoTool()
        
        # 测试各种输入组合
        tests = [
            ("text", None, None, "纯文本 (Qwen生成)"),
            ("text", "video.mp4", None, "视频+文本 (FFmpeg编辑)"),
            ("text", None, "image.jpg", "图片+文本 (Qwen生成)"),
            ("text", "video.mp4", "image.jpg", "视频+图片+文本"),
        ]
        
        all_pass = True
        for text, video, image, expected in tests:
            result = tool._get_modal_type(text, video, image)
            if result == expected:
                print(f"✅ {expected}")
            else:
                print(f"❌ 期望: {expected}, 得到: {result}")
                all_pass = False
        
        return all_pass
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_validation():
    """测试文件验证"""
    print("\n📁 测试文件验证...")
    try:
        from multimodal_video_tool import MultimodalVideoTool
        tool = MultimodalVideoTool()
        
        # 测试不存在的文件
        print("测试不存在的视频文件...")
        result = tool.process(
            text="test",
            video_path="nonexistent.mp4",
            auto_execute=False
        )
        
        if not result['success'] and 'error' in result:
            print("✅ 正确检测到文件不存在")
            return True
        else:
            print("❌ 未能检测到文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("="*70)
    print("🧪 多模态视频工具 - 基本功能测试")
    print("="*70)
    print("\n这些测试不需要API密钥或实际的视频文件\n")
    
    results = []
    
    # 运行测试
    results.append(("导入测试", test_import()))
    
    # 如果导入成功，继续其他测试
    if results[0][1]:
        results.append(("初始化测试", test_init()))
        results.append(("模态类型判断", test_modal_type()))
        results.append(("文件验证", test_file_validation()))
    
    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有基本功能测试通过！")
        print("\n💡 注意: 这些只是基本测试，实际使用需要:")
        print("   1. 安装所有依赖 (dashscope, openai, 等)")
        print("   2. 配置 API 密钥")
        print("   3. 准备测试文件")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


