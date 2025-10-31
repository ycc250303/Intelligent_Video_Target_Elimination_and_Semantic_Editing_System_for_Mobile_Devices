import 'package:flutter/material.dart';
import '../../../models/operation_record.dart';

/// Persona 数据模型
class Persona {
  final String id;
  final String title;
  final String tag;
  final Color tagColor;
  final double progress;
  final IconData icon;

  Persona({
    required this.id,
    required this.title,
    required this.tag,
    required this.tagColor,
    required this.progress,
    required this.icon,
  });
}

/// 风格卡数据模型（合并了本地和共享信息）
class StyleCard {
  final String id;
  final String title;
  final String imageUrl;
  final String description; // 风格卡描述
  final List<OperationRecord> operations; // 记录的操作（包含函数信息）
  final StyleCardStatus status; // 状态：本地/已共享/可下载
  final int downloads; // 下载量（仅共享时有效）
  final int comments; // 评论数（仅共享时有效）
  final bool isShared; // 是否已共享到社区
  final bool isShareEnabled; // 共享开关状态
  final bool isDemoCard; // 是否为Demo卡（Demo卡不可删除）

  StyleCard({
    required this.id,
    required this.title,
    required this.imageUrl,
    this.description = '', // 默认为空
    this.operations = const [], // 默认为空列表
    required this.status,
    this.downloads = 0,
    this.comments = 0,
    this.isShared = false,
    this.isShareEnabled = false,
    this.isDemoCard = false, // 默认不是Demo卡
  });

  /// 创建本地风格卡
  factory StyleCard.local({
    required String id,
    required String title,
    String imageUrl = '',
    String description = '',
    List<OperationRecord> operations = const [],
    bool isSharedToCommunity = false, // 是否已共享到社区（但保持本地状态）
    bool isDemoCard = false, // 是否为Demo卡
  }) {
    return StyleCard(
      id: id,
      title: title,
      imageUrl: imageUrl,
      description: description,
      operations: operations,
      status: StyleCardStatus.local,
      isShared: isSharedToCommunity,
      isDemoCard: isDemoCard,
    );
  }

  /// 创建已共享的风格卡
  factory StyleCard.shared({
    required String id,
    required String title,
    String imageUrl = '',
    String description = '',
    List<OperationRecord> operations = const [],
    required int downloads,
    required int comments,
    required bool isShareEnabled,
  }) {
    return StyleCard(
      id: id,
      title: title,
      imageUrl: imageUrl,
      description: description,
      operations: operations,
      status: StyleCardStatus.shared,
      downloads: downloads,
      comments: comments,
      isShared: true,
      isShareEnabled: isShareEnabled,
    );
  }

  /// 创建可下载的风格卡
  factory StyleCard.downloadable({
    required String id,
    required String title,
    String imageUrl = '',
    String description = '',
    List<OperationRecord> operations = const [],
    required int downloads,
    required int comments,
  }) {
    return StyleCard(
      id: id,
      title: title,
      imageUrl: imageUrl,
      description: description,
      operations: operations,
      status: StyleCardStatus.downloadable,
      downloads: downloads,
      comments: comments,
      isShared: false,
    );
  }
}

/// 风格卡状态枚举
enum StyleCardStatus {
  local, // 本地风格卡（未共享）
  shared, // 已共享到社区
  downloadable, // 可下载（来自社区但未下载）
}

/// 共享Persona数据模型（已废弃，保留用于兼容）
@Deprecated('Use StyleCard instead')
class SharedPersona {
  final String id;
  final String title;
  final int downloads;
  final int comments;
  final bool isEnabled;

  SharedPersona({
    required this.id,
    required this.title,
    required this.downloads,
    required this.comments,
    required this.isEnabled,
  });
}

/// 成长轨迹数据模型
class GrowthData {
  final double value;
  final String label;

  GrowthData({required this.value, required this.label});
}
