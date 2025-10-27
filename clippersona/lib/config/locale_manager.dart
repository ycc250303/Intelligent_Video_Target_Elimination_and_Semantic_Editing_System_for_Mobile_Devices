import 'package:flutter/material.dart';

/// 支持的语言枚举
enum AppLocale {
  zh('zh', '中文'),
  en('en', 'English');

  final String code;
  final String name;

  const AppLocale(this.code, this.name);
}

/// 语言配置管理器
class LocaleManager extends ChangeNotifier {
  static final LocaleManager _instance = LocaleManager._internal();
  factory LocaleManager() => _instance;
  LocaleManager._internal();

  AppLocale _currentLocale = AppLocale.zh; // 默认中文

  /// 获取当前语言
  AppLocale get currentLocale => _currentLocale;

  /// 切换语言
  void setLocale(AppLocale locale) {
    if (_currentLocale != locale) {
      _currentLocale = locale;
      notifyListeners(); // 通知所有监听者更新UI
    }
  }

  /// 切换到中文
  void toChinese() => setLocale(AppLocale.zh);

  /// 切换到英文
  void toEnglish() => setLocale(AppLocale.en);

  /// 判断当前是否为中文
  bool get isChinese => _currentLocale == AppLocale.zh;

  /// 判断当前是否为英文
  bool get isEnglish => _currentLocale == AppLocale.en;
}

