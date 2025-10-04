enum MessageType { text, image, video, voice }

enum MessageSender { user, bot }

class Message {
  final String id;
  final String content;
  final MessageType type;
  final MessageSender sender;
  final DateTime timestamp;
  final String? mediaPath;
  final Duration? voiceDuration;

  Message({
    required this.id,
    required this.content,
    required this.type,
    required this.sender,
    required this.timestamp,
    this.mediaPath,
    this.voiceDuration,
  });

  factory Message.text({
    required String id,
    required String content,
    required MessageSender sender,
    DateTime? timestamp,
  }) {
    return Message(
      id: id,
      content: content,
      type: MessageType.text,
      sender: sender,
      timestamp: timestamp ?? DateTime.now(),
    );
  }

  factory Message.media({
    required String id,
    required String content,
    required MessageType type,
    required MessageSender sender,
    required String mediaPath,
    DateTime? timestamp,
    Duration? voiceDuration,
  }) {
    return Message(
      id: id,
      content: content,
      type: type,
      sender: sender,
      timestamp: timestamp ?? DateTime.now(),
      mediaPath: mediaPath,
      voiceDuration: voiceDuration,
    );
  }
}
