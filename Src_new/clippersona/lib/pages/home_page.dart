import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _counter = 0;
  final String _userName = "翔仔";

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('首页'),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.notifications),
            onPressed: () {
              // 处理通知点击
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // 欢迎卡片
            Container(
              width: double.infinity,
              margin: EdgeInsets.all(16),
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.deepPurple, Colors.deepPurple.shade300],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.deepPurple.withOpacity(0.3),
                    blurRadius: 10,
                    offset: Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 40,
                    backgroundColor: Colors.white,
                    child: Text(
                      _userName[0],
                      style: TextStyle(
                        fontSize: 32,
                        color: Colors.deepPurple,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Text(
                    '你好，$_userName！',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    '欢迎回到您的应用',
                    style: TextStyle(fontSize: 16, color: Colors.white70),
                  ),
                ],
              ),
            ),

            // 计数器卡片
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16),
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    blurRadius: 10,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Text(
                    '计数器',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 16),
                  Text(
                    '$_counter',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.deepPurple,
                    ),
                  ),
                  SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _incrementCounter,
                    icon: Icon(Icons.add),
                    label: Text('增加计数'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            SizedBox(height: 20),

            // 快捷功能
            Container(
              margin: EdgeInsets.symmetric(horizontal: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '快捷功能',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildQuickAction(
                          icon: Icons.explore,
                          title: '探索',
                          color: Colors.green,
                          onTap: () {
                            // 切换到探索页面
                          },
                        ),
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: _buildQuickAction(
                          icon: Icons.message,
                          title: '消息',
                          color: Colors.blue,
                          onTap: () {
                            // 切换到消息页面
                          },
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildQuickAction(
                          icon: Icons.person,
                          title: '个人资料',
                          color: Colors.purple,
                          onTap: () {
                            // 切换到个人资料页面
                          },
                        ),
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: _buildQuickAction(
                          icon: Icons.settings,
                          title: '设置',
                          color: Colors.orange,
                          onTap: () {
                            // 打开设置
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String title,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            SizedBox(height: 8),
            Text(
              title,
              style: TextStyle(color: color, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
