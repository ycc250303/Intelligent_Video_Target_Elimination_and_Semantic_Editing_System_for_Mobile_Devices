import 'package:flutter/material.dart';

class FavoritesPage extends StatelessWidget {
  const FavoritesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('收藏'),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.search),
            onPressed: () {
              // 处理搜索
            },
          ),
        ],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildFavoriteCard(
            title: 'Flutter 开发指南',
            subtitle: '学习 Flutter 的最佳实践',
            icon: Icons.code,
            color: Colors.blue,
          ),
          _buildFavoriteCard(
            title: 'UI 设计技巧',
            subtitle: '创建美观的用户界面',
            icon: Icons.design_services,
            color: Colors.purple,
          ),
          _buildFavoriteCard(
            title: '移动应用优化',
            subtitle: '提升应用性能的方法',
            icon: Icons.speed,
            color: Colors.green,
          ),
          _buildFavoriteCard(
            title: '用户体验设计',
            subtitle: '设计用户友好的应用',
            icon: Icons.psychology,
            color: Colors.orange,
          ),
        ],
      ),
    );
  }

  Widget _buildFavoriteCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      elevation: 4,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white),
        ),
        title: Text(
          title,
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        subtitle: Text(subtitle),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(Icons.favorite, color: Colors.red),
              onPressed: () {
                // 处理取消收藏
              },
            ),
            Icon(Icons.arrow_forward_ios, size: 16),
          ],
        ),
        onTap: () {
          // 处理点击事件
        },
      ),
    );
  }
}
