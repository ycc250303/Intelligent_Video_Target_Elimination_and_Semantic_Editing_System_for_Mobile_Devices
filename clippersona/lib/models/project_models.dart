import 'message.dart';

class Project {
  final String id;
  final String title;
  final double progress;
  final String icon;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<Message> messages;

  const Project({
    required this.id,
    required this.title,
    required this.progress,
    required this.icon,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.messages = const [],
  });

  Project copyWith({
    String? id,
    String? title,
    double? progress,
    String? icon,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    List<Message>? messages,
  }) {
    return Project(
      id: id ?? this.id,
      title: title ?? this.title,
      progress: progress ?? this.progress,
      icon: icon ?? this.icon,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      messages: messages ?? this.messages,
    );
  }
}

class StyleCard {
  final String id;
  final String title;
  final String imagePath;
  final String description;
  final bool isDownloaded;

  const StyleCard({
    required this.id,
    required this.title,
    required this.imagePath,
    required this.description,
    this.isDownloaded = false,
  });
}

class CurrentPersona {
  final String id;
  final String title;
  final String tag;
  final double progress;
  final String description;

  const CurrentPersona({
    required this.id,
    required this.title,
    required this.tag,
    required this.progress,
    required this.description,
  });
}
