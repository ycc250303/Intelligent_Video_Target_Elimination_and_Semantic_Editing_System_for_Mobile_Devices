"""
Visualization helpers for persona analysis.
"""

import matplotlib.pyplot as plt


def visualize_persona(user_persona):
    """在控制台展示人格分析结果"""
    stats = user_persona.get("statistics", {})
    print(f"总操作次数: {user_persona.get('total_operations', 0)}")
    print("\n=== 操作偏好排名 ===")
    for action, confidence in user_persona.get("preferences", {}).get("frequent_actions", {}).items():
        print(f"- {action:<20} 置信度: {confidence:.2f}")

    print("\n=== 常用工作流模板 ===")
    workflows = user_persona.get("workflow_templates", [])
    for workflow in workflows:
        sequence = " -> ".join(workflow.get("sequence", []))
        print(f"- {sequence:<40} 置信度: {workflow.get('confidence', 0.0):.2f}")

    _create_persona_charts(user_persona)
    _create_effect_and_stage_charts(user_persona)


def _create_persona_charts(user_persona):
    """生成基本的可视化图表"""
    stats = user_persona.get("statistics", {})

    actions = list(stats.get("action_frequencies", {}).keys())
    freqs = list(stats.get("action_frequencies", {}).values())

    if not actions:
        print("\n暂无操作频率数据可视化。")
        return

    plt.figure(figsize=(10, 4))
    plt.bar(actions, freqs)
    plt.title("用户操作频率分布")
    plt.xlabel("操作类型")
    plt.ylabel("频率")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("persona_analysis.png", dpi=150, bbox_inches="tight")
    print("\n人格分析图表已保存为: persona_analysis.png")


def _create_effect_and_stage_charts(user_persona):
    preferences = user_persona.get("preferences", {})
    effect_tendencies = preferences.get("effect_tendencies", {})
    stage_distribution = user_persona.get("statistics", {}).get("action_stage_distribution", {})

    if not effect_tendencies and not stage_distribution:
        print("暂无效果偏好或阶段分布数据。")
        return

    plt.figure(figsize=(12, 5))

    if effect_tendencies:
        plt.subplot(1, 2, 1)
        effects = list(effect_tendencies.keys())
        weights = list(effect_tendencies.values())
        plt.barh(effects, weights)
        plt.title("效果偏好分布")

    if stage_distribution:
        plt.subplot(1, 2, 2)
        stages = list(stage_distribution.keys())
        ratios = list(stage_distribution.values())
        plt.bar(stages, ratios)
        plt.title("动作阶段分布")

    plt.tight_layout()
    plt.savefig("persona_analysis_extended.png", dpi=150, bbox_inches="tight")
    print("扩展可视化图表已保存为: persona_analysis_extended.png")


def visualize_recommendations(video, recommendations, title="推荐操作"):
    """展示推荐结果"""
    print(f"\n{title}")
    print(f"视频信息: 时长 {video.get('duration', '未知')} 秒, 比例 {video.get('aspect_ratio', '未知')}, 类型 {video.get('category', '未知')}")
    if not recommendations:
        print("暂无推荐。")
        return
    for rec in recommendations:
        print(
            f"- {rec['action']:<20} 置信度: {rec['confidence']:.2f} 来源: {rec['source']}"
        )
