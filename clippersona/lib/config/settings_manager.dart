import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 应用设置管理器
class SettingsManager extends ChangeNotifier {
  static final SettingsManager _instance = SettingsManager._internal();
  factory SettingsManager() => _instance;
  SettingsManager._internal() {
    _loadSettings();
  }

  bool _communityUpdatesEnabled = true;

  /// 获取社区动态是否启用
  bool get communityUpdatesEnabled => _communityUpdatesEnabled;

  /// 设置社区动态开关
  Future<void> setCommunityUpdates(bool enabled) async {
    if (_communityUpdatesEnabled != enabled) {
      _communityUpdatesEnabled = enabled;
      notifyListeners(); // 通知所有监听者更新UI

      // 持久化保存
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('community_updates_enabled', enabled);
    }
  }

  /// 从本地存储加载设置
  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _communityUpdatesEnabled =
        prefs.getBool('community_updates_enabled') ?? true;
    notifyListeners();
  }
}

