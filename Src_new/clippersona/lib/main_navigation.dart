import 'package:flutter/material.dart';
import 'pages/home_page.dart';
import 'pages/explore_page.dart';
import 'pages/favorites_page.dart';
import 'pages/message_page.dart';
import 'pages/profile_page.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  // 定义所有页面
  final List<Widget> _pages = [
    const HomePage(),
    const ExplorePage(),
    const FavoritesPage(),
    const MessagePage(),
    const ProfilePage(),
  ];

  // 定义导航栏项目
  final List<BottomNavigationBarItem> _navItems = [
    BottomNavigationBarItem(icon: Icon(Icons.home), label: '首页'),
    BottomNavigationBarItem(icon: Icon(Icons.explore), label: '探索'),
    BottomNavigationBarItem(icon: Icon(Icons.star), label: '收藏'),
    BottomNavigationBarItem(
      icon: Stack(
        children: [
          Icon(Icons.message),
          Positioned(
            right: 0,
            top: 0,
            child: Container(
              padding: EdgeInsets.all(2),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(6),
              ),
              constraints: BoxConstraints(minWidth: 12, minHeight: 12),
              child: Text(
                '3',
                style: TextStyle(color: Colors.white, fontSize: 8),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
      label: '消息',
    ),
    BottomNavigationBarItem(icon: Icon(Icons.person), label: '我的'),
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
          // 使用 navbackground 作为导航栏背景
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
