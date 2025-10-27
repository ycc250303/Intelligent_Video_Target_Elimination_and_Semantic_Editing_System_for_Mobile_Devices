import 'package:flutter/material.dart';

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

/// 风格卡数据模型
class StyleCard {
  final String id;
  final String title;
  final String imageUrl;
  final bool isDownloaded;

  StyleCard({
    required this.id,
    required this.title,
    required this.imageUrl,
    required this.isDownloaded,
  });
}

/// 共享Persona数据模型
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
