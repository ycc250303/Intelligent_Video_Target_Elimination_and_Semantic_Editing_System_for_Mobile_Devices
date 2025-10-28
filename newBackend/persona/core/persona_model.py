import json
import os
from datetime import datetime
from typing import Dict, List, Any

from .pattern_analyzer import OperationPatternAnalyzer
from .preference_model import PreferenceModel
from .recommender import ContextAwareRecommender


class VideoEditingPersona:
    """
    视频剪辑人格模型主类
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.pattern_analyzer = OperationPatternAnalyzer(n=3)
        self.preference_model = PreferenceModel()
        self.recommender = ContextAwareRecommender()
        self.user_persona = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_operations": 0,
            "preferences": {},
            "patterns": {},
            "workflow_templates": [],
            "statistics": {},
        }

    def train(self, operations_data: List[Dict[str, Any]]):
        """训练用户人格模型"""
        if not operations_data:
            raise ValueError("操作数据不能为空")

        self.user_persona["total_operations"] = len(operations_data)
        self.user_persona["updated_at"] = datetime.now().isoformat()

        self.pattern_analyzer.learn_sequences(operations_data)
        preferences = self.preference_model.calculate_preferences(operations_data)
        workflow_templates = self._extract_workflow_templates(operations_data)
        statistics = self._calculate_statistics(operations_data)

        self.user_persona.update(
            {
                "preferences": preferences,
                "patterns": self.pattern_analyzer.get_patterns(),
                "workflow_templates": workflow_templates,
                "statistics": statistics,
            }
        )

    def predict_operations(self, video_metadata):
        """预测用户可能执行的操作"""
        return self.recommender.recommend_operations(self.user_persona, video_metadata)

    def get_persona(self):
        """获取用户人格数据"""
        return self.user_persona.copy()

    def save_persona(self, file_path: str):
        """保存用户人格到文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.user_persona, f, indent=2, ensure_ascii=False)

    def load_persona(self, file_path: str):
        """从文件加载用户人格"""
        with open(file_path, "r", encoding="utf-8") as f:
            self.user_persona = json.load(f)

    def _extract_workflow_templates(self, operations_data: List[Dict[str, Any]]):
        """提取常见的工作流模板"""
        workflows = []
        sequences = {}
        sequence_length = 4

        for i in range(len(operations_data) - sequence_length + 1):
            sequence = tuple(op["action"] for op in operations_data[i : i + sequence_length])
            sequences[sequence] = sequences.get(sequence, 0) + 1

        top_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)[:5]

        for sequence, frequency in top_sequences:
            if frequency > 1:
                workflows.append(
                    {
                        "sequence": list(sequence),
                        "frequency": frequency,
                        "confidence": min(frequency / len(operations_data) * 10, 1.0),
                    }
                )

        return workflows

    def _calculate_statistics(self, operations_data: List[Dict[str, Any]]):
        """计算统计信息"""
        if not operations_data:
            return {}

        action_counts = {}
        total_duration = 0
        video_categories = {}

        for op in operations_data:
            action = op["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

            if "parameters" in op and isinstance(op["parameters"], dict):
                duration_val = op["parameters"].get("duration")
                if isinstance(duration_val, (int, float)):
                    total_duration += duration_val

            if "video_context" in op and isinstance(op["video_context"], dict):
                category = op["video_context"].get("category")
                if category:
                    video_categories[category] = video_categories.get(category, 0) + 1

        total_actions = len(operations_data)
        if total_actions == 0:
            return {}

        action_frequencies = {action: count / total_actions for action, count in action_counts.items()}

        return {
            "action_frequencies": action_frequencies,
            "most_common_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_editing_duration": total_duration,
            "preferred_categories": sorted(video_categories.items(), key=lambda x: x[1], reverse=True)[:3],
            "average_operations_per_session": self._calculate_avg_operations_per_session(operations_data),
            "action_stage_distribution": self._compute_action_stage_distribution(operations_data),
        }

    def _calculate_avg_operations_per_session(self, operations_data: List[Dict[str, Any]]):
        """计算每次编辑会话的平均操作数"""
        if not operations_data:
            return 0

        sessions: List[List[Dict[str, Any]]] = []
        current_session: List[Dict[str, Any]] = []

        for i, op in enumerate(operations_data):
            if not current_session:
                current_session.append(op)
                continue

            try:
                prev_time_str = operations_data[i - 1]["timestamp"].replace("Z", "+00:00")
                curr_time_str = op["timestamp"].replace("Z", "+00:00")

                prev_time = datetime.fromisoformat(prev_time_str)
                curr_time = datetime.fromisoformat(curr_time_str)
                time_diff = (curr_time - prev_time).total_seconds() / 60

                if time_diff < 60:
                    current_session.append(op)
                else:
                    sessions.append(current_session)
                    current_session = [op]
            except Exception:
                current_session.append(op)

        if current_session:
            sessions.append(current_session)

        if not sessions:
            return len(operations_data)

        total_operations = sum(len(session) for session in sessions)
        return total_operations / len(sessions)

    def _compute_action_stage_distribution(self, operations_data: List[Dict[str, Any]]):
        """统计用户在会话流程中的动作阶段分布"""
        if not operations_data:
            return {}

        stages = {"early": 0, "middle": 0, "late": 0}
        total_operations = len(operations_data)

        for idx, op in enumerate(operations_data):
            position = idx / total_operations
            if position < 0.33:
                stages["early"] += 1
            elif position < 0.66:
                stages["middle"] += 1
            else:
                stages["late"] += 1

        return {stage: count / total_operations for stage, count in stages.items()}
