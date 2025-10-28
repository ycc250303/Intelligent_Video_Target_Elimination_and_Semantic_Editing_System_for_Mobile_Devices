import 'package:flutter/material.dart';

class ClipAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onHistoryTap;
  final VoidCallback onNewConversationTap;
  final String? title; // 可选的自定义标题

  const ClipAppBar({
    super.key,
    required this.onHistoryTap,
    required this.onNewConversationTap,
    this.title, // 如果为null，使用默认标题"剪辑"
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title ?? '剪辑'),
      centerTitle: true,
      foregroundColor: Colors.white,
      backgroundColor: Colors.transparent,
      elevation: 0,
      leading: IconButton(
        icon: const Icon(Icons.history),
        onPressed: onHistoryTap,
        tooltip: '历史对话',
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.add),
          onPressed: onNewConversationTap,
          tooltip: '新建对话',
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
