import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 用户信息服务 - 管理用户昵称等信息的持久化
class UserService {
  static const String _userNameKey = 'user_name';
  static const String _defaultUserName = 'USER_NAME';

  // 昵称更新通知
  static final ValueNotifier<String> userNameNotifier = ValueNotifier<String>(
    _defaultUserName,
  );

  /// 保存用户昵称
  static Future<bool> saveUserName(String userName) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final success = await prefs.setString(_userNameKey, userName);

      if (success) {
        userNameNotifier.value = userName;
      }

      return success;
    } catch (e) {
      debugPrint('保存用户昵称失败: $e');
      return false;
    }
  }

  /// 获取用户昵称
  static Future<String> getUserName() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userName = prefs.getString(_userNameKey) ?? _defaultUserName;

      // 更新通知器的值
      if (userNameNotifier.value != userName) {
        userNameNotifier.value = userName;
      }

      return userName;
    } catch (e) {
      debugPrint('获取用户昵称失败: $e');
      return _defaultUserName;
    }
  }

  /// 删除用户昵称（恢复默认）
  static Future<bool> deleteUserName() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final success = await prefs.remove(_userNameKey);

      if (success) {
        userNameNotifier.value = _defaultUserName;
      }

      return success;
    } catch (e) {
      debugPrint('删除用户昵称失败: $e');
      return false;
    }
  }
}

