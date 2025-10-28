from collections import defaultdict

class PreferenceModel:
    """
    用户偏好分析模型
    """
    
    def __init__(self):
        self.action_weights = defaultdict(float)
        self.parameter_preferences = defaultdict(lambda: defaultdict(list))
    
    def calculate_preferences(self, operations):
        """计算用户偏好"""
        preferences = {
            'frequent_actions': {},
            'parameter_tendencies': {},
            'action_correlations': defaultdict(dict),
            'temporal_patterns': {},
            # 新增：效果偏好与上下文偏好（在不改数据格式前提下由启发式推断）
            'effect_tendencies': defaultdict(float),
            'effect_to_actions': defaultdict(lambda: defaultdict(float)),
            'effect_to_actions_counts': defaultdict(lambda: defaultdict(float)),
            'action_to_effects': defaultdict(lambda: defaultdict(float)),
            'action_to_effects_counts': defaultdict(lambda: defaultdict(float)),
            'contextual_preferences': defaultdict(lambda: defaultdict(float))  # key为上下文bucket，value为动作权重
        }
        
        # 计算操作频率（带时间衰减）
        total_operations = len(operations)
        for i, op in enumerate(operations):
            # 时间衰减权重：最近的操作权重更高
            weight = 1.0 + (total_operations - i) * 0.05
            action = op['action']
            preferences['frequent_actions'][action] = \
                preferences['frequent_actions'].get(action, 0) + weight
            
            # 参数倾向分析
            if 'parameters' in op:
                self._analyze_parameters(preferences, action, op['parameters'], weight)
            
            # 操作关联分析
            if i > 0:
                prev_action = operations[i-1]['action']
                preferences['action_correlations'][prev_action][action] = \
                    preferences['action_correlations'][prev_action].get(action, 0) + 1

            # 新增：效果推断（基于启发式）
            inferred_effects = self._infer_effects_from_operation(op)
            success_multiplier = float(op.get('success_metric', 0.8))  # 若无则给个中等成功系数
            for effect in inferred_effects:
                preferences['effect_tendencies'][effect] += weight * success_multiplier
                preferences['effect_to_actions'][effect][action] += weight * success_multiplier
                preferences['effect_to_actions_counts'][effect][action] += 1.0  # 样本量按条计数
                preferences['action_to_effects'][action][effect] += weight * success_multiplier
                preferences['action_to_effects_counts'][action][effect] += 1.0

            # 新增：上下文条件偏好
            context_bucket = self._bucketize_context(op.get('video_context', {}))
            if context_bucket:
                preferences['contextual_preferences'][context_bucket][action] += weight
        
        # 归一化频率
        total_weight = sum(preferences['frequent_actions'].values())
        preferences['frequent_actions'] = {
            action: freq/total_weight 
            for action, freq in preferences['frequent_actions'].items()
        }
        
        # 计算参数倾向的统计值
        self._calculate_parameter_statistics(preferences)

        # 归一化效果与上下文偏好分布
        if preferences['effect_tendencies']:
            total_effect = sum(preferences['effect_tendencies'].values())
            for k in list(preferences['effect_tendencies'].keys()):
                preferences['effect_tendencies'][k] = preferences['effect_tendencies'][k] / total_effect if total_effect > 0 else 0.0
        # 归一化映射
        for effect, actions_map in preferences['effect_to_actions'].items():
            s = sum(actions_map.values()) or 1.0
            for a in list(actions_map.keys()):
                actions_map[a] = actions_map[a] / s
        for action, effects_map in preferences['action_to_effects'].items():
            s = sum(effects_map.values()) or 1.0
            for e in list(effects_map.keys()):
                effects_map[e] = effects_map[e] / s
        # 上下文归一化
        for ctx, actions_map in preferences['contextual_preferences'].items():
            s = sum(actions_map.values()) or 1.0
            for a in list(actions_map.keys()):
                actions_map[a] = actions_map[a] / s
        
        return preferences
    
    def _analyze_parameters(self, preferences, action, parameters, weight):
        """分析参数倾向"""
        if action not in preferences['parameter_tendencies']:
            preferences['parameter_tendencies'][action] = {}
        
        for param, value in parameters.items():
            if param not in preferences['parameter_tendencies'][action]:
                preferences['parameter_tendencies'][action][param] = {
                    'values': [],
                    'weights': []
                }
            
            preferences['parameter_tendencies'][action][param]['values'].append(value)
            preferences['parameter_tendencies'][action][param]['weights'].append(weight)
    
    def _calculate_parameter_statistics(self, preferences):
        """计算参数统计值"""
        for action, params in preferences['parameter_tendencies'].items():
            for param, data in params.items():
                values = data['values']
                weights = data['weights']
                
                # 对于数值型参数，计算加权平均值
                if all(isinstance(v, (int, float)) for v in values):
                    weighted_sum = sum(v * w for v, w in zip(values, weights))
                    total_weight = sum(weights)
                    preferences['parameter_tendencies'][action][param]['average'] = \
                        weighted_sum / total_weight if total_weight > 0 else 0
                
                # 对于类别型参数，计算频率分布
                else:
                    value_counts = {}
                    for i, value in enumerate(values):
                        # 处理不可哈希的值（如列表、字典等）
                        try:
                            # 尝试直接使用值作为键
                            value_counts[value] = value_counts.get(value, 0) + weights[i]
                        except TypeError:
                            # 如果值不可哈希（如列表、字典），转换为字符串
                            value_key = str(value)
                            value_counts[value_key] = value_counts.get(value_key, 0) + weights[i]
                    
                    # 找到最常用的值
                    if value_counts:
                        preferred_value = max(value_counts.items(), key=lambda x: x[1])
                        preferences['parameter_tendencies'][action][param]['preferred'] = \
                            preferred_value[0]
                        preferences['parameter_tendencies'][action][param]['confidence'] = \
                            preferred_value[1] / sum(value_counts.values())

    def _infer_effects_from_operation(self, op):
        """基于现有operation的字段进行启发式效果推断，不修改数据格式。
        返回效果标签列表，例如 ['rhythm_boost', 'warm', 'info_highlight']。
        """
        effects = []
        action = op.get('action', '')
        params = op.get('parameters', {}) or {}
        vc = op.get('video_context', {}) or {}

        # 音乐相关启发：music_track/volume
        music_track = str(params.get('music_track', '')).lower()
        volume = params.get('volume') if isinstance(params.get('volume'), (int, float)) else None
        if action in ['add_music', 'background_music', 'trendy_music'] or music_track:
            if any(k in music_track for k in ['ambient', 'calm', 'chill', 'study']):
                effects.append('calm_warmth')
            if any(k in music_track for k in ['orchestral', 'epic']):
                effects.append('epic_emotion')
            if any(k in music_track for k in ['electronic', 'dance', 'upbeat', 'trending', 'viral']):
                effects.append('rhythm_boost')
            # 音量较高偏向强化情绪或节奏
            if volume is not None and volume >= 0.75:
                effects.append('intensify_mood')

        # 剪辑节奏相关：fast_cut/cut_duration/rhythm
        if action == 'fast_cut':
            effects.append('rhythm_boost')
        if str(params.get('rhythm', '')).lower() in ['sync_with_music', 'beat_match']:
            effects.append('audio_video_sync')
        cut_dur = params.get('cut_duration')
        if isinstance(cut_dur, (int, float)) and cut_dur <= 1.2:
            effects.append('speed_up')

        # 慢动作/慢摇
        if action in ['slow_motion', 'slow_pan']:
            effects.append('cinematic_feel')
            effects.append('emphasis')

        # 文本/标注类
        if action in ['text_overlay', 'text_annotation', 'subtitles', 'chapter_markers']:
            effects.append('info_highlight')
            if action == 'subtitles':
                effects.append('clarity')
            if action == 'chapter_markers':
                effects.append('structure')

        # 调色/滤镜类
        filter_name = str(params.get('filter_name', '')).lower()
        if action in ['apply_filter', 'color_grade', 'color_grading', 'color_correction', 'film_grain', 'vignette']:
            if 'warm' in filter_name:
                effects.append('warm_tone')
            if any(k in filter_name for k in ['cinematic', 'vintage', 'sepia']):
                effects.append('style_consistency')
            # 对比度/饱和度变化可能对应强调/风格统一
            if any(k in params for k in ['contrast', 'saturation', 'highlights', 'midtones', 'shadows']):
                effects.append('visual_emphasis')
            if 'bright' in filter_name:
                effects.append('brightness_boost')
            if 'dramatic' in filter_name or 'vibrant' in filter_name:
                effects.append('color_vividness')

        # 画面裁切/构图
        if action == 'crop':
            effects.append('framing_refinement')
            effects.append('format_fit')

        # 垂直相关过渡
        if action in ['vertical_transition']:
            effects.append('vertical_flow')

        # 上下文辅助：短视频类常追求节奏/吸引；教程类追求清晰/信息突出
        category = str(vc.get('category', '')).lower()
        if category in ['short', 'social_media']:
            effects.append('engagement')
            effects.append('rhythm_boost')
        if category in ['tutorial', 'educational', 'interview']:
            effects.append('clarity')
            effects.append('info_highlight')
        if category in ['cinematic']:
            effects.append('cinematic_feel')

        # 音频处理
        if action in ['split_audio']:
            effects.append('audio_control')
            effects.append('audio_clarity')
        if action in ['noise_reduction']:
            effects.append('audio_cleanliness')
            effects.append('audio_clarity')
        if action in ['voice_over']:
            effects.append('narrative_guidance')
            effects.append('clarity')

        # 时间操作
        if action in ['time_lapse']:
            effects.append('time_compression')
            effects.append('energy_increase')

        # 机位/稳定
        if action in ['stabilize']:
            effects.append('stability')
            effects.append('professionalism')

        # 过渡/节奏
        if action in ['quick_transition']:
            effects.append('flow_smoothness')
            effects.append('pacing')
        if action in ['fast_cut']:
            effects.append('pacing')

        # 去重
        return list(dict.fromkeys(effects))

    def _bucketize_context(self, vc):
        """将上下文聚类成粗粒度bucket，便于统计条件偏好。"""
        if not vc:
            return None
        try:
            duration = vc.get('duration', 0) or 0
            if duration <= 20:
                dur_b = 'dur<=20'
            elif duration <= 60:
                dur_b = '20<dur<=60'
            elif duration <= 180:
                dur_b = '60<dur<=180'
            else:
                dur_b = 'dur>180'
            category = str(vc.get('category', 'unknown')).lower()
            aspect = str(vc.get('aspect_ratio', 'unknown')).lower()
            return f"{category}|{aspect}|{dur_b}"
        except Exception:
            return None