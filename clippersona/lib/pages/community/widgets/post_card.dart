import 'package:flutter/material.dart';
import '../persona_detail_page.dart';

class PostCard extends StatelessWidget {
  final Map<String, dynamic> post;
  final VoidCallback? onTap;

  const PostCard({super.key, required this.post, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap:
          onTap ??
          () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => PersonaDetailPage(persona: post),
              ),
            );
          },
      child: Container(
        margin: EdgeInsets.only(bottom: 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color.fromRGBO(134, 227, 201, 1.0),
              Color.fromRGBO(181, 236, 54, 1.0),
            ],
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 8,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 用户信息
              _buildUserInfo(),
              SizedBox(height: 4),
              // 内容
              _buildContent(),
              SizedBox(height: 4),
              // 图片
              if (post['image'] != null) _buildImage(),
              SizedBox(height: 4),
              // 互动按钮
              _buildInteractionButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildUserInfo() {
    return Row(
      children: [
        CircleAvatar(radius: 20, backgroundImage: AssetImage(post['avatar'])),
        SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                post['user'],
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: Color(0xFF2C3E50),
                ),
              ),
              Text(
                post['time'],
                style: TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        IconButton(
          icon: Icon(Icons.more_vert),
          onPressed: () {
            // 处理更多选项
          },
        ),
      ],
    );
  }

  Widget _buildContent() {
    return Text(
      post['content'],
      style: TextStyle(
        fontSize: 14,
        color: Color(0xFF34495E),
        height: 1.4,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildImage() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Image.asset(
        post['image'],
        width: double.infinity,
        height: 180,
        fit: BoxFit.cover,
      ),
    );
  }

  Widget _buildInteractionButtons() {
    return Row(
      children: [
        IconButton(
          icon: Icon(Icons.favorite_border, color: Color(0xFFE74C3C)),
          onPressed: () {
            // 处理点赞
          },
        ),
        Text(
          '${post['likes']}',
          style: TextStyle(
            color: Color(0xFF7F8C8D),
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(width: 20),
        IconButton(
          icon: Icon(Icons.comment_outlined, color: Color(0xFF3498DB)),
          onPressed: () {
            // 处理评论
          },
        ),
        Text(
          '${post['comments']}',
          style: TextStyle(
            color: Color(0xFF7F8C8D),
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(width: 20),
        IconButton(
          icon: Icon(Icons.share, color: Color(0xFF27AE60)),
          onPressed: () {
            // 处理分享
          },
        ),
      ],
    );
  }
}
