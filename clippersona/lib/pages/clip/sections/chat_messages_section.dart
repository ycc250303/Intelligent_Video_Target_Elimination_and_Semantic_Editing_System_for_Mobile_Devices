import 'package:flutter/material.dart';
import '../../../models/message.dart';
import '../widgets/message_bubble.dart';
import 'welcome_section.dart';

class ChatMessagesSection extends StatelessWidget {
  final List<Message> messages;
  final ScrollController scrollController;
  final List<dynamic> historyProjects;
  final VoidCallback onStartConversation;
  final VoidCallback onStyleCardMode;
  final VoidCallback onCreateStyleCardMode;
  final VoidCallback? onTrainStyleCard;
  final String? userAvatarPath;
  final Function(String mediaPath)? onRemoveFromBuffer;
  final bool hasActiveSession; // 新增：是否有活跃会话

  const ChatMessagesSection({
    super.key,
    required this.messages,
    required this.scrollController,
    required this.historyProjects,
    required this.onStartConversation,
    required this.onStyleCardMode,
    required this.onCreateStyleCardMode,
    this.onTrainStyleCard,
    this.userAvatarPath,
    this.onRemoveFromBuffer,
    required this.hasActiveSession, // 新增：必传参数
  });

  @override
  Widget build(BuildContext context) {
    // 有活跃会话或有消息时显示消息列表；否则显示欢迎页面
    final hasMessages = messages.isNotEmpty;
    final shouldShowMessages = hasActiveSession || hasMessages;

    return Container(
      color: Colors.transparent,
      child: shouldShowMessages
          ? ListView.builder(
              controller: scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return MessageBubble(
                  message: messages[index],
                  userAvatarPath: userAvatarPath,
                  onRemoveFromBuffer: onRemoveFromBuffer,
                );
              },
            )
          : WelcomeSection(
              onStartConversation: onStartConversation,
              onStyleCardMode: onStyleCardMode,
              onCreateStyleCardMode: onCreateStyleCardMode,
              onTrainStyleCard: onTrainStyleCard,
            ),
    );
  }
}
