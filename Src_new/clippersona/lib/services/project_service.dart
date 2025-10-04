import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/project_models.dart';
import '../models/message.dart';

class ProjectService {
  static const String _projectsKey = 'saved_projects';
  static ProjectService? _instance;

  ProjectService._();

  static ProjectService get instance {
    _instance ??= ProjectService._();
    return _instance!;
  }

  // 获取所有项目
  Future<List<Project>> getAllProjects() async {
    final prefs = await SharedPreferences.getInstance();
    final projectsJson = prefs.getStringList(_projectsKey) ?? [];

    return projectsJson.map((jsonString) {
      final json = jsonDecode(jsonString);
      return ProjectJson.fromJson(json);
    }).toList();
  }

  // 保存项目
  Future<void> saveProject(Project project) async {
    final prefs = await SharedPreferences.getInstance();
    final projects = await getAllProjects();

    // 查找是否已存在相同ID的项目
    final existingIndex = projects.indexWhere((p) => p.id == project.id);

    if (existingIndex >= 0) {
      // 更新现有项目
      projects[existingIndex] = project;
    } else {
      // 添加新项目
      projects.add(project);
    }

    // 按更新时间排序，最新的在前
    projects.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));

    // 保存到本地存储
    final projectsJson = projects.map((p) => jsonEncode(p.toJson())).toList();
    await prefs.setStringList(_projectsKey, projectsJson);
  }

  // 根据ID获取项目
  Future<Project?> getProjectById(String id) async {
    final projects = await getAllProjects();
    try {
      return projects.firstWhere((p) => p.id == id);
    } catch (e) {
      return null;
    }
  }

  // 删除项目
  Future<void> deleteProject(String id) async {
    final prefs = await SharedPreferences.getInstance();
    final projects = await getAllProjects();
    projects.removeWhere((p) => p.id == id);

    final projectsJson = projects.map((p) => jsonEncode(p.toJson())).toList();
    await prefs.setStringList(_projectsKey, projectsJson);
  }

  // 创建新项目
  Future<Project> createNewProject() async {
    final now = DateTime.now();
    final project = Project(
      id: 'project_${now.millisecondsSinceEpoch}',
      title: '新对话 ${_formatDateTime(now)}',
      progress: 0.0,
      icon: '🎬',
      status: '进行中',
      createdAt: now,
      updatedAt: now,
      messages: [],
    );

    await saveProject(project);
    return project;
  }

  // 更新项目消息
  Future<void> updateProjectMessages(
    String projectId,
    List<Message> messages,
  ) async {
    final project = await getProjectById(projectId);
    if (project != null) {
      final updatedProject = project.copyWith(
        messages: messages,
        updatedAt: DateTime.now(),
        progress: _calculateProgress(messages),
      );
      await saveProject(updatedProject);
    }
  }

  // 计算项目进度
  double _calculateProgress(List<Message> messages) {
    if (messages.isEmpty) return 0.0;

    // 简单的进度计算：基于消息数量
    final userMessages = messages
        .where((m) => m.sender == MessageSender.user)
        .length;
    if (userMessages == 0) return 0.0;

    // 每10条用户消息增加10%进度，最大100%
    return (userMessages * 0.1).clamp(0.0, 1.0);
  }

  // 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

// 扩展Project类，添加JSON序列化方法
extension ProjectJson on Project {
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'progress': progress,
      'icon': icon,
      'status': status,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'messages': messages.map((m) => _messageToJson(m)).toList(),
    };
  }

  static Project fromJson(Map<String, dynamic> json) {
    return Project(
      id: json['id'],
      title: json['title'],
      progress: json['progress'].toDouble(),
      icon: json['icon'],
      status: json['status'],
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: DateTime.parse(json['updatedAt']),
      messages: (json['messages'] as List)
          .map((m) => _messageFromJson(m))
          .toList(),
    );
  }

  static Map<String, dynamic> _messageToJson(Message message) {
    return {
      'id': message.id,
      'content': message.content,
      'type': message.type.name,
      'sender': message.sender.name,
      'timestamp': message.timestamp.toIso8601String(),
      'mediaPath': message.mediaPath,
      'voiceDuration': message.voiceDuration?.inMilliseconds,
    };
  }

  static Message _messageFromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      type: MessageType.values.firstWhere((e) => e.name == json['type']),
      sender: MessageSender.values.firstWhere((e) => e.name == json['sender']),
      timestamp: DateTime.parse(json['timestamp']),
      mediaPath: json['mediaPath'],
      voiceDuration: json['voiceDuration'] != null
          ? Duration(milliseconds: json['voiceDuration'])
          : null,
    );
  }
}
