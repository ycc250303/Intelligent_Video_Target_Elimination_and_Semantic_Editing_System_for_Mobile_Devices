#!/usr/bin/env python3
"""
轻量级自测脚本：仅验证 NLP 解析层是否能识别 Qwen 的视频生成操作。
不调用任何外部 API，仅使用 qwen_nlp_parser 的分类与响应生成功能。
运行：python Src/newBackend/test_nlp_qwen_ops.py
"""

import os
import sys
import json

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.qwen_nlp_parser import classify_instruction_type, generate_response_by_type


def run_case(title: str, ai_response_obj: dict, expected_type: int):
    print(f"\n=== {title} ===")
    ai_response = json.dumps(ai_response_obj, ensure_ascii=False)
    t = classify_instruction_type("用户口语输入示例", ai_response)
    print("分类结果:", t, "期望:", expected_type)
    processed = generate_response_by_type(t, ai_response, "用户口语输入示例")
    print("处理后响应:", processed)
    assert t == expected_type, f"期望类型 {expected_type}, 实际 {t}"
    return processed


def main():
    # 情况1：参数齐全 → type=1
    case1 = {
        "operations": {
            "operation": "make_video_by_first_frame",
            "params": {
                "img_url": "../Images/hanfu.png",
                "prompt": "小猫在草地上快速奔跑",
                "model": "wan2.2-i2v-flash",
                "resolution": "1080P"
            },
            "editor": "qwen"
        }
    }
    run_case("I2V-首帧-参数齐全", case1, expected_type=1)

    # 情况2：能匹配操作但提取不到必要参数（例如 prompt 为 Unknown）→ type=2
    case2 = {
        "operations": {
            "operation": "make_video_by_text",
            "params": {
                "prompt": "小猫在草地上快速奔跑"
            },
            "editor": "qwen"
        }
    }
    processed2 = run_case("T2V-缺失参数", case2, expected_type=1)
    # 验证生成的响应里 params 被填充为 None
    data2 = json.loads(processed2)
    assert set(data2["operations"]["params"].keys()) >= {"prompt", "model", "size"}

    # 情况3：不匹配的操作 → type=3
    case3 = {"operations": {}}
    run_case("无匹配操作", case3, expected_type=3)

    print("\n✅ 全部用例通过")


if __name__ == "__main__":
    main()


