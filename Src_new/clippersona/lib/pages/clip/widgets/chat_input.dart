import 'package:flutter/material.dart';

class ChatInput extends StatefulWidget {
  final Function(String) onSendMessage;
  final Function() onVoiceStart;
  final Function() onVoiceStop;
  final Function() onImagePick;
  final Function() onVideoPick;
  final bool isRecording;

  const ChatInput({
    super.key,
    required this.onSendMessage,
    required this.onVoiceStart,
    required this.onVoiceStop,
    required this.onImagePick,
    required this.onVideoPick,
    this.isRecording = false,
  });

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isNotEmpty) {
      widget.onSendMessage(text);
      _controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF232336),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // 媒体选择按钮
            Row(
              children: [
                IconButton(
                  onPressed: widget.onImagePick,
                  icon: const Icon(Icons.image),
                  color: Colors.blue,
                ),
                IconButton(
                  onPressed: widget.onVideoPick,
                  icon: const Icon(Icons.videocam),
                  color: Colors.green,
                ),
              ],
            ),
            // 输入框
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[100]?.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  decoration: const InputDecoration(
                    hintText: '输入消息...',
                    border: InputBorder.none,
                    contentPadding: EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                  ),
                  maxLines: null,
                  textCapitalization: TextCapitalization.sentences,
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // 发送/录音按钮
            GestureDetector(
              onTapDown: (_) => widget.onVoiceStart(),
              onTapUp: (_) => widget.onVoiceStop(),
              onTapCancel: () => widget.onVoiceStop(),
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: (widget.isRecording ? Colors.red : Colors.blue)
                      .withValues(alpha: 0.8),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  widget.isRecording ? Icons.stop : Icons.mic,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 8),
            // 发送按钮
            GestureDetector(
              onTap: _sendMessage,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.8),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.send, color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
