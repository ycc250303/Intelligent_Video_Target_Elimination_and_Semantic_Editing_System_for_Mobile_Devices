import 'package:flutter/material.dart';

class CommunityHeader extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback? onSearchPressed;
  final VoidCallback? onAddPressed;

  const CommunityHeader({super.key, this.onSearchPressed, this.onAddPressed});

  @override
  Size get preferredSize => Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text('社区'),
      centerTitle: true,
      foregroundColor: Colors.white,
      actions: [
        IconButton(
          icon: Icon(Icons.search),
          onPressed:
              onSearchPressed ??
              () {
                // 默认搜索处理
              },
        ),
        IconButton(
          icon: Icon(Icons.add),
          onPressed:
              onAddPressed ??
              () {
                // 默认发布处理
              },
        ),
      ],
    );
  }
}
