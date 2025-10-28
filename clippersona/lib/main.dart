import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'main_navigation.dart';
import 'config/locale_manager.dart';
import 'services/backend_session_service.dart';

// 全局标记：是否已完成初始化
bool _isInitialized = false;

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

/// 应用初始化（清空所有会话和缓存）
Future<void> _initializeApp() async {
  if (_isInitialized) return; // 避免重复初始化

  try {
    print('🧹 开始清空会话记录...');

    // 1. 清空后端会话（添加5秒超时，避免长时间等待）
    await BackendSessionService.deleteAllSessions().timeout(
      const Duration(seconds: 5),
    );
    print('✅ 后端会话已清空');

    // 2. 清空前端本地缓存（SharedPreferences）
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('saved_projects');
    print('✅ 前端本地缓存已清空');

    _isInitialized = true;
  } catch (e) {
    print('⚠️ 清空会话失败（可能后端未启动）: $e');
    _isInitialized = true; // 即使失败也标记为已初始化，避免一直等待
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
      // 使用 FutureBuilder 确保初始化完成后再显示主界面
      home: FutureBuilder<void>(
        future: _initializeApp(),
        builder: (context, snapshot) {
          // 显示加载指示器，直到初始化完成
          if (snapshot.connectionState != ConnectionState.done) {
            return Scaffold(
              body: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF1a1a2e),
                      Color(0xFF16213e),
                      Color(0xFF0f3460),
                    ],
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(color: Colors.white),
                      SizedBox(height: 20),
                      Text(
                        '正在初始化...',
                        style: TextStyle(color: Colors.white, fontSize: 16),
                      ),
                    ],
                  ),
                ),
              ),
            );
          }
          // 初始化完成，显示主界面
          return const MainNavigation();
        },
      ),
      debugShowCheckedModeBanner: false, // 隐藏调试横幅
    );
  }
}
