import 'package:flutter/material.dart';

class WelcomeSection extends StatelessWidget {
  final VoidCallback onStartConversation;
  final VoidCallback onStyleCardMode;
  final VoidCallback onCreateStyleCardMode;

  const WelcomeSection({
    super.key,
    required this.onStartConversation,
    required this.onStyleCardMode,
    required this.onCreateStyleCardMode,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 欢迎图标
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFF374151),
                borderRadius: BorderRadius.circular(40),
                border: Border.all(
                  color: Colors.green.withValues(alpha: 0.3),
                  width: 2,
                ),
              ),
              child: const Icon(
                Icons.chat_bubble_outline,
                size: 40,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 24),

            // 欢迎标题
            const Text(
              '欢迎使用剪辑助手',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),

            // 欢迎描述
            const Text(
              '我是您的专业剪辑助手，可以帮助您进行各种剪辑相关的操作',
              style: TextStyle(color: Colors.grey, fontSize: 14, height: 1.4),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),

            // 三个模式按钮
            _buildModeButton(
              context: context,
              icon: Icons.auto_awesome,
              label: '智能剪辑',
              description: '通过对话进行智能剪辑',
              color: const Color(0xFF3B82F6),
              onPressed: onStartConversation,
            ),
            const SizedBox(height: 16),
            _buildModeButton(
              context: context,
              icon: Icons.style,
              label: '调用风格卡',
              description: '使用预设风格快速剪辑',
              color: const Color(0xFF8B5CF6),
              onPressed: onStyleCardMode,
            ),
            const SizedBox(height: 16),
            _buildModeButton(
              context: context,
              icon: Icons.add_circle_outline,
              label: '创建风格卡',
              description: '创建自定义剪辑风格',
              color: const Color(0xFF10B981),
              onPressed: onCreateStyleCardMode,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModeButton({
    required BuildContext context,
    required IconData icon,
    required String label,
    required String description,
    required Color color,
    required VoidCallback onPressed,
  }) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 4,
        ),
        child: Row(
          children: [
            Icon(icon, size: 24),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    description,
                    style: const TextStyle(fontSize: 12, color: Colors.white70),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 16),
          ],
        ),
      ),
    );
  }
}
