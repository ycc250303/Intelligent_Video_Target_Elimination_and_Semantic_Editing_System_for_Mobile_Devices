import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import '../models/project_models.dart';
import '../models/message.dart';
import '../utils/status_mapper.dart';
import '../utils/time_converter.dart';
import '../utils/sender_mapper.dart';

/// 后端会话服务（单用户模式）
///
/// 提供与后端API的对接功能，处理数据格式转换
class BackendSessionService {
  /// 后端API基础URL
  /// 注意：
  /// - 真机测试：使用电脑的局域网IP
  /// - Android模拟器：使用 10.0.2.2（模拟器访问主机的特殊IP）
  /// - iOS模拟器/浏览器：使用 localhost
  /// 简化版本：不再使用 /api/v2 前缀
  static const String baseUrl = "http://100.80.59.113:8000"; // 真机 - 电脑WLAN IP
  // static const String baseUrl = "http://10.0.2.2:8000"; // Android模拟器
  // static const String baseUrl = "http://localhost:8000"; // iOS/浏览器

  /// 获取所有会话（单用户模式）
  ///
  /// 从后端加载所有会话并转换为前端的Project模型
  static Future<List<Project>> loadAllSessions() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/sessions'));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final sessions = data['sessions'] as List;
        return sessions.map((s) => _parseSession(s)).toList();
      }

      return [];
    } catch (e) {
      print('加载会话失败: $e');
      return [];
    }
  }

  /// 创建新会话（单用户模式）
  ///
  /// 在后端创建新会话，无需user_id参数
  static Future<Project?> createSession(String title, String icon) async {
    try {
      print('🔵 开始创建后端会话...');
      print('🔵 URL: $baseUrl/sessions/create');
      print('🔵 标题: $title, 图标: $icon');

      final response = await http.post(
        Uri.parse('$baseUrl/sessions/create'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({'title': title, 'icon': icon}),
      );

      print('🔵 创建会话响应状态码: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        print('✅ 会话创建成功！ID: ${data['session']['id']}');
        return _parseSession(data['session']);
      } else {
        print('❌ 创建会话失败: ${response.statusCode} - ${response.body}');
      }

      return null;
    } catch (e) {
      print('❌ 创建会话异常: $e');
      return null;
    }
  }

  /// 获取单个会话详情
  static Future<Project?> getSession(String sessionId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/sessions/$sessionId'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return _parseSession(data['session']);
      }

      return null;
    } catch (e) {
      print('获取会话失败: $e');
      return null;
    }
  }

  /// 更新会话信息
  static Future<bool> updateSession({
    required String sessionId,
    String? title,
    String? status,
  }) async {
    try {
      final body = <String, dynamic>{'session_id': sessionId};
      if (title != null) body['title'] = title;
      if (status != null) body['status'] = StatusMapper.toBackend(status);

      final response = await http.put(
        Uri.parse('$baseUrl/sessions/update'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode(body),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('更新会话失败: $e');
      return false;
    }
  }

  /// 删除会话
  static Future<bool> deleteSession(String sessionId) async {
    try {
      print('🗑️ 开始删除会话: $sessionId');

      final response = await http.delete(
        Uri.parse('$baseUrl/sessions/$sessionId'),
      );

      print('🗑️ 删除会话响应: ${response.statusCode}');

      if (response.statusCode == 200) {
        print('✅ 会话删除成功');
        return true;
      } else {
        print('❌ 删除会话失败: ${response.body}');
        return false;
      }
    } catch (e) {
      print('❌ 删除会话异常: $e');
      return false;
    }
  }

  /// 删除所有会话（单用户模式）
  static Future<Map<String, dynamic>?> deleteAllSessions() async {
    try {
      print('🗑️ 开始删除所有会话...');

      final response = await http.delete(Uri.parse('$baseUrl/sessions/all'));

      print('🗑️ 删除所有会话响应: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        print('✅ 所有会话删除成功，共删除 ${data['count']} 个');
        return data;
      } else {
        print('❌ 删除所有会话失败: ${response.body}');
        return null;
      }
    } catch (e) {
      print('❌ 删除所有会话异常: $e');
      return null;
    }
  }

  /// 向会话添加消息
  static Future<Message?> addMessage({
    required String sessionId,
    required String content,
    String messageType = 'text',
    String sender = 'user',
    String? mediaPath,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sessions/add_message'),
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: jsonEncode({
          'session_id': sessionId,
          'content': content,
          'message_type': messageType,
          'sender': sender,
          'media_path': mediaPath,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return _parseMessage(data['message']);
      }

      return null;
    } catch (e) {
      print('添加消息失败: $e');
      return null;
    }
  }

  /// 解析后端Session数据为前端Project模型
  ///
  /// 应用所有必要的数据转换：
  /// - 状态映射（英文枚举 → 中文字符串）
  /// - 时间转换（ISO8601字符串 → DateTime）
  static Project _parseSession(Map<String, dynamic> json) {
    return Project(
      id: json['id'],
      title: json['title'],
      progress: (json['progress'] as num).toDouble(),
      icon: json['icon'],
      status: StatusMapper.fromBackend(json['status']), // ⭐ 状态映射
      createdAt: TimeConverter.fromIso(json['created_at']), // ⭐ 时间转换
      updatedAt: TimeConverter.fromIso(json['updated_at']), // ⭐ 时间转换
      messages: (json['messages'] as List)
          .map((m) => _parseMessage(m))
          .toList(),
    );
  }

  /// 解析后端Message数据为前端Message模型
  ///
  /// 应用所有必要的数据转换：
  /// - Sender映射（assistant/system → bot）
  /// - 时间转换（ISO8601字符串 → DateTime）
  static Message _parseMessage(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'],
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.text,
      ),
      sender: SenderMapper.fromBackend(json['sender']), // ⭐ Sender映射
      timestamp: TimeConverter.fromIso(json['timestamp']), // ⭐ 时间转换
      mediaPath: json['media_path'],
    );
  }

  /// 处理多模态输入（视频+图片+文本）
  ///
  /// 发送视频、图片和文本指令到后端进行处理
  static Future<ProcessResult?> processMultimodal({
    required String sessionId,
    required String text,
    File? videoFile,
    List<File>? imageFiles,
    bool executeAsync = true,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/sessions/process-multimodal'),
      );

      // 添加表单字段
      request.fields['session_id'] = sessionId;
      request.fields['text'] = text;
      request.fields['execute_async'] = executeAsync ? 'true' : 'false';

      // 添加视频文件
      if (videoFile != null) {
        var videoStream = http.ByteStream(videoFile.openRead());
        var videoLength = await videoFile.length();
        var multipartFile = http.MultipartFile(
          'video',
          videoStream,
          videoLength,
          filename: videoFile.path.split('/').last,
        );
        request.files.add(multipartFile);
      }

      // 添加图片文件
      if (imageFiles != null) {
        for (var imageFile in imageFiles) {
          var imageStream = http.ByteStream(imageFile.openRead());
          var imageLength = await imageFile.length();
          var multipartFile = http.MultipartFile(
            'images',
            imageStream,
            imageLength,
            filename: imageFile.path.split('/').last,
          );
          request.files.add(multipartFile);
        }
      }

      // 发送请求
      print('发送多模态处理请求到: $baseUrl/sessions/process-multimodal');
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      print('响应状态码: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        print('✅ 后端处理成功');
        return ProcessResult.fromJson(data);
      } else {
        // 详细记录错误信息
        print('❌ 后端处理失败:');
        print('   状态码: ${response.statusCode}');
        print('   响应体: ${response.body}');

        // 解析错误详情
        String errorMessage = '处理失败';
        try {
          final errorData = jsonDecode(response.body);
          if (errorData.containsKey('detail')) {
            errorMessage = '${response.statusCode} - ${errorData['detail']}';
          } else {
            errorMessage = '${response.statusCode} - ${response.body}';
          }
        } catch (_) {
          errorMessage = '${response.statusCode} - ${response.body}';
        }

        // 返回包含错误信息的ProcessResult
        return ProcessResult(
          success: false,
          response: '',
          errorMessage: errorMessage,
        );
      }
    } catch (e) {
      print('❌ 处理多模态输入异常: $e');
      return ProcessResult(
        success: false,
        response: '',
        errorMessage: '网络错误: $e',
      );
    }
  }

  /// 获取任务状态
  ///
  /// 用于轮询异步任务的处理进度
  static Future<TaskStatus?> getTaskStatus(String taskId) async {
    try {
      print('📡 获取任务状态: $baseUrl/tasks/$taskId');
      final response = await http.get(Uri.parse('$baseUrl/tasks/$taskId'));

      print('📡 任务状态响应码: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        print('📡 任务状态数据: $data');

        final taskData = data['task'];
        print('📡 任务详情:');
        print('   - status: ${taskData['status']}');
        print('   - video_url: ${taskData['video_url']}');
        print('   - output_path: ${taskData['output_path']}');

        return TaskStatus.fromJson(taskData);
      } else {
        print('❌ 获取任务状态失败: ${response.statusCode} - ${response.body}');
      }

      return null;
    } catch (e) {
      print('❌ 获取任务状态异常: $e');
      return null;
    }
  }

  /// 下载处理后的视频
  ///
  /// 从后端下载视频文件到本地
  static Future<String?> downloadVideo({
    required String videoUrl,
    String? filename,
  }) async {
    try {
      // 构建完整URL
      final fullUrl = videoUrl.startsWith('http')
          ? videoUrl
          : '$baseUrl$videoUrl';

      print('开始下载视频: $fullUrl');

      // 发送GET请求
      final response = await http.get(Uri.parse(fullUrl));

      if (response.statusCode == 200) {
        // 获取应用文档目录
        final appDir = await getApplicationDocumentsDirectory();
        final videosDir = Directory('${appDir.path}/videos');
        if (!await videosDir.exists()) {
          await videosDir.create(recursive: true);
        }

        // 生成文件名
        final fileName =
            filename ?? 'video_${DateTime.now().millisecondsSinceEpoch}.mp4';
        final filePath = '${videosDir.path}/$fileName';

        // 保存文件
        final file = File(filePath);
        await file.writeAsBytes(response.bodyBytes);

        print('视频下载成功: $filePath');
        return filePath;
      } else {
        print('下载视频失败: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('下载视频时出错: $e');
      return null;
    }
  }

  /// 获取媒体文件URL
  ///
  /// 将相对路径转换为可访问的完整URL
  static String getMediaUrl(String relativePath) {
    return '$baseUrl/media/$relativePath';
  }
}

/// 处理结果数据类
class ProcessResult {
  final bool success;
  final String? taskId;
  final String? videoUrl;
  final String? outputPath;
  final String? response;
  final String? errorMessage;
  final bool isAsync;

  ProcessResult({
    required this.success,
    this.taskId,
    this.videoUrl,
    this.outputPath,
    this.response,
    this.errorMessage,
    this.isAsync = false,
  });

  factory ProcessResult.fromJson(Map<String, dynamic> json) {
    final execution = json['execution'] as Map<String, dynamic>?;

    return ProcessResult(
      success: json['status'] == 'success',
      taskId: json['task_id'],
      videoUrl: execution?['video_url'] ?? json['video_url'],
      outputPath: execution?['output_path'] ?? json['output_path'],
      response: json['response'],
      errorMessage: json['error_message'],
      isAsync: json['async'] ?? false,
    );
  }
}

/// 任务状态数据类
class TaskStatus {
  final String taskId;
  final String sessionId;
  final String status;
  final String? videoUrl;
  final String? outputPath;
  final String? errorMessage;
  final double? executionTime;

  TaskStatus({
    required this.taskId,
    required this.sessionId,
    required this.status,
    this.videoUrl,
    this.outputPath,
    this.errorMessage,
    this.executionTime,
  });

  factory TaskStatus.fromJson(Map<String, dynamic> json) {
    return TaskStatus(
      taskId: json['task_id'],
      sessionId: json['session_id'],
      status: json['status'],
      videoUrl: json['video_url'],
      outputPath: json['output_path'],
      errorMessage: json['error_message'],
      executionTime: json['execution_time']?.toDouble(),
    );
  }

  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isRunning => status == 'running' || status == 'pending';
}
