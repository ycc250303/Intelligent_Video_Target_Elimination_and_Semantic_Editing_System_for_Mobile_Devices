class ContextAwareRecommender:
    """
    基于用户偏好和上下文信息的操作推荐系统
    """

    def __init__(self):
        self.context_priority = {
            "short": ["trim", "vertical_crop", "add_text", "add_music", "filters"],
            "medium": ["color_grading", "transitions", "text_overlay"],
            "long": ["story_enhancement", "multi_scene_edit", "advanced_color"],
        }
        self.video_context_rules = {
            "vlog": ["trim_silence", "color_grading", "add_bgm", "subtitle_gpt"],
            "travel": ["color_correction", "slow_motion", "transition_effects"],
            "tutorial": ["screen_recording", "text_overlay", "highlight_effect"],
            "short": ["fast_cut", "beat_sync", "viral_effects"],
        }

    def recommend_operations(self, user_persona, video_metadata):
        """生成个性化操作推荐"""
        if not user_persona:
            return []

        user_preferred = self._get_user_preferred_actions(user_persona)
        sequence_suggestions = self._predict_from_sequences(user_persona)
        workflow_suggestions = self._suggest_from_workflows(user_persona, video_metadata)
        context_actions = self._match_video_context(video_metadata)

        combined = []
        seen_actions = set()

        for action_source in [
            ("preference", user_preferred),
            ("sequence", sequence_suggestions),
            ("workflow", workflow_suggestions),
            ("context", context_actions),
        ]:
            source_name, action_list = action_source
            for action in action_list:
                if isinstance(action, tuple):
                    action_name, score = action
                else:
                    action_name, score = action, 0.5

                if action_name not in seen_actions:
                    seen_actions.add(action_name)
                    combined.append(
                        {
                            "action": action_name,
                            "score": score,
                            "source": source_name,
                            "confidence": self._calculate_confidence(action_name, user_persona, video_metadata),
                            "reason": self._get_recommendation_reason(action_name, user_persona, video_metadata),
                        }
                    )
        combined.sort(key=lambda x: x["confidence"], reverse=True)
        return combined[:10]

    def _get_user_preferred_actions(self, user_persona):
        preferences = user_persona.get("preferences", {})
        frequent_actions = preferences.get("frequent_actions", {})
        return sorted(frequent_actions.items(), key=lambda x: x[1], reverse=True)[:5]

    def _predict_from_sequences(self, user_persona):
        patterns = user_persona.get("patterns", {})
        transition_matrix = patterns.get("transition_matrix", {})

        suggestions = []
        for sequence, next_actions in transition_matrix.items():
            top_action = max(next_actions.items(), key=lambda x: x[1])
            suggestions.append(top_action)
        return sorted(suggestions, key=lambda x: x[1], reverse=True)[:5]

    def _suggest_from_workflows(self, user_persona, video_metadata):
        workflows = user_persona.get("workflow_templates", [])
        if not workflows:
            return []

        suggestions = []
        for workflow in workflows:
            sequence = workflow.get("sequence", [])
            if not sequence:
                continue

            suggestions.append(
                (
                    sequence[0],
                    workflow.get("confidence", 0.5) * self._context_match_score(sequence[0], video_metadata),
                )
            )

        return sorted(suggestions, key=lambda x: x[1], reverse=True)[:5]

    def _match_video_context(self, video_metadata):
        if not video_metadata:
            return []

        context_actions = []
        duration = video_metadata.get("duration", 60)
        category = video_metadata.get("category", "").lower()

        if duration <= 30:
            context_actions.extend(self.context_priority.get("short", []))
        elif duration <= 120:
            context_actions.extend(self.context_priority.get("medium", []))
        else:
            context_actions.extend(self.context_priority.get("long", []))

        if category in self.video_context_rules:
            context_actions.extend(self.video_context_rules[category])

        return [(action, 0.6) for action in context_actions]

    def _context_match_score(self, action, video_metadata):
        if not video_metadata:
            return 1.0
        category = video_metadata.get("category")
        if not category:
            return 1.0
        rules = self.video_context_rules.get(category.lower(), [])
        return 1.2 if action in rules else 1.0

    def _calculate_confidence(self, action, user_persona, video_metadata):
        preferences = user_persona.get("preferences", {})
        frequent_actions = preferences.get("frequent_actions", {})
        preference_score = frequent_actions.get(action, 0)

        patterns = user_persona.get("patterns", {})
        transition_matrix = patterns.get("transition_matrix", {})
        pattern_score = 0
        for sequence, actions in transition_matrix.items():
            if action in actions:
                pattern_score = max(pattern_score, actions[action])

        context_actions = self._match_video_context(video_metadata)
        context_score = max((score for act, score in context_actions if act == action), default=0)

        return min(preference_score * 0.6 + pattern_score * 0.3 + context_score * 0.1 + 0.2, 1.0)

    def _get_recommendation_reason(self, action, user_persona, video_metadata):
        preferences = user_persona.get("preferences", {})

        frequent_actions = preferences.get("frequent_actions", {})
        if action in frequent_actions and frequent_actions[action] > 0.15:
            return f"该操作占用户历史操作的 {frequent_actions[action]*100:.1f}%"

        patterns = user_persona.get("patterns", {})
        transition_matrix = patterns.get("transition_matrix", {})
        for sequence, actions in transition_matrix.items():
            if action in actions and actions[action] > 0.2:
                return f"常见于操作序列: {sequence} -> {action}"

        context_actions = self._match_video_context(video_metadata)
        for act, score in context_actions:
            if act == action:
                if video_metadata:
                    return f"适合 {video_metadata.get('category', '该类型')} 视频 ({score*100:.0f}%)"
                return "匹配当前视频上下文"

        workflows = user_persona.get("workflow_templates", [])
        for workflow in workflows:
            if action in workflow.get("sequence", []):
                return f"来源于常用工作流（置信度 {workflow.get('confidence', 0.5)*100:.0f}%）"

        return "具有潜力提升视频质量"
