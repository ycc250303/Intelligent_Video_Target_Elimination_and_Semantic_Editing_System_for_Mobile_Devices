/// 操作记录模型 - 记录用户指令和对应的函数调用
class OperationRecord {
  final String userInstruction; // 用户输入的指令
  final List<FunctionCall> functionCalls; // 执行的函数调用列表
  final DateTime timestamp; // 操作时间

  OperationRecord({
    required this.userInstruction,
    required this.functionCalls,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// 从JSON创建
  factory OperationRecord.fromJson(Map<String, dynamic> json) {
    return OperationRecord(
      userInstruction: json['userInstruction'] as String,
      functionCalls:
          (json['functionCalls'] as List<dynamic>?)
              ?.map((e) => FunctionCall.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'userInstruction': userInstruction,
      'functionCalls': functionCalls.map((e) => e.toJson()).toList(),
      'timestamp': timestamp.toIso8601String(),
    };
  }

  /// 获取显示文本（仅显示用户指令）
  String getDisplayText() {
    return userInstruction;
  }
}

/// 函数调用记录
class FunctionCall {
  final String functionName; // 函数名称
  final Map<String, dynamic> parameters; // 函数参数

  FunctionCall({required this.functionName, required this.parameters});

  /// 从JSON创建
  factory FunctionCall.fromJson(Map<String, dynamic> json) {
    return FunctionCall(
      functionName: json['functionName'] as String,
      parameters: Map<String, dynamic>.from(json['parameters'] as Map),
    );
  }

  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {'functionName': functionName, 'parameters': parameters};
  }

  @override
  String toString() {
    return 'FunctionCall(functionName: $functionName, parameters: $parameters)';
  }
}

