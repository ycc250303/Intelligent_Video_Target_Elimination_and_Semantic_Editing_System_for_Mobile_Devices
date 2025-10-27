import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'config/app_locales.dart';
import 'config/locale_manager.dart';
import 'config/settings_manager.dart';
import 'pages/persona/persona_page.dart';
import 'pages/clip/clip_page.dart';
import 'pages/community/community_page.dart';
import 'pages/settings/settings_page.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;
  final LocaleManager _localeManager = LocaleManager();
  final SettingsManager _settingsManager = SettingsManager();

  @override
  void initState() {
    super.initState();
    // 监听语言变化
    _localeManager.addListener(_onLocaleChanged);
    // 监听设置变化
    _settingsManager.addListener(_onSettingsChanged);
  }

  @override
  void dispose() {
    _localeManager.removeListener(_onLocaleChanged);
    _settingsManager.removeListener(_onSettingsChanged);
    super.dispose();
  }

  void _onLocaleChanged() {
    setState(() {}); // 重新构建UI以更新导航栏文本
  }

  void _onSettingsChanged() {
    setState(() {
      // 如果社区功能被关闭
      if (!_settingsManager.communityUpdatesEnabled) {
        // 如果当前在社区页面（索引2），切换到Persona页面
        if (_currentIndex == 2) {
          _currentIndex = 0;
        }
        // 如果当前在设置页面（原索引3，现在变成索引2），调整索引
        else if (_currentIndex >= 3) {
          _currentIndex = 2; // 设置页面现在的索引
        }
      }
      // 如果社区功能被重新开启，且当前索引是2（设置），需要调整为3
      else {
        if (_currentIndex == 2) {
          _currentIndex = 3; // 恢复到设置页面的正确索引
        }
      }
    });
  }

  // 获取所有可用页面 - 动态根据社区开关决定是否包含社区页面
  List<Widget> get _pages {
    final pages = [
      const PersonaPage(),
      const ClipPage(),
      if (_settingsManager.communityUpdatesEnabled) const CommunityPage(),
      const SettingsPage(),
    ];
    return pages;
  }

  // 定义导航栏项目 - 根据语言和设置动态生成
  List<BottomNavigationBarItem> get _navItems {
    final items = [
      BottomNavigationBarItem(
        icon: const Icon(Icons.person),
        label: appLocales.navPersona,
      ),
      BottomNavigationBarItem(
        icon: const Icon(Icons.video_library),
        label: appLocales.navClip,
      ),
      if (_settingsManager.communityUpdatesEnabled)
        BottomNavigationBarItem(
          icon: const Icon(Icons.people),
          label: appLocales.navCommunity,
        ),
      BottomNavigationBarItem(
        icon: const Icon(Icons.settings),
        label: appLocales.navSettings,
      ),
    ];
    return items;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: IndexedStack(index: _currentIndex, children: _pages),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/navBackground.png'),
            fit: BoxFit.cover,
          ),
          // 添加阴影效果
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 10,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.transparent, // 设置为透明
          elevation: 0, // 移除默认阴影
          currentIndex: _currentIndex,
          onTap: (index) {
            HapticFeedback.lightImpact();
            setState(() {
              _currentIndex = index;
            });
          },
          selectedItemColor: Colors.white, // 选中项为白色
          unselectedItemColor: Colors.white.withValues(
            alpha: 0.6,
          ), // 未选中项为半透明白色
          items: _navItems,
        ),
      ),
    );
  }
}
