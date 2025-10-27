import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'main_navigation.dart';
import 'config/locale_manager.dart';
import 'services/backend_session_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // 在后台异步清空后端会话（不阻塞UI启动）
  _initializeApp();

  runApp(const MyApp());
}

/// 应用初始化（异步，在后台执行）
Future<void> _initializeApp() async {
  try {
    print('🧹 开始清空后端会话记录...');

    // 添加5秒超时，避免长时间等待
    await BackendSessionService.deleteAllSessions().timeout(
      const Duration(seconds: 5),
    );

    print('✅ 后端会话已清空');
  } catch (e) {
    print('⚠️ 清空后端会话失败（可能后端未启动）: $e');
    // 失败不影响app启动
  }
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
