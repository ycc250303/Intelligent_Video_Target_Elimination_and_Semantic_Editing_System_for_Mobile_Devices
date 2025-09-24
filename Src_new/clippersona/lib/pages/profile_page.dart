import 'package:flutter/material.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  String _userName = "翔仔";
  String _userEmail = "xiang@example.com";
  final int _likes = 42;
  final int _followers = 128;
  final int _following = 56;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('个人资料'),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.edit),
            onPressed: () {
              _showEditDialog();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // 用户头像和基本信息
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.purple, Colors.purple.shade300],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: Colors.white,
                    child: Text(
                      _userName[0],
                      style: TextStyle(
                        fontSize: 40,
                        color: Colors.purple,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Text(
                    _userName,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    _userEmail,
                    style: TextStyle(fontSize: 16, color: Colors.white70),
                  ),
                ],
              ),
            ),

            // 统计信息
            Container(
              padding: EdgeInsets.all(20),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildStatItem('点赞', _likes.toString()),
                  _buildStatItem('关注者', _followers.toString()),
                  _buildStatItem('关注中', _following.toString()),
                ],
              ),
            ),

            // 功能列表
            _buildProfileItem(Icons.person, '编辑资料', () {}),
            _buildProfileItem(Icons.settings, '设置', () {}),
            _buildProfileItem(Icons.help, '帮助与反馈', () {}),
            _buildProfileItem(Icons.info, '关于我们', () {}),
            _buildProfileItem(Icons.logout, '退出登录', () {}, isDestructive: true),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.purple,
          ),
        ),
        Text(label, style: TextStyle(color: Colors.grey)),
      ],
    );
  }

  Widget _buildProfileItem(
    IconData icon,
    String title,
    VoidCallback onTap, {
    bool isDestructive = false,
  }) {
    return ListTile(
      leading: Icon(icon, color: isDestructive ? Colors.red : Colors.grey),
      title: Text(
        title,
        style: TextStyle(color: isDestructive ? Colors.red : Colors.black),
      ),
      trailing: Icon(Icons.arrow_forward_ios),
      onTap: onTap,
    );
  }

  void _showEditDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('编辑资料'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                decoration: InputDecoration(labelText: '用户名'),
                controller: TextEditingController(text: _userName),
                onChanged: (value) => _userName = value,
              ),
              TextField(
                decoration: InputDecoration(labelText: '邮箱'),
                controller: TextEditingController(text: _userEmail),
                onChanged: (value) => _userEmail = value,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('取消'),
            ),
            TextButton(
              onPressed: () {
                setState(() {});
                Navigator.pop(context);
              },
              child: Text('保存'),
            ),
          ],
        );
      },
    );
  }
}
