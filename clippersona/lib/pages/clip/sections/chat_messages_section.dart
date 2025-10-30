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
  final String? userAvatarPath;
  final Function(String mediaPath)? onRemoveFromBuffer;

  const ChatMessagesSection({
    super.key,
    required this.messages,
    required this.scrollController,
    required this.historyProjects,
    required this.onStartConversation,
    required this.onStyleCardMode,
    required this.onCreateStyleCardMode,
    this.userAvatarPath,
    this.onRemoveFromBuffer,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.transparent,
      child: historyProjects.isEmpty
          ? WelcomeSection(
              onStartConversation: onStartConversation,
              onStyleCardMode: onStyleCardMode,
              onCreateStyleCardMode: onCreateStyleCardMode,
            )
          : ListView.builder(
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
            ),
    );
  }
}
