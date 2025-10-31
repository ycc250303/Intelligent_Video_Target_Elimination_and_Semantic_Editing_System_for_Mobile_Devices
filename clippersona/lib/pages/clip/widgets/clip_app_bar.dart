import 'package:flutter/material.dart';

enum ClipAppBarMode {
  normal, // 普通模式：显示"工作台"和"+"按钮
  createStyleCard, // 创建风格卡模式：显示"创建风格卡"和"导出"按钮
}

class ClipAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback onHistoryTap;
  final VoidCallback onNewConversationTap;
  final VoidCallback? onExportStyleCard; // 导出风格卡回调
  final VoidCallback? onBackToWelcome; // 返回欢迎页面回调
  final String? title; // 可选的自定义标题
  final ClipAppBarMode mode; // AppBar模式
  final bool showBackButton; // 是否显示返回按钮

  const ClipAppBar({
    super.key,
    required this.onHistoryTap,
    required this.onNewConversationTap,
    this.onExportStyleCard,
    this.onBackToWelcome,
    this.title,
    this.mode = ClipAppBarMode.normal,
    this.showBackButton = false,
  });

  @override
  Widget build(BuildContext context) {
    // 根据模式决定标题
    String displayTitle =
        title ?? (mode == ClipAppBarMode.createStyleCard ? '创建风格卡' : '工作台');

    return AppBar(
      title: Text(displayTitle),
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
        // 根据模式显示不同的按钮
        if (mode == ClipAppBarMode.createStyleCard)
          IconButton(
            icon: const Icon(Icons.upload),
            onPressed: onExportStyleCard,
            tooltip: '导出风格卡',
          )
        else ...[
          // 如果有活跃会话，显示返回按钮
          if (showBackButton)
            IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: onBackToWelcome,
              tooltip: '返回首页',
            ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: onNewConversationTap,
            tooltip: '新建对话',
          ),
        ],
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
