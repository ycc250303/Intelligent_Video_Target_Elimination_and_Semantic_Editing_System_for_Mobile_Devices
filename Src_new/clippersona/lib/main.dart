import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'main_navigation.dart';
import 'config/locale_manager.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final LocaleManager _localeManager = LocaleManager();

  @override
  void initState() {
    super.initState();
    // 监听语言变化
    _localeManager.addListener(_onLocaleChanged);
  }

  @override
  void dispose() {
    _localeManager.removeListener(_onLocaleChanged);
    super.dispose();
  }

  void _onLocaleChanged() {
    setState(() {}); // 重新构建UI
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CoEdit',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
        scaffoldBackgroundColor: Colors.transparent, // 设置背景透明
        textTheme: TextTheme(
          bodyLarge: TextStyle(fontWeight: FontWeight.bold),
          bodyMedium: TextStyle(fontWeight: FontWeight.bold),
          bodySmall: TextStyle(fontWeight: FontWeight.bold),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          foregroundColor: Colors.white,
          // 添加标题文字样式
          titleTextStyle: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
          systemOverlayStyle: SystemUiOverlayStyle(
            statusBarColor: Colors.transparent,
            statusBarIconBrightness: Brightness.dark,
            statusBarBrightness: Brightness.light,
          ),
        ),
      ),
      home: const MainNavigation(), // 使用主导航页面
      debugShowCheckedModeBanner: false, // 隐藏调试横幅
    );
  }
}
