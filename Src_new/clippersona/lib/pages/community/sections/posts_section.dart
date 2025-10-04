import 'package:flutter/material.dart';
import '../widgets/post_card.dart';

class PostsSection extends StatelessWidget {
  final List<Map<String, dynamic>> posts;
  final Function(Map<String, dynamic>)? onPostTap;

  const PostsSection({super.key, required this.posts, this.onPostTap});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: EdgeInsets.all(16),
      itemCount: posts.length,
      itemBuilder: (context, index) {
        final post = posts[index];
        return PostCard(
          post: post,
          onTap: onPostTap != null ? () => onPostTap!(post) : null,
        );
      },
    );
  }
}
