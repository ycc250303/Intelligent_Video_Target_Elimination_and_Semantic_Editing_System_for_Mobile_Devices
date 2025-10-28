class OperationPatternAnalyzer:
    """
    操作序列模式分析器
    """
    
    def __init__(self, n=3):
        self.n = n  # n-gram大小
        self.sequence_patterns = {}
        self.transition_matrix = {}
    
    def learn_sequences(self, operations):
        """学习操作序列模式"""
        if len(operations) < self.n:
            return
        
        for i in range(len(operations) - self.n + 1):
            sequence = tuple(op['action'] for op in operations[i:i+self.n])
            next_action = operations[i+self.n]['action'] if i+self.n < len(operations) else None
            
            # 将元组转换为字符串作为键
            sequence_key = "->".join(sequence)
            
            if sequence_key not in self.sequence_patterns:
                self.sequence_patterns[sequence_key] = {}
            
            if next_action:
                self.sequence_patterns[sequence_key][next_action] = \
                    self.sequence_patterns[sequence_key].get(next_action, 0) + 1
        
        # 构建转移概率矩阵
        self._build_transition_matrix()
    
    def _build_transition_matrix(self):
        """构建转移概率矩阵"""
        for sequence, next_actions in self.sequence_patterns.items():
            total = sum(next_actions.values())
            self.transition_matrix[sequence] = {
                action: count/total for action, count in next_actions.items()
            }
    
    def predict_next_actions(self, current_sequence):
        """预测下一个可能执行的操作"""
        if len(current_sequence) < self.n:
            # 如果序列较短，使用缩短的n-gram
            if current_sequence:
                sequence_key = "->".join(current_sequence[-(self.n-1):])
            else:
                sequence_key = ""
        else:
            sequence_key = "->".join(current_sequence[-self.n:])
        
        if sequence_key in self.transition_matrix:
            return sorted(
                self.transition_matrix[sequence_key].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]  # 返回前3个最可能的操作
        
        return []
    
    def get_patterns(self):
        """获取学习到的模式"""
        return {
            "sequence_patterns": self.sequence_patterns,
            "transition_matrix": self.transition_matrix
        }