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
            "frequent_actions": {},
            "parameter_tendencies": {},
            "action_correlations": defaultdict(dict),
            "temporal_patterns": {},
            "effect_tendencies": defaultdict(float),
            "effect_to_actions": defaultdict(lambda: defaultdict(float)),
            "effect_to_actions_counts": defaultdict(lambda: defaultdict(float)),
            "action_to_effects": defaultdict(lambda: defaultdict(float)),
            "action_to_effects_counts": defaultdict(lambda: defaultdict(float)),
            "contextual_preferences": defaultdict(lambda: defaultdict(float)),
        }

        total_operations = len(operations)
        for i, op in enumerate(operations):
            weight = 1.0 + (total_operations - i) * 0.05
            action = op["action"]
            preferences["frequent_actions"][action] = (
                preferences["frequent_actions"].get(action, 0) + weight
            )

            if "parameters" in op:
                self._analyze_parameters(preferences, action, op["parameters"], weight)

            if i > 0:
                prev_action = operations[i - 1]["action"]
                preferences["action_correlations"][prev_action][action] = (
                    preferences["action_correlations"][prev_action].get(action, 0) + 1
                )

            inferred_effects = self._infer_effects_from_operation(op)
            success_multiplier = float(op.get("success_metric", 0.8))
            for effect in inferred_effects:
                preferences["effect_tendencies"][effect] += weight * success_multiplier
                preferences["effect_to_actions"][effect][action] += weight * success_multiplier
                preferences["effect_to_actions_counts"][effect][action] += 1.0
                preferences["action_to_effects"][action][effect] += weight * success_multiplier
                preferences["action_to_effects_counts"][action][effect] += 1.0

            context_bucket = self._bucketize_context(op.get("video_context", {}))
            if context_bucket:
                preferences["contextual_preferences"][context_bucket][action] += weight

        total_weight = sum(preferences["frequent_actions"].values())
        if total_weight > 0:
            preferences["frequent_actions"] = {
                action: freq / total_weight for action, freq in preferences["frequent_actions"].items()
            }

        self._calculate_parameter_statistics(preferences)

        if preferences["effect_tendencies"]:
            total_effect = sum(preferences["effect_tendencies"].values())
            if total_effect > 0:
                for key in list(preferences["effect_tendencies"].keys()):
                    preferences["effect_tendencies"][key] = preferences["effect_tendencies"][key] / total_effect

        for effect, actions_map in preferences["effect_to_actions"].items():
            s_val = sum(actions_map.values()) or 1.0
            for a_key in list(actions_map.keys()):
                actions_map[a_key] = actions_map[a_key] / s_val
        for action, effects_map in preferences["action_to_effects"].items():
            s_val = sum(effects_map.values()) or 1.0
            for e_key in list(effects_map.keys()):
                effects_map[e_key] = effects_map[e_key] / s_val

        for ctx, actions_map in preferences["contextual_preferences"].items():
            s_val = sum(actions_map.values()) or 1.0
            for a_key in list(actions_map.keys()):
                actions_map[a_key] = actions_map[a_key] / s_val

        return preferences

    def _analyze_parameters(self, preferences, action, parameters, weight):
        """分析参数倾向"""
        if action not in preferences["parameter_tendencies"]:
            preferences["parameter_tendencies"][action] = {}

        for param, value in parameters.items():
            if param not in preferences["parameter_tendencies"][action]:
                preferences["parameter_tendencies"][action][param] = {
                    "values": [],
                    "weights": [],
                }

            preferences["parameter_tendencies"][action][param]["values"].append(value)
            preferences["parameter_tendencies"][action][param]["weights"].append(weight)

    def _calculate_parameter_statistics(self, preferences):
        """计算参数统计值"""
        for action, params in preferences["parameter_tendencies"].items():
            for param, data in params.items():
                values = data["values"]
                weights = data["weights"]

                if all(isinstance(v, (int, float)) for v in values):
                    weighted_sum = sum(v * w for v, w in zip(values, weights))
                    total_weight = sum(weights)
                    preferences["parameter_tendencies"][action][param]["average"] = (
                        weighted_sum / total_weight if total_weight > 0 else 0
                    )
                else:
                    value_counts = {}
                    for i, value in enumerate(values):
                        try:
                            value_counts[value] = value_counts.get(value, 0) + weights[i]
                        except TypeError:
                            value_key = str(value)
                            value_counts[value_key] = value_counts.get(value_key, 0) + weights[i]

                    if value_counts:
                        preferred_value = max(value_counts.items(), key=lambda x: x[1])
                        preferences["parameter_tendencies"][action][param]["preferred"] = preferred_value[0]
                        preferences["parameter_tendencies"][action][param]["confidence"] = (
                            preferred_value[1] / sum(value_counts.values())
                        )

    def _infer_effects_from_operation(self, op):
        """
        基于现有operation的字段进行启发式效果推断，不修改数据格式。
        返回效果标签列表。
        """
        effects = []
        action = op.get("action", "")
        params = op.get("parameters", {}) or {}
        vc = op.get("video_context", {}) or {}

        music_track = str(params.get("music_track", "")).lower()
        volume = params.get("volume") if isinstance(params.get("volume"), (int, float)) else None
        if action in ["add_music", "background_music", "trendy_music"] or music_track:
            if any(k in music_track for k in ["ambient", "calm", "chill", "study"]):
                effects.append("calm_warmth")
            if any(k in music_track for k in ["orchestral", "epic"]):
                effects.append("epic_emotion")
            if any(k in music_track for k in ["electronic", "dance", "upbeat", "trending", "viral"]):
                effects.append("rhythm_boost")
            if volume is not None and volume >= 0.75:
                effects.append("intensify_mood")

        if action == "fast_cut":
            effects.append("rhythm_boost")
        if str(params.get("rhythm", "")).lower() in ["sync_with_music", "beat_match"]:
            effects.append("audio_video_sync")
        cut_dur = params.get("cut_duration")
        if isinstance(cut_dur, (int, float)) and cut_dur <= 1.2:
            effects.append("speed_up")

        if action in ["slow_motion", "slow_pan"]:
            effects.append("cinematic_feel")
            effects.append("emphasis")

        if action in ["text_overlay", "text_annotation", "subtitles", "chapter_markers"]:
            effects.append("info_highlight")
            if action == "subtitles":
                effects.append("clarity")
            if action == "chapter_markers":
                effects.append("structure")

        filter_name = str(params.get("filter_name", "")).lower()
        if action in ["apply_filter", "color_grade", "color_grading", "color_correction", "film_grain", "vignette"]:
            if "warm" in filter_name:
                effects.append("warm_tone")
            if any(k in filter_name for k in ["cinematic", "vintage", "sepia"]):
                effects.append("style_consistency")
            if any(k in params for k in ["contrast", "saturation", "highlights", "midtones", "shadows"]):
                effects.append("visual_emphasis")
            if "bright" in filter_name:
                effects.append("brightness_boost")

        if action in ["stabilize", "anti_shake"]:
            effects.append("smooth_motion")

        camera_move = str(vc.get("camera_movement", "")).lower()
        if "handheld" in camera_move:
            effects.append("dynamic_storytelling")
        if "gimbal" in camera_move:
            effects.append("smooth_motion")

        lighting = str(vc.get("lighting", "")).lower()
        if "low" in lighting or "night" in lighting:
            effects.append("denoise")
        if "studio" in lighting or "day" in lighting:
            effects.append("clear_focus")

        if action in ["transitions", "apply_transition"]:
            transition_type = str(params.get("transition_type", "")).lower()
            if any(k in transition_type for k in ["fade", "crossfade"]):
                effects.append("smooth_transition")
            elif any(k in transition_type for k in ["zoom", "spin"]):
                effects.append("dynamic_transition")
            else:
                effects.append("basic_transition")

        if action in ["add_b_roll", "cutaway"]:
            effects.append("story_enhancement")

        if action in ["increase_contrast", "highlight_subject"]:
            effects.append("subject_focus")

        return effects

    def _bucketize_context(self, context):
        """将上下文信息归入桶，以便统计偏好"""
        if not context:
            return None

        bucket_parts = []
        category = context.get("category")
        if category:
            bucket_parts.append(f"category:{category}")

        target_platform = context.get("platform")
        if target_platform:
            bucket_parts.append(f"platform:{target_platform}")

        duration = context.get("duration")
        if isinstance(duration, (int, float)):
            if duration < 30:
                bucket_parts.append("duration:short")
            elif duration < 90:
                bucket_parts.append("duration:medium")
            else:
                bucket_parts.append("duration:long")

        orientation = context.get("orientation")
        if orientation:
            bucket_parts.append(f"orientation:{orientation}")

        return "|".join(bucket_parts) if bucket_parts else None
