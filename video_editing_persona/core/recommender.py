class ContextAwareRecommender:
    """
    上下文感知推荐器
    """
    
    def __init__(self):
        # 效果标签中文描述（用于理由展示）
        self.effect_descriptions = {
            'calm_warmth': '温暖/舒缓氛围',
            'epic_emotion': '史诗/宏大情绪',
            'rhythm_boost': '节奏增强/更有律动',
            'intensify_mood': '强化情绪张力',
            'audio_video_sync': '画面与音乐节拍同步',
            'speed_up': '提升节奏速度',
            'cinematic_feel': '电影感',
            'emphasis': '突出重点',
            'info_highlight': '信息突出/清晰表达',
            'clarity': '表达更清晰',
            'warm_tone': '暖色调/温暖基调',
            'style_consistency': '风格统一/一致性增强',
            'visual_emphasis': '视觉强调',
            'engagement': '提升吸引力/互动性',
            'structure': '结构清晰/章节分明',
            'brightness_boost': '亮度提升',
            'color_vividness': '色彩更鲜明',
            'framing_refinement': '构图优化/画面取舍',
            'format_fit': '适配画幅/平台格式',
            'vertical_flow': '竖屏观感/过渡更自然',
            'audio_control': '音轨可控/灵活编辑',
            'audio_cleanliness': '降噪净化',
            'narrative_guidance': '叙事引导/讲解说明',
            'time_compression': '时间压缩/加速讲述',
            'energy_increase': '能量提升/更带感',
            'stability': '画面稳定',
            'professionalism': '专业质感',
            'flow_smoothness': '镜头衔接更顺滑',
            'pacing': '节奏掌控'
        }
        self.video_context_rules = {
            'short_video': {
                'max_duration': 30, 
                'preferred_actions': ['fast_cut', 'trendy_music', 'quick_transition', 'text_overlay']
            },
            'long_video': {
                'min_duration': 180, 
                'preferred_actions': ['slow_pan', 'narration', 'detailed_color_correction', 'chapter_markers']
            },
            'vertical_video': {
                'aspect_ratio': '9:16', 
                'preferred_actions': ['vertical_zoom', 'mobile_optimized_text', 'vertical_transition']
            },
            'vlog': {
                'category': 'vlog',
                'preferred_actions': ['stabilize', 'color_grade', 'background_music', 'subtitles']
            },
            'tutorial': {
                'category': 'tutorial', 
                'preferred_actions': ['zoom_highlight', 'text_annotation', 'slow_motion', 'voice_over']
            }
        }
    
    def recommend_operations(self, user_persona, video_metadata):
        """基于用户人格和视频上下文的推荐"""
        recommendations = []
        
        # 1. 匹配视频上下文
        context_actions = self._match_video_context(video_metadata)
        
        # 2. 用户偏好动作
        user_preferred = self._get_user_preferred_actions(user_persona)
        
        # 3. 序列模式预测
        sequence_suggestions = self._predict_from_sequences(user_persona)
        
        # 4. 工作流模板推荐
        workflow_suggestions = self._suggest_from_workflows(user_persona, video_metadata)
        
        # 合并和排序推荐结果
        all_suggestions = self._merge_recommendations(
            context_actions, user_preferred, sequence_suggestions, workflow_suggestions
        )
        
        # 添加置信度评分
        for action in all_suggestions:
            confidence = self._calculate_confidence(action, user_persona, video_metadata)
            recommendations.append({
                'action': action,
                'confidence': confidence,
                'reason': self._get_recommendation_reason(action, user_persona, video_metadata)
            })
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:8]  # 返回前8个推荐
    
    def _match_video_context(self, video_metadata):
        """匹配视频上下文规则"""
        matched_actions = []
        
        for rule_name, rule in self.video_context_rules.items():
            match = True
            
            for key, value in rule.items():
                if key in ['preferred_actions']:
                    continue
                    
                if key in video_metadata:
                    if key == 'max_duration' and video_metadata.get('duration', 0) > value:
                        match = False
                    elif key == 'min_duration' and video_metadata.get('duration', 0) < value:
                        match = False
                    elif key == 'aspect_ratio' and video_metadata.get('aspect_ratio') != value:
                        match = False
                    elif key == 'category' and video_metadata.get('category') != value:
                        match = False
            
            if match:
                matched_actions.extend(rule['preferred_actions'])
        
        return list(set(matched_actions))  # 去重
    
    def _get_user_preferred_actions(self, user_persona):
        """获取用户偏好动作"""
        preferences = user_persona.get('preferences', {})
        frequent_actions = preferences.get('frequent_actions', {})
        
        # 返回频率最高的动作
        return sorted(frequent_actions.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _predict_from_sequences(self, user_persona):
        """从序列模式预测"""
        # 这里可以基于用户最近的操作序列进行预测
        # 简化实现：返回常见序列中的下一个动作
        patterns = user_persona.get('patterns', {})
        sequence_patterns = patterns.get('sequence_patterns', {})
        
        suggestions = []
        for sequence, next_actions in sequence_patterns.items():
            for action, count in next_actions.items():
                suggestions.append(action)
        
        return list(set(suggestions))[:5]  # 去重并取前5个
    
    def _suggest_from_workflows(self, user_persona, video_metadata):
        """从工作流模板推荐"""
        workflows = user_persona.get('workflow_templates', [])
        suggestions = []
        
        for workflow in workflows:
            # 只推荐完整的工作流中的动作
            suggestions.extend(workflow['sequence'])
        
        return list(set(suggestions))
    
    def _merge_recommendations(self, *suggestion_lists):
        """合并推荐结果"""
        merged = []
        
        for suggestions in suggestion_lists:
            if isinstance(suggestions, list):
                for item in suggestions:
                    if isinstance(item, tuple):
                        merged.append(item[0])  # 如果是(动作,频率)元组，取动作
                    else:
                        merged.append(item)
            elif isinstance(suggestions, dict):
                merged.extend(suggestions.keys())
        
        return list(set(merged))
    
    def _calculate_confidence(self, action, user_persona, video_metadata):
        """计算推荐置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于用户偏好
        preferences = user_persona.get('preferences', {})
        frequent_actions = preferences.get('frequent_actions', {})
        if action in frequent_actions:
            confidence += frequent_actions[action] * 0.3
        
        # 基于视频上下文匹配
        context_actions = self._match_video_context(video_metadata)
        if action in context_actions:
            confidence += 0.2
        
        # 基于序列模式
        patterns = user_persona.get('patterns', {})
        sequence_patterns = patterns.get('sequence_patterns', {})
        for sequence in sequence_patterns:
            if action in sequence_patterns[sequence]:
                confidence += 0.1

        # 新增：基于效果目标与动作映射
        effect_to_actions = preferences.get('effect_to_actions', {})
        target_effects = self._infer_target_effects(video_metadata)
        if effect_to_actions and target_effects:
            for eff in target_effects:
                actions_map = effect_to_actions.get(eff, {})
                score = actions_map.get(action, 0.0)
                if score:
                    confidence += min(score * 0.25, 0.25)

        # 新增：基于上下文条件偏好
        contextual_preferences = preferences.get('contextual_preferences', {})
        ctx_bucket = self._bucketize_context(video_metadata)
        if ctx_bucket and ctx_bucket in contextual_preferences:
            ctx_score = contextual_preferences[ctx_bucket].get(action, 0.0)
            confidence += min(ctx_score * 0.25, 0.25)
        
        return min(confidence, 1.0)  # 确保不超过1.0
    
    def _get_recommendation_reason(self, action, user_persona, video_metadata):
        """生成推荐理由"""
        reasons = []
        
        # 检查用户偏好
        preferences = user_persona.get('preferences', {})
        frequent_actions = preferences.get('frequent_actions', {})
        if action in frequent_actions and frequent_actions[action] > 0.1:
            reasons.append("您经常使用此操作")
        
        # 检查视频上下文
        context_actions = self._match_video_context(video_metadata)
        if action in context_actions:
            reasons.append("适合此类视频")
        
        # 检查序列模式
        patterns = user_persona.get('patterns', {})
        sequence_patterns = patterns.get('sequence_patterns', {})
        for sequence in sequence_patterns:
            if action in sequence_patterns[sequence]:
                reasons.append("常在此操作序列中使用")
                break

        # 新增：效果目标一致性
        effect_to_actions = preferences.get('effect_to_actions', {})
        effect_to_actions_counts = preferences.get('effect_to_actions_counts', {})
        target_effects = self._infer_target_effects(video_metadata)
        matched_effects = []
        matched_counts = []
        for eff in target_effects:
            if action in effect_to_actions.get(eff, {}):
                matched_effects.append(eff)
                cnt = int(effect_to_actions_counts.get(eff, {}).get(action, 0))
                matched_counts.append(cnt)
        if matched_effects:
            cn = [self.effect_descriptions.get(e, e) for e in matched_effects]
            pairs = []
            for i, e in enumerate(matched_effects):
                c_desc = cn[i]
                count_str = f", 样本量:{matched_counts[i]}" if i < len(matched_counts) else ""
                pairs.append(f"{e}（{c_desc}{count_str}）")
            reasons.append("有助于实现预期效果: " + ", ".join(pairs))

        # 新增：上下文条件偏好
        contextual_preferences = preferences.get('contextual_preferences', {})
        ctx_bucket = self._bucketize_context(video_metadata)
        if ctx_bucket and ctx_bucket in contextual_preferences and action in contextual_preferences[ctx_bucket]:
            score = contextual_preferences[ctx_bucket].get(action, 0.0)
            reasons.append(f"符合您在此上下文中的常用偏好(置信:{score:.2f})")

        # 新增：参数建议区间
        param_suggestion = self._suggest_parameters_for_action(action, preferences)
        if param_suggestion:
            reasons.append(f"参数建议: {param_suggestion}")
        
        return "；".join(reasons) if reasons else "基于您的剪辑习惯推荐"

    def _suggest_parameters_for_action(self, action, preferences):
        """根据 parameter_tendencies 生成简易参数建议范围/默认值。
        - 数值型：给出平均值±简易范围（使用方差不可得时，给±20%区间）
        - 类别型：给出最偏好类别
        """
        pt = preferences.get('parameter_tendencies', {})
        if action not in pt:
            return ""
        suggestions = []
        for param, data in pt[action].items():
            if 'average' in data:
                avg = data['average']
                low = avg * 0.8
                high = avg * 1.2
                suggestions.append(f"{param}≈{avg:.2f}[{low:.2f}-{high:.2f}]")
            elif 'preferred' in data:
                pref = data.get('preferred')
                conf = data.get('confidence', 0.0)
                suggestions.append(f"{param}={pref}(置信:{conf:.2f})")
        return ", ".join(suggestions)

    def _infer_target_effects(self, video_metadata):
        """基于视频元数据推断目标效果（启发式）。"""
        effects = []
        if not isinstance(video_metadata, dict):
            return effects
        duration = video_metadata.get('duration', 0) or 0
        aspect = str(video_metadata.get('aspect_ratio', '')).lower()
        category = str(video_metadata.get('category', '')).lower()

        if duration <= 20 or category in ['short', 'social_media']:
            effects.extend(['engagement', 'rhythm_boost'])
        if duration >= 180 or category in ['tutorial', 'educational', 'interview']:
            effects.extend(['clarity', 'info_highlight'])
        if category in ['cinematic'] or aspect == '21:9':
            effects.append('cinematic_feel')
        if category in ['vlog', 'travel']:
            effects.append('warm_tone')
        return list(dict.fromkeys(effects))

    def _bucketize_context(self, video_metadata):
        """与偏好模型一致的上下文分桶。"""
        if not isinstance(video_metadata, dict):
            return None
        try:
            duration = video_metadata.get('duration', 0) or 0
            if duration <= 20:
                dur_b = 'dur<=20'
            elif duration <= 60:
                dur_b = '20<dur<=60'
            elif duration <= 180:
                dur_b = '60<dur<=180'
            else:
                dur_b = 'dur>180'
            category = str(video_metadata.get('category', 'unknown')).lower()
            aspect = str(video_metadata.get('aspect_ratio', 'unknown')).lower()
            return f"{category}|{aspect}|{dur_b}"
        except Exception:
            return None