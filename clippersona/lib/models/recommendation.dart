/// 推荐操作模型
class Recommendation {
  final String action;
  final double score;
  final String source;
  final double confidence;
  final String reason;

  Recommendation({
    required this.action,
    required this.score,
    required this.source,
    required this.confidence,
    required this.reason,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      action: json['action'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
      source: json['source'] ?? '',
      confidence: (json['confidence'] ?? 0).toDouble(),
      reason: json['reason'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'action': action,
      'score': score,
      'source': source,
      'confidence': confidence,
      'reason': reason,
    };
  }

  /// 获取置信度百分比
  int get confidencePercent => (confidence * 100).round();

  /// 获取推荐来源的友好名称
  String get sourceName {
    switch (source) {
      case 'preference':
        return '用户偏好';
      case 'sequence':
        return '操作序列';
      case 'workflow':
        return '工作流';
      case 'context':
        return '视频类型';
      default:
        return source;
    }
  }

  /// 获取操作的友好名称
  String get actionDisplayName {
    final actionNames = {
      'trim': '裁剪',
      'color_grading': '调色',
      'add_music': '添加音乐',
      'fast_cut': '快剪',
      'text_overlay': '添加字幕',
      'slow_motion': '慢动作',
      'filters': '滤镜',
      'transitions': '转场',
      'vertical_crop': '竖屏裁剪',
      'stabilize': '防抖',
      'subtitle_gpt': '智能字幕',
      'export': '导出',
    };
    return actionNames[action] ?? action;
  }
}

/// 工作流模板模型
class WorkflowTemplate {
  final List<String> sequence;
  final int frequency;
  final double confidence;

  WorkflowTemplate({
    required this.sequence,
    required this.frequency,
    required this.confidence,
  });

  factory WorkflowTemplate.fromJson(Map<String, dynamic> json) {
    return WorkflowTemplate(
      sequence: List<String>.from(json['sequence'] ?? []),
      frequency: json['frequency'] ?? 0,
      confidence: (json['confidence'] ?? 0).toDouble(),
    );
  }

  /// 获取工作流名称
  String get name {
    // 根据序列内容生成名称
    if (sequence.contains('trim') &&
        sequence.contains('color_grading') &&
        sequence.contains('add_music')) {
      return '快速Vlog制作';
    } else if (sequence.contains('text_overlay') && sequence.contains('trim')) {
      return '教程视频制作';
    } else if (sequence.contains('fast_cut') &&
        sequence.contains('add_music')) {
      return '短视频剪辑';
    }
    return '自定义工作流';
  }

  /// 获取工作流步骤的友好名称
  String get stepsDisplay {
    final actionNames = {
      'trim': '裁剪',
      'color_grading': '调色',
      'add_music': '音乐',
      'fast_cut': '快剪',
      'text_overlay': '字幕',
      'slow_motion': '慢动作',
      'export': '导出',
    };

    return sequence.map((action) => actionNames[action] ?? action).join(' → ');
  }

  /// 获取置信度百分比
  int get confidencePercent => (confidence * 100).round();
}



