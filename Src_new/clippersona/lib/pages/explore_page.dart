import 'package:flutter/material.dart';

class ExplorePage extends StatelessWidget {
  const ExplorePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('探索'), foregroundColor: Colors.white),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          _buildExploreCard(
            icon: Icons.trending_up,
            title: '热门推荐',
            subtitle: '发现最受欢迎的内容',
            color: Colors.orange,
          ),
          _buildExploreCard(
            icon: Icons.category,
            title: '分类浏览',
            subtitle: '按类别查看内容',
            color: Colors.blue,
          ),
          _buildExploreCard(
            icon: Icons.search,
            title: '搜索发现',
            subtitle: '搜索你感兴趣的内容',
            color: Colors.purple,
          ),
          _buildExploreCard(
            icon: Icons.star,
            title: '精选内容',
            subtitle: '编辑精选的优质内容',
            color: Colors.amber,
          ),
        ],
      ),
    );
  }

  Widget _buildExploreCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white),
        ),
        title: Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: Icon(Icons.arrow_forward_ios),
        onTap: () {
          // 处理点击事件
        },
      ),
    );
  }
}
