import 'package:flutter/material.dart';
import '../../../models/message.dart';
import '../widgets/message_bubble.dart';
import 'welcome_section.dart';

class ChatMessagesSection extends StatelessWidget {
  final List<Message> messages;
  final ScrollController scrollController;
  final List<dynamic> historyProjects;
  final VoidCallback onStartConversation;

  const ChatMessagesSection({
    super.key,
    required this.messages,
    required this.scrollController,
    required this.historyProjects,
    required this.onStartConversation,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.transparent,
      child: historyProjects.isEmpty
          ? WelcomeSection(onStartConversation: onStartConversation)
          : ListView.builder(
              controller: scrollController,
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return MessageBubble(message: messages[index]);
              },
            ),
    );
  }
}
