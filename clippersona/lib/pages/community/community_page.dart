import 'package:flutter/material.dart';
import 'sections/posts_section.dart';
import 'widgets/community_header.dart';
import 'persona_detail_page.dart';

class CommunityPage extends StatefulWidget {
  const CommunityPage({super.key});

  @override
  State<CommunityPage> createState() => _CommunityPageState();
}

class _CommunityPageState extends State<CommunityPage> {
  final List<Map<String, dynamic>> _posts = [
    {
      'user': '剪辑大师',
      'avatar': 'assets/communityPage/persona.png',
      'time': '2小时前',
      'content': '分享一个超实用的剪辑技巧，让你的视频更有层次感！',
      'likes': 128,
      'comments': 23,
      'image': 'assets/communityPage/persona.png',
    },
    {
      'user': '视频达人',
      'avatar': 'assets/communityPage/persona.png',
      'time': '5小时前',
      'content': '今天用新功能制作了一个创意视频，效果太棒了！',
      'likes': 89,
      'comments': 15,
      'image': 'assets/communityPage/persona.png',
    },
    {
      'user': '创意设计师',
      'avatar': 'assets/communityPage/persona.png',
      'time': '1天前',
      'content': '推荐几个超好用的素材网站，免费高质量！',
      'likes': 256,
      'comments': 67,
      'image': 'assets/communityPage/persona.png',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CommunityHeader(
        onSearchPressed: _handleSearch,
        onAddPressed: _handleAddPost,
      ),
      body: PostsSection(posts: _posts, onPostTap: _handlePostTap),
    );
  }

  void _handleSearch() {
    // 处理搜索功能
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('搜索'),
        content: TextField(
          decoration: InputDecoration(
            hintText: '搜索帖子、用户或标签...',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('搜索'),
          ),
        ],
      ),
    );
  }

  void _handleAddPost() {
    // 处理发布功能
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('发布功能开发中...'), backgroundColor: Color(0xFF3498DB)),
    );
  }

  void _handlePostTap(Map<String, dynamic> post) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => PersonaDetailPage(persona: post)),
    );
  }
}
