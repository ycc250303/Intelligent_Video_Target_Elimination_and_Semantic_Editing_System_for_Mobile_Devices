enum MessageType { text, image, video, voice, multimodal }

enum MessageSender { user, bot }

/// 媒体项
class MessageMedia {
  final String path;
  final String type; // 'image' 或 'video'
  final String? thumbnailPath;

  MessageMedia({required this.path, required this.type, this.thumbnailPath});
}

class Message {
  final String id;
  final String content;
  final MessageType type;
  final MessageSender sender;
  final DateTime timestamp;
  final String? mediaPath;
  final String? thumbnailPath; // 视频缩略图路径
  final Duration? voiceDuration;
  final List<MessageMedia>? mediaList; // 多模态消息的媒体列表

  Message({
    required this.id,
    required this.content,
    required this.type,
    required this.sender,
    required this.timestamp,
    this.mediaPath,
    this.thumbnailPath,
    this.voiceDuration,
    this.mediaList,
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
    String? thumbnailPath,
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
      thumbnailPath: thumbnailPath,
      voiceDuration: voiceDuration,
    );
  }

  // 多模态消息工厂方法
  factory Message.multimodal({
    required String id,
    required String content,
    required MessageSender sender,
    required List<MessageMedia> mediaList,
    DateTime? timestamp,
  }) {
    return Message(
      id: id,
      content: content,
      type: MessageType.multimodal,
      sender: sender,
      timestamp: timestamp ?? DateTime.now(),
      mediaList: mediaList,
    );
  }
}
