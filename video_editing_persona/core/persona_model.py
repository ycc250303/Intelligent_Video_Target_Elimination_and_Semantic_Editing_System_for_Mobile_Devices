import json
import os
from datetime import datetime
from .pattern_analyzer import OperationPatternAnalyzer
from .preference_model import PreferenceModel
from .recommender import ContextAwareRecommender

class VideoEditingPersona:
    """
    视频剪辑人格模型主类
    """
    
    def __init__(self, user_id="default_user"):
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
            "statistics": {}
        }
    
    def train(self, operations_data):
        """训练用户人格模型"""
        if not operations_data:
            raise ValueError("操作数据不能为空")
        
        self.user_persona["total_operations"] = len(operations_data)
        self.user_persona["updated_at"] = datetime.now().isoformat()
        
        # 1. 学习序列模式
        self.pattern_analyzer.learn_sequences(operations_data)
        
        # 2. 分析偏好
        preferences = self.preference_model.calculate_preferences(operations_data)
        
        # 3. 提取工作流模板
        workflow_templates = self._extract_workflow_templates(operations_data)
        
        # 4. 计算统计信息
        statistics = self._calculate_statistics(operations_data)
        
        # 整合用户人格
        self.user_persona.update({
            "preferences": preferences,
            "patterns": self.pattern_analyzer.get_patterns(),
            "workflow_templates": workflow_templates,
            "statistics": statistics
        })
    
    def predict_operations(self, video_metadata):
        """预测用户可能执行的操作"""
        return self.recommender.recommend_operations(self.user_persona, video_metadata)
    
    def get_persona(self):
        """获取用户人格数据"""
        return self.user_persona.copy()
    
    def save_persona(self, file_path):
        """保存用户人格到文件"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_persona, f, indent=2, ensure_ascii=False)
    
    def load_persona(self, file_path):
        """从文件加载用户人格"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.user_persona = json.load(f)
    
    def _extract_workflow_templates(self, operations_data):
        """提取常见的工作流模板"""
        workflows = []
        
        # 简单的模板提取：找到频繁出现的操作序列
        sequences = {}
        sequence_length = 4
        
        for i in range(len(operations_data) - sequence_length + 1):
            sequence = tuple(op["action"] for op in operations_data[i:i+sequence_length])
            sequences[sequence] = sequences.get(sequence, 0) + 1
        
        # 选择出现频率高的序列作为模板
        top_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for sequence, frequency in top_sequences:
            if frequency > 1:  # 至少出现2次
                workflows.append({
                    "sequence": list(sequence),
                    "frequency": frequency,
                    "confidence": min(frequency / len(operations_data) * 10, 1.0)
                })
        
        return workflows
    
    def _calculate_statistics(self, operations_data):
        """计算统计信息"""
        if not operations_data:
            return {}
        
        # 计算各种操作的频率
        action_counts = {}
        total_duration = 0
        video_categories = {}
        
        for op in operations_data:
            action = op["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
            
            if "parameters" in op and "duration" in op["parameters"]:
                total_duration += op["parameters"]["duration"]
            
            if "video_context" in op and "category" in op["video_context"]:
                category = op["video_context"]["category"]
                video_categories[category] = video_categories.get(category, 0) + 1
        
        # 计算比例
        total_actions = len(operations_data)
        action_frequencies = {action: count/total_actions for action, count in action_counts.items()}
        
        return {
            "action_frequencies": action_frequencies,
            "most_common_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_editing_duration": total_duration,
            "preferred_categories": sorted(video_categories.items(), key=lambda x: x[1], reverse=True)[:3],
            "average_operations_per_session": self._calculate_avg_operations_per_session(operations_data),
            # 新增：统计用户在会话流程中的动作阶段分布（early/middle/late）
            "action_stage_distribution": self._compute_action_stage_distribution(operations_data)
        }
    
    def _calculate_avg_operations_per_session(self, operations_data):
        """计算每次编辑会话的平均操作数"""
        if not operations_data:
            return 0
    
        # 简单实现：假设每次连续操作时间在1小时内的属于同一次会话
        sessions = []
        current_session = []
    
        for i, op in enumerate(operations_data):
            if not current_session:
                current_session.append(op)
                continue
            
            # 检查时间间隔（修复时间解析问题）
            try:
                # 处理时间字符串，移除Z并添加时区信息
                prev_time_str = operations_data[i-1]["timestamp"].replace('Z', '+00:00')
                curr_time_str = op["timestamp"].replace('Z', '+00:00')
            
                prev_time = datetime.fromisoformat(prev_time_str)
                curr_time = datetime.fromisoformat(curr_time_str)
                time_diff = (curr_time - prev_time).total_seconds() / 60  # 分钟
            
                if time_diff < 60:  # 1小时内属于同一次会话
                    current_session.append(op)
                else:
                    sessions.append(current_session)
                    current_session = [op]
            except (ValueError, KeyError) as e:
                # 如果时间解析失败，默认属于同一次会话
                print(f"时间解析错误: {e}，将操作归入当前会话")
                current_session.append(op)
    
        if current_session:
            sessions.append(current_session)
    
        if sessions:
            return sum(len(session) for session in sessions) / len(sessions)
        else:
            return 0

    def _compute_action_stage_distribution(self, operations_data):
        """统计每个动作在会话内出现的位置分布（early/middle/late）。
        不依赖样例格式变更：基于时间顺序将连续<1小时的操作划为同一会话。
        """
        if not operations_data:
            return {}

        # 划分会话
        sessions = []
        current_session = []
        for i, op in enumerate(operations_data):
            if not current_session:
                current_session.append(op)
                continue
            try:
                prev_time_str = operations_data[i-1]["timestamp"].replace('Z', '+00:00')
                curr_time_str = op["timestamp"].replace('Z', '+00:00')
                prev_time = datetime.fromisoformat(prev_time_str)
                curr_time = datetime.fromisoformat(curr_time_str)
                time_diff = (curr_time - prev_time).total_seconds() / 60
                if time_diff < 60:
                    current_session.append(op)
                else:
                    sessions.append(current_session)
                    current_session = [op]
            except (ValueError, KeyError):
                current_session.append(op)
        if current_session:
            sessions.append(current_session)

        # 统计阶段
        stage_counts = {}
        for session in sessions:
            if not session:
                continue
            length = len(session)
            for idx, op in enumerate(session):
                action = op.get("action", "unknown")
                pos = idx / max(length - 1, 1)
                if action not in stage_counts:
                    stage_counts[action] = {"early": 0, "middle": 0, "late": 0}
                if pos <= 0.33:
                    stage_counts[action]["early"] += 1
                elif pos <= 0.66:
                    stage_counts[action]["middle"] += 1
                else:
                    stage_counts[action]["late"] += 1

        # 归一化
        for action, buckets in stage_counts.items():
            total = sum(buckets.values()) or 1
            for k in buckets:
                buckets[k] = buckets[k] / total
        return stage_counts