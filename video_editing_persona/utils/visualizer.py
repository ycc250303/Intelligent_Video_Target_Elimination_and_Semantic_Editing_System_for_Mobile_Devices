import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_persona(user_persona):
    """可视化用户人格特征"""
    print("\n--- 用户剪辑习惯分析 ---")
    
    # 显示基本统计
    stats = user_persona.get('statistics', {})
    print(f"总操作次数: {user_persona.get('total_operations', 0)}")
    print(f"总剪辑时长: {stats.get('total_editing_duration', 0):.1f} 秒")
    print(f"平均每次会话操作数: {stats.get('average_operations_per_session', 0):.1f}")
    
    # 显示最常用操作
    print("\n最常用的操作:")
    for action, count in stats.get('most_common_actions', [])[:5]:
        freq = stats.get('action_frequencies', {}).get(action, 0)
        print(f"  {action}: {count}次 ({freq*100:.1f}%)")
    
    # 显示偏好分类
    print("\n最常编辑的视频类型:")
    for category, count in stats.get('preferred_categories', [])[:3]:
        print(f"  {category}: {count}次")
    
    # 显示工作流模板
    workflows = user_persona.get('workflow_templates', [])
    if workflows:
        print("\n常用工作流模板:")
        for i, workflow in enumerate(workflows[:3], 1):
            # 确保序列中的所有元素都是字符串
            sequence_str = " → ".join(str(action) for action in workflow['sequence'])
            print(f"  模板{i}: {sequence_str} (置信度: {workflow['confidence']:.2f})")
    
    # 可视化图表
    _create_persona_charts(user_persona)
    _create_effect_and_stage_charts(user_persona)

def _create_persona_charts(user_persona):
    """创建人格分析图表"""
    # 设置matplotlib支持中文显示（扩展常见可用字体，优先macOS字体）
    plt.rcParams['font.sans-serif'] = [
        'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei',
        'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'SimHei', 'Songti SC',
        'Heiti SC', 'STHeiti', 'DejaVu Sans'
    ]
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    stats = user_persona.get('statistics', {})
    action_frequencies = stats.get('action_frequencies', {})
    
    if not action_frequencies:
        print("没有足够的数据生成图表")
        return
    
    try:
        # 操作频率饼图
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        actions = list(action_frequencies.keys())[:8]  # 取前8个
        frequencies = [action_frequencies[action] for action in actions]
        
        # 确保所有标签都是字符串
        labels = [str(action) for action in actions]
        
        plt.pie(frequencies, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Operation Frequency Distribution')
        
        # 参数偏好条形图
        plt.subplot(1, 2, 2)
        preferences = user_persona.get('preferences', {})
        parameter_tendencies = preferences.get('parameter_tendencies', {})
        
        # 选择几个关键操作的参数偏好显示
        top_actions = list(action_frequencies.keys())[:4]
        param_data = {}
        
        for action in top_actions:
            if action in parameter_tendencies:
                for param, data in parameter_tendencies[action].items():
                    if 'average' in data:
                        key = f"{action}.{param}"
                        param_data[key] = data['average']
        
        if param_data:
            param_names = list(param_data.keys())
            param_values = list(param_data.values())
            
            y_pos = np.arange(len(param_names))
            plt.barh(y_pos, param_values)
            plt.yticks(y_pos, param_names)
            plt.title('Parameter Preferences')
            plt.xlabel('Average Value')
        else:
            # 如果没有参数数据，显示操作频率条形图
            actions = list(action_frequencies.keys())[:6]
            frequencies = [action_frequencies[action] for action in actions]
            
            y_pos = np.arange(len(actions))
            plt.barh(y_pos, frequencies)
            plt.yticks(y_pos, [str(action) for action in actions])
            plt.title('Top Operations')
            plt.xlabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('persona_analysis.png', dpi=150, bbox_inches='tight')
        print("\n人格分析图表已保存为: persona_analysis.png")
        
    except Exception as e:
        print(f"生成图表时出错: {e}")
        # 尝试使用英文设置
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        try:
            plt.figure(figsize=(10, 6))
            actions = list(action_frequencies.keys())[:6]
            frequencies = [action_frequencies[action] for action in actions]
            
            plt.bar(range(len(actions)), frequencies)
            plt.xticks(range(len(actions)), [str(action) for action in actions], rotation=45)
            plt.title('Operation Frequencies')
            plt.ylabel('Frequency')
            
            plt.tight_layout()
            plt.savefig('persona_analysis_simple.png', dpi=150, bbox_inches='tight')
            print("简化版人格分析图表已保存为: persona_analysis_simple.png")
        except Exception as e2:
            print(f"生成简化图表时也出错: {e2}")

def _create_effect_and_stage_charts(user_persona):
    """展示效果偏好与动作阶段分布，以及动作-效果意图映射。"""
    # 再次确保中文字体回退链覆盖
    plt.rcParams['font.sans-serif'] = [
        'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei',
        'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'SimHei', 'Songti SC',
        'Heiti SC', 'STHeiti', 'DejaVu Sans'
    ]
    plt.rcParams['axes.unicode_minus'] = False
    preferences = user_persona.get('preferences', {})
    stats = user_persona.get('statistics', {})
    effect_tendencies = preferences.get('effect_tendencies', {})
    effect_to_actions = preferences.get('effect_to_actions', {})
    stage_dist = stats.get('action_stage_distribution', {})

    has_effects = bool(effect_tendencies)
    has_stage = bool(stage_dist)
    has_mapping = bool(effect_to_actions)

    if not (has_effects or has_stage or has_mapping):
        return

    try:
        # 取top效果与top动作
        top_effects = sorted(effect_tendencies.items(), key=lambda x: x[1], reverse=True)[:8] if has_effects else []
        effect_labels = [e for e, _ in top_effects]
        effect_values = [v for _, v in top_effects]

        # 从动作频率中选top动作
        action_freq = stats.get('action_frequencies', {})
        top_actions = list(sorted(action_freq.items(), key=lambda x: x[1], reverse=True))[:6]
        action_labels = [a for a, _ in top_actions]

        # 准备动作-效果矩阵（显示强度）与样本量矩阵
        heatmap = None
        countmap = None
        if has_mapping and effect_labels and action_labels:
            heatmap = np.zeros((len(effect_labels), len(action_labels)))
            countmap = np.zeros((len(effect_labels), len(action_labels)))
            for i, eff in enumerate(effect_labels):
                amap = effect_to_actions.get(eff, {})
                acount = preferences.get('effect_to_actions_counts', {}).get(eff, {})
                for j, act in enumerate(action_labels):
                    heatmap[i, j] = float(amap.get(act, 0.0))
                    countmap[i, j] = float(acount.get(act, 0.0))

        # 准备阶段分布数据
        stage_matrix = None
        if has_stage and action_labels:
            stage_matrix = np.zeros((3, len(action_labels)))  # early, middle, late
            for j, act in enumerate(action_labels):
                buckets = stage_dist.get(act, {"early": 0, "middle": 0, "late": 0})
                stage_matrix[0, j] = float(buckets.get('early', 0.0))
                stage_matrix[1, j] = float(buckets.get('middle', 0.0))
                stage_matrix[2, j] = float(buckets.get('late', 0.0))

        # 生成图
        cols = 3
        plt.figure(figsize=(16, 5))

        # 子图1：效果偏好分布
        plt.subplot(1, cols, 1)
        if effect_labels:
            y_pos = np.arange(len(effect_labels))
            plt.barh(y_pos, effect_values)
            plt.yticks(y_pos, [str(e) for e in effect_labels])
            plt.title('Effect Preferences (推断的效果偏好)')
            plt.xlabel('Normalized Weight')
        else:
            plt.text(0.5, 0.5, '无效果偏好数据', ha='center', va='center')

        # 子图2：动作-效果映射热力图（强度+样本量注记）
        plt.subplot(1, cols, 2)
        if heatmap is not None:
            im = plt.imshow(heatmap, aspect='auto', cmap='YlOrRd')
            plt.colorbar(im, fraction=0.046, pad=0.04)
            plt.xticks(range(len(action_labels)), [str(a) for a in action_labels], rotation=45, ha='right')
            plt.yticks(range(len(effect_labels)), [str(e) for e in effect_labels])
            plt.title('Action → Effect (意图映射)')
            # 在格子里标注样本量
            if countmap is not None:
                for i in range(countmap.shape[0]):
                    for j in range(countmap.shape[1]):
                        c = int(countmap[i, j])
                        if c > 0:
                            plt.text(j, i, str(c), ha='center', va='center', color='black', fontsize=8)
        else:
            plt.text(0.5, 0.5, '无动作-效果映射', ha='center', va='center')

        # 子图3：动作在会话阶段的分布
        plt.subplot(1, cols, 3)
        if stage_matrix is not None:
            indices = np.arange(len(action_labels))
            bottom = np.zeros(len(action_labels))
            labels = ['early', 'middle', 'late']
            colors = ['#8dd3c7', '#ffffb3', '#fb8072']
            for i in range(3):
                plt.bar(indices, stage_matrix[i], bottom=bottom, color=colors[i], label=labels[i])
                bottom += stage_matrix[i]
            plt.xticks(indices, [str(a) for a in action_labels], rotation=45, ha='right')
            plt.legend()
            plt.title('Action Stage Distribution (会话阶段分布)')
        else:
            plt.text(0.5, 0.5, '无阶段分布数据', ha='center', va='center')

        plt.tight_layout()
        plt.savefig('persona_effects_stages.png', dpi=150, bbox_inches='tight')
        print("效果与阶段图表已保存为: persona_effects_stages.png")
    except Exception as e:
        print(f"生成效果与阶段图表时出错: {e}")

def visualize_recommendations(video_metadata, recommendations, title):
    """可视化推荐结果"""
    print(f"\n{title}:")
    print(f"  视频信息: {video_metadata.get('category', '未知')}类, " 
          f"{video_metadata.get('duration', 0)}秒, "
          f"{video_metadata.get('aspect_ratio', '未知')}比例")
    
    print("  推荐操作:")
    for i, rec in enumerate(recommendations[:5], 1):
        # 确保操作名称是字符串
        action_str = str(rec['action'])
        print(f"    {i}. {action_str} (置信度: {rec['confidence']:.2f})")
        print(f"       理由: {rec['reason']}")