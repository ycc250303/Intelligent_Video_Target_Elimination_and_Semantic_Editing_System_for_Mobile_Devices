import 'package:flutter/material.dart';
import 'clip_page.dart';

class ClipFullPage extends StatelessWidget {
  final String? projectId;

  const ClipFullPage({super.key, this.projectId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: Stack(
          children: [
            ClipPage(projectId: projectId),
            // 右上角返回按钮
            Positioned(
              top: MediaQuery.of(context).padding.top + 16,
              right: 16,
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: IconButton(
                  icon: const Icon(Icons.close, color: Colors.white, size: 24),
                  onPressed: () => Navigator.of(context).pop(),
                  tooltip: '返回',
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
