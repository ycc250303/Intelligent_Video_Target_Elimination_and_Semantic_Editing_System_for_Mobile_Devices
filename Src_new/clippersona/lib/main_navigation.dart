import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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

  // 定义所有页面
  final List<Widget> _pages = [
    const PersonaPage(),
    const ClipPage(),
    const CommunityPage(),
    const SettingsPage(),
  ];

  // 定义导航栏项目
  final List<BottomNavigationBarItem> _navItems = [
    BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Persona'),
    BottomNavigationBarItem(icon: Icon(Icons.video_library), label: '剪辑'),
    BottomNavigationBarItem(icon: Icon(Icons.people), label: '社区'),
    BottomNavigationBarItem(icon: Icon(Icons.settings), label: '设置'),
  ];

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
