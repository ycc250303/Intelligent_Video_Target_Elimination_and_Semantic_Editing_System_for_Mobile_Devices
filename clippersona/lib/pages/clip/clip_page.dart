import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../models/message.dart';
import '../../models/project_models.dart';
import '../../services/project_service.dart';
import '../../services/backend_session_service.dart';
import '../../services/avatar_service.dart';
import '../../config/app_locales.dart';
import 'widgets/chat_input.dart';
import 'widgets/delete_dialog.dart';
import 'widgets/clip_app_bar.dart';
import 'widgets/media_preview_bar.dart';
import 'sections/history_sidebar.dart';
import 'sections/chat_messages_section.dart';

class ClipPage extends StatefulWidget {
  final String? projectId;

  const ClipPage({super.key, this.projectId});

  @override
  State<ClipPage> createState() => _ClipPageState();
}

class _ClipPageState extends State<ClipPage> with TickerProviderStateMixin {
  final List<Message> _messages = [];
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _imagePicker = ImagePicker();
  final List<MediaItem> _pendingMedia = []; // 暂存的媒体文件
  String? _currentProjectId;
  bool _isHistoryOpen = false;
  List<Project> _historyProjects = [];
  String? _userAvatarPath; // 用户头像路径
  late AnimationController _historyAnimationController;
  late Animation<double> _historySlideAnimation;

  @override
  void initState() {
    super.initState();
    _initializeProject();
    _loadHistoryProjects();
    _loadUserAvatar();
    _initializeAnimations();
  }

  // 加载用户头像
  Future<void> _loadUserAvatar() async {
    final avatarPath = await AvatarService.getAvatarPath();
    if (mounted) {
      setState(() {
        _userAvatarPath = avatarPath;
      });
    }
  }

  void _initializeAnimations() {
    _historyAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1600),
      vsync: this,
    );
    _historySlideAnimation = Tween<double>(begin: -1.0, end: 0.0).animate(
      CurvedAnimation(
        parent: _historyAnimationController,
        curve: Curves.elasticOut,
      ),
    );
  }

  Future<void> _initializeProject() async {
    if (widget.projectId != null) {
      // 加载现有项目
      final project = await ProjectService.instance.getProjectById(
        widget.projectId!,
      );
      if (project != null) {
        setState(() {
          _currentProjectId = project.id;
          _messages.addAll(project.messages);
        });
      }
    }
    // 如果没有指定项目ID，不自动创建项目，等待用户点击开始对话
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _historyAnimationController.dispose();
    super.dispose();
  }

  void _sendMessage(String text) async {
    // 如果没有文本也没有媒体，不发送
    if (text.trim().isEmpty && _pendingMedia.isEmpty) return;

    // === 输入验证 ===
    final hasText = text.trim().isNotEmpty;
    final hasVideo = _pendingMedia.any((m) => m.type == MediaType.video);
    final hasImage = _pendingMedia.any((m) => m.type == MediaType.image);

    // 1️⃣ 只有视频或只有图片（无文本） → 提醒用户补充指令
    if (!hasText && (hasVideo || hasImage)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              hasVideo
                  ? '请输入您想对视频进行的操作指令\n例如：裁剪前5秒、加速2倍、添加滤镜等'
                  : '请输入您想对图片进行的操作指令\n例如：生成视频、添加动画效果等',
            ),
            backgroundColor: Colors.orange,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return; // 不发送，让用户补充文本
    }

    // 2️⃣ 文本+视频+图片（同时存在） → 暂不支持
    if (hasVideo && hasImage) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('暂不支持同时处理视频和图片\n请选择其中一种类型的媒体进行处理'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 4),
          ),
        );
      }
      return; // 不发送
    }

    // 3️⃣ 验证通过的场景：
    // ✅ 纯文本（文生视频）
    // ✅ 文本+图片（图生视频）
    // ✅ 文本+视频（视频编辑）

    print('📤 发送消息 - 文本: $hasText, 视频: $hasVideo, 图片: $hasImage');

    // 如果是新对话且还没有项目ID，创建新项目
    if (_currentProjectId == null) {
      await _createNewProjectWithBackend();
    }

    // 将暂存的媒体转换为 MessageMedia 列表
    final mediaList = _pendingMedia.map((item) {
      return MessageMedia(
        path: item.path,
        type: item.type == MediaType.image ? 'image' : 'video',
        thumbnailPath: item.thumbnailPath,
      );
    }).toList();

    // 根据内容类型发送不同的消息
    final userMessageId = 'user_${DateTime.now().millisecondsSinceEpoch}';

    if (_pendingMedia.isNotEmpty && text.trim().isNotEmpty) {
      // 多模态消息：文本 + 媒体
      print(
        '📝 添加用户多模态消息: "$text" + ${mediaList.length}个媒体, ID: $userMessageId',
      );
      setState(() {
        _messages.add(
          Message.multimodal(
            id: userMessageId,
            content: text,
            sender: MessageSender.user,
            mediaList: mediaList,
          ),
        );
      });
      print('✅ 用户消息已添加，当前消息总数: ${_messages.length}');
    } else if (_pendingMedia.isNotEmpty) {
      // 仅媒体消息
      print('📝 添加用户仅媒体消息: ${mediaList.length}个媒体, ID: $userMessageId');
      setState(() {
        _messages.add(
          Message.multimodal(
            id: userMessageId,
            content: '',
            sender: MessageSender.user,
            mediaList: mediaList,
          ),
        );
      });
      print('✅ 用户消息已添加，当前消息总数: ${_messages.length}');
    } else {
      // 仅文本消息
      print('📝 添加用户纯文本消息: "$text", ID: $userMessageId');
      setState(() {
        _messages.add(
          Message.text(
            id: userMessageId,
            content: text,
            sender: MessageSender.user,
          ),
        );
      });
      print('✅ 用户消息已添加，当前消息总数: ${_messages.length}');
    }

    // 清空暂存区
    final hadMedia = _pendingMedia.isNotEmpty;
    setState(() {
      _pendingMedia.clear();
    });

    _scrollToBottom();
    _saveMessages();

    // 调用后端API进行处理（如果有媒体或有效文本）
    if (hadMedia || text.trim().isNotEmpty) {
      _processWithBackend(text, mediaList);
    }
  }

  /// 使用后端API处理用户输入
  void _processWithBackend(String text, List<MessageMedia> mediaList) async {
    // 1. 显示"处理中"状态
    // 延迟1ms确保ID不与用户消息冲突
    await Future.delayed(const Duration(milliseconds: 1));
    final processingMessageId = 'bot_${DateTime.now().millisecondsSinceEpoch}';

    print('🤖 添加机器人"处理中"消息，ID: $processingMessageId');
    setState(() {
      _messages.add(
        Message.text(
          id: processingMessageId,
          content: '正在处理您的请求，请稍候...',
          sender: MessageSender.bot,
        ),
      );
    });
    print('✅ 机器人消息已添加，当前消息总数: ${_messages.length}');
    _scrollToBottom();
    _saveMessages();

    try {
      // 2. 准备文件
      File? videoFile;
      List<File>? imageFiles;

      for (var media in mediaList) {
        if (media.type == 'video') {
          videoFile = File(media.path);
        } else if (media.type == 'image') {
          imageFiles ??= [];
          imageFiles.add(File(media.path));
        }
      }

      // 3. 调用后端API
      final result = await BackendSessionService.processMultimodal(
        sessionId: _currentProjectId!,
        text: text.isEmpty ? '请处理这个视频' : text,
        videoFile: videoFile,
        imageFiles: imageFiles,
        executeAsync: true, // 使用异步处理
      );

      if (result != null && result.success) {
        if (result.isAsync && result.taskId != null) {
          // 异步处理：轮询任务状态
          _pollTaskStatus(result.taskId!, processingMessageId);
        } else {
          // 同步处理：直接显示结果
          _handleProcessResult(result, processingMessageId);
        }
      } else {
        // 处理失败 - 输出详细日志，但向用户显示友好消息
        final errorDetail = result?.errorMessage ?? "未知错误";
        print('❌ 后端处理失败，详细错误: $errorDetail');

        // 向用户显示更友好的提示
        String friendlyMessage = '抱歉，处理遇到了一些问题';
        if (errorDetail.contains('422') ||
            errorDetail.contains('Unprocessable')) {
          friendlyMessage = '抱歉，上传的文件格式可能有问题，请重试';
        } else if (errorDetail.contains('timeout') ||
            errorDetail.contains('超时')) {
          friendlyMessage = '处理时间有点长，请稍后再试';
        } else if (errorDetail.contains('network') ||
            errorDetail.contains('网络')) {
          friendlyMessage = '网络似乎不太稳定，请检查连接后重试';
        }

        _updateBotMessage(processingMessageId, friendlyMessage);
      }
    } catch (e) {
      // 捕获异常 - 输出详细日志
      print('❌ 处理多模态输入异常，详细信息: $e');
      print('异常类型: ${e.runtimeType}');

      // 向用户显示友好提示
      _updateBotMessage(processingMessageId, '抱歉，处理遇到了一些问题，请稍后重试');
    }
  }

  /// 轮询异步任务状态
  void _pollTaskStatus(String taskId, String messageId) async {
    print('🔄 开始轮询任务状态，task_id: $taskId');

    int retryCount = 0;
    const maxRetries = 60; // 最多轮询60次（2分钟）
    const pollInterval = Duration(seconds: 2);

    while (retryCount < maxRetries) {
      await Future.delayed(pollInterval);
      retryCount++;

      try {
        // 每10次才打印一次日志，减少日志输出
        if (retryCount % 10 == 1 || retryCount == 1) {
          print('🔄 轮询次数: $retryCount/$maxRetries, 获取任务状态...');
        }

        final taskStatus = await BackendSessionService.getTaskStatus(taskId);

        if (taskStatus == null) {
          print('❌ 无法获取任务状态');
          _updateBotMessage(messageId, '无法获取任务状态');
          return;
        }

        // 只在状态变化时打印
        if (retryCount % 5 == 0) {
          print('📊 任务状态: ${taskStatus.status}');
        }

        if (taskStatus.isCompleted) {
          print('✅ 任务完成！outputPath: ${taskStatus.outputPath}');
          print('   outputType: ${taskStatus.outputType}');

          final mediaUrl = taskStatus.effectiveMediaUrl;
          if (mediaUrl != null && mediaUrl.isNotEmpty) {
            print('📹 开始下载媒体 (${taskStatus.outputType}): $mediaUrl');
            // 根据类型下载媒体（图片或视频）
            _downloadAndShowMedia(
              mediaUrl: mediaUrl,
              messageId: messageId,
              isImage: taskStatus.isImage,
            );
          } else {
            // mediaUrl为空 → 可能是不支持的操作或解析失败
            print('⚠️ 任务完成但mediaUrl为空');
            print('   outputPath: ${taskStatus.outputPath}');

            // 给用户更友好的提示
            _updateBotMessage(messageId, '抱歉，当前系统暂不支持此操作');
          }
          return;
        } else if (taskStatus.isFailed) {
          // 任务失败
          print('❌ 任务失败: ${taskStatus.errorMessage}');
          _updateBotMessage(
            messageId,
            '处理失败：${taskStatus.errorMessage ?? "未知错误"}',
          );
          return;
        } else {
          // 任务还在进行中，更新进度消息
          print('⏳ 任务进行中... (${retryCount * 2}秒)');
          _updateBotMessage(messageId, '正在处理中...（${retryCount * 2}秒）');
        }
      } catch (e) {
        print('❌ 轮询任务状态出错: $e');
        // 继续轮询
      }
    }

    // 超时
    print('⏰ 轮询超时');
    _updateBotMessage(messageId, '处理超时，请稍后查看');
  }

  /// 处理同步返回的结果
  void _handleProcessResult(ProcessResult result, String messageId) async {
    final mediaUrl = result.effectiveMediaUrl;
    if (mediaUrl != null) {
      _downloadAndShowMedia(
        mediaUrl: mediaUrl,
        messageId: messageId,
        isImage: result.isImage,
      );
    } else {
      _updateBotMessage(messageId, result.response ?? '处理完成');
    }
  }

  /// 下载并显示处理后的媒体（图片或视频）
  void _downloadAndShowMedia({
    required String mediaUrl,
    required String messageId,
    required bool isImage,
  }) async {
    try {
      final mediaType = isImage ? '图片' : '视频';
      _updateBotMessage(messageId, '正在下载处理后的$mediaType...');

      final localPath = await BackendSessionService.downloadVideo(
        videoUrl: mediaUrl,
      );

      if (localPath != null) {
        print('✅ $mediaType下载成功: $localPath');

        String? thumbnailPath;

        // 只有视频需要生成缩略图
        if (!isImage) {
          try {
            print('📸 生成视频缩略图: $localPath');
            final tempDir = await getTemporaryDirectory();
            thumbnailPath = await VideoThumbnail.thumbnailFile(
              video: localPath,
              thumbnailPath: tempDir.path,
              imageFormat: ImageFormat.JPEG,
              maxWidth: 400,
              quality: 75,
            );
            print('✅ 缩略图已生成: $thumbnailPath');
          } catch (e) {
            print('⚠️ 生成缩略图失败: $e');
          }
        }

        // 删除旧的处理中消息
        print('🗑️ 删除"处理中"消息，ID: $messageId');
        print('   删除前消息总数: ${_messages.length}');
        setState(() {
          _messages.removeWhere((msg) => msg.id == messageId);
        });
        print('   删除后消息总数: ${_messages.length}');

        // 添加包含媒体的消息
        final botMediaMessageId =
            'bot_media_${DateTime.now().millisecondsSinceEpoch}';
        print('📱 添加机器人$mediaType消息，ID: $botMediaMessageId');
        setState(() {
          _messages.add(
            Message.media(
              id: botMediaMessageId,
              content: '$mediaType${isImage ? "生成" : "处理"}完成！',
              type: isImage ? MessageType.image : MessageType.video,
              sender: MessageSender.bot,
              mediaPath: localPath,
              thumbnailPath: thumbnailPath,
            ),
          );

          // 🎯 自动将生成的媒体添加到多模态输入栏（暂存区）
          // 这样用户可以继续对这个媒体进行操作
          print('📥 将生成的$mediaType自动添加到输入栏，路径: $localPath');
          _pendingMedia.add(
            MediaItem(
              path: localPath,
              type: isImage ? MediaType.image : MediaType.video,
              thumbnailPath: thumbnailPath,
            ),
          );
          print('✅ $mediaType已添加到暂存区，当前暂存媒体数: ${_pendingMedia.length}');
        });
        print('✅ 机器人$mediaType消息已添加，当前消息总数: ${_messages.length}');

        _scrollToBottom();
        _saveMessages();
      } else {
        _updateBotMessage(messageId, '下载视频失败');
      }
    } catch (e) {
      _updateBotMessage(messageId, '下载视频出错：$e');
    }
  }

  /// 更新机器人消息内容
  void _updateBotMessage(String messageId, String newContent) {
    print('📝 更新机器人消息，ID: $messageId, 新内容: "$newContent"');
    setState(() {
      final index = _messages.indexWhere((msg) => msg.id == messageId);
      if (index != -1) {
        print('   找到消息索引: $index');
        _messages[index] = Message.text(
          id: messageId,
          content: newContent,
          sender: MessageSender.bot,
          timestamp: _messages[index].timestamp,
        );
      } else {
        print('   ⚠️ 未找到消息！当前消息总数: ${_messages.length}');
      }
    });
    _saveMessages();
  }

  // 保存消息到项目
  Future<void> _saveMessages() async {
    if (_currentProjectId != null) {
      await ProjectService.instance.updateProjectMessages(
        _currentProjectId!,
        _messages,
      );
    }
  }

  // 加载历史项目
  Future<void> _loadHistoryProjects() async {
    final projects = await ProjectService.instance.getAllProjects();
    setState(() {
      _historyProjects = projects;
    });
  }

  // 切换历史侧边栏
  void _toggleHistory() {
    setState(() {
      _isHistoryOpen = !_isHistoryOpen;
    });

    if (_isHistoryOpen) {
      _historyAnimationController.forward();
    } else {
      _historyAnimationController.reverse();
    }
  }

  // 新建对话
  Future<void> _createNewConversation() async {
    await _createNewProjectWithBackend();
    setState(() {
      _messages.clear();
      _isHistoryOpen = false;
    });
    _loadHistoryProjects(); // 重新加载历史项目
  }

  // 创建新项目并同步到后端
  Future<void> _createNewProjectWithBackend() async {
    // 1. 在后端创建会话
    final backendProject = await BackendSessionService.createSession(
      '新对话 ${_formatDateTime(DateTime.now())}',
      '🎬',
    );

    if (backendProject != null) {
      // 2. 使用后端返回的session ID
      setState(() {
        _currentProjectId = backendProject.id;
      });

      // 3. 保存到本地
      await ProjectService.instance.saveProject(backendProject);
    } else {
      // 后端创建失败，使用本地ID（降级方案）
      final project = await ProjectService.instance.createNewProject();
      setState(() {
        _currentProjectId = project.id;
      });
    }
  }

  // 进入历史对话
  Future<void> _enterHistoryConversation(Project project) async {
    setState(() {
      _currentProjectId = project.id;
      _messages.clear();
      _messages.addAll(project.messages);
      _isHistoryOpen = false;
    });
    _scrollToBottom();
  }

  // 删除历史对话
  Future<void> _deleteHistoryConversation(Project project) async {
    // 如果删除的是当前对话，先创建新对话
    if (project.id == _currentProjectId) {
      await _createNewConversation();
    }

    // 删除后端会话
    print('🗑️ 删除会话: ${project.id}');
    final backendDeleted = await BackendSessionService.deleteSession(
      project.id,
    );
    if (backendDeleted) {
      print('✅ 后端会话已删除: ${project.id}');
    } else {
      print('⚠️ 后端会话删除失败: ${project.id}');
    }

    // 删除本地项目
    await ProjectService.instance.deleteProject(project.id);
    await _loadHistoryProjects();
  }

  // 删除所有历史对话
  Future<void> _deleteAllHistory() async {
    // 显示确认对话框
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(appLocales.confirmClearHistory),
          content: Text(appLocales.clearHistoryWarning),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(appLocales.cancel),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: Text(appLocales.confirm),
            ),
          ],
        );
      },
    );

    if (confirmed == true) {
      print('🗑️ 开始清空所有历史...');

      // 1. 删除所有本地历史项目
      for (final project in _historyProjects) {
        await ProjectService.instance.deleteProject(project.id);
      }
      print('✅ 本地历史已清空');

      // 2. 删除后端所有会话
      final result = await BackendSessionService.deleteAllSessions();
      if (result != null) {
        print('✅ 后端会话已清空，共删除 ${result['count']} 个');
      } else {
        print('⚠️ 后端会话清空失败');
      }

      // 3. 创建新对话
      await _createNewConversation();

      // 4. 重新加载历史
      await _loadHistoryProjects();

      // 5. 关闭侧边栏
      setState(() {
        _isHistoryOpen = false;
      });
    }
  }

  // 显示删除确认对话框
  void _showDeleteDialog(Project project) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return DeleteDialog(
          project: project,
          onCancel: () => Navigator.of(context).pop(),
          onConfirm: () {
            Navigator.of(context).pop();
            _deleteHistoryConversation(project);
          },
        );
      },
    );
  }

  // 格式化日期时间
  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final projectDate = DateTime(dateTime.year, dateTime.month, dateTime.day);

    if (projectDate == today) {
      return '今天 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (projectDate == yesterday) {
      return '昨天 ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else {
      return '${dateTime.month.toString().padLeft(2, '0')}-${dateTime.day.toString().padLeft(2, '0')} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    }
  }

  // 开始对话 - 创建新会话（智能剪辑模式）
  Future<void> _startConversation() async {
    await _createNewProjectWithBackend();
    setState(() {
      _messages.clear();
    });
    await _loadHistoryProjects(); // 重新加载历史项目
  }

  // 调用风格卡模式
  void _onStyleCardMode() {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('调用风格卡功能开发中...')));
  }

  // 创建风格卡模式
  void _onCreateStyleCardMode() {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('创建风格卡功能开发中...')));
  }

  /// 检查并请求图片权限
  Future<bool> _checkAndRequestPhotoPermission() async {
    // Android 13+ 使用 photos 权限，Android 12 及以下使用 storage 权限
    // permission_handler会自动处理版本适配
    Permission permission = Permission.photos;

    // 先检查新权限
    PermissionStatus status = await permission.status;
    if (status.isGranted) return true;

    // 如果新权限不可用（Android 12-），尝试旧权限
    if (status.isDenied) {
      // 尝试请求，如果是旧版本会自动fallback到storage
      status = await permission.request();
      if (status.isGranted) return true;

      // 如果还是不行，尝试旧的storage权限
      Permission storagePermission = Permission.storage;
      PermissionStatus storageStatus = await storagePermission.status;
      if (storageStatus.isGranted) return true;

      if (storageStatus.isDenied) {
        storageStatus = await storagePermission.request();
        if (storageStatus.isGranted) {
          print('✅ 图片权限已授予（使用storage）');
          return true;
        }
      }
    }

    return await _checkAndRequestPermission(permission, '图片');
  }

  /// 检查并请求视频权限
  Future<bool> _checkAndRequestVideoPermission() async {
    // Android 13+ 使用 videos 权限，Android 12 及以下使用 storage 权限
    Permission permission = Permission.videos;

    // 先检查新权限
    PermissionStatus status = await permission.status;
    if (status.isGranted) return true;

    // 如果新权限不可用（Android 12-），尝试旧权限
    if (status.isDenied) {
      // 尝试请求，如果是旧版本会自动fallback到storage
      status = await permission.request();
      if (status.isGranted) return true;

      // 如果还是不行，尝试旧的storage权限
      Permission storagePermission = Permission.storage;
      PermissionStatus storageStatus = await storagePermission.status;
      if (storageStatus.isGranted) return true;

      if (storageStatus.isDenied) {
        storageStatus = await storagePermission.request();
        if (storageStatus.isGranted) {
          print('✅ 视频权限已授予（使用storage）');
          return true;
        }
      }
    }

    return await _checkAndRequestPermission(permission, '视频');
  }

  /// 通用权限检查和请求方法
  Future<bool> _checkAndRequestPermission(
    Permission permission,
    String mediaType,
  ) async {
    // 检查当前权限状态
    PermissionStatus status = await permission.status;
    print('📱 $mediaType权限状态: $status');

    if (status.isGranted) {
      return true;
    }

    // 如果未授予，请求权限
    if (status.isDenied) {
      print('📱 请求$mediaType权限...');
      status = await permission.request();

      if (status.isGranted) {
        print('✅ $mediaType权限已授予');
        return true;
      }
    }

    // 如果被永久拒绝，引导用户到设置
    if (status.isPermanentlyDenied) {
      print('⚠️ $mediaType权限被永久拒绝，引导用户到设置');
      final shouldOpenSettings = await showDialog<bool>(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('需要权限'),
            content: Text(
              '访问$mediaType需要存储权限。\n\n'
              '请在"设置 → 应用 → CoEdit → 权限"中开启：\n'
              '• 照片和视频\n'
              '• 文件和媒体\n\n'
              '是否前往设置？',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('取消'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                style: TextButton.styleFrom(foregroundColor: Colors.blue),
                child: const Text('前往设置'),
              ),
            ],
          );
        },
      );

      if (shouldOpenSettings == true) {
        await openAppSettings();
      }
      return false;
    }

    // 其他情况（被拒绝但不是永久）
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('需要访问权限才能选择$mediaType'),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 3),
        ),
      );
    }
    return false;
  }

  Future<void> _onImagePick() async {
    // 1️⃣ 先检查并请求权限
    if (!await _checkAndRequestPhotoPermission()) {
      print('❌ 图片权限被拒绝');
      return;
    }

    // 显示选择对话框：相机或图库
    final ImageSource? source = await showDialog<ImageSource>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('选择图片来源'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt, color: Colors.blue),
                title: const Text('拍照'),
                onTap: () => Navigator.pop(context, ImageSource.camera),
              ),
              ListTile(
                leading: const Icon(Icons.photo_library, color: Colors.green),
                title: const Text('从图库选择'),
                onTap: () => Navigator.pop(context, ImageSource.gallery),
              ),
            ],
          ),
        );
      },
    );

    if (source == null) return;

    try {
      // 从选择的来源获取图片
      final XFile? pickedFile = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        // 添加到暂存区，不立即发送
        setState(() {
          _pendingMedia.add(
            MediaItem(path: pickedFile.path, type: MediaType.image),
          );
        });
      }
    } catch (e) {
      // 显示错误提示
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('选择图片失败: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _onVideoPick() async {
    print('📹 开始选择视频...');

    // 1️⃣ 先检查并请求权限
    if (!await _checkAndRequestVideoPermission()) {
      print('❌ 权限被拒绝');
      return;
    }

    // 显示选择对话框：相机或图库
    final String? source = await showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('选择视频来源'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.videocam, color: Colors.red),
                title: const Text('拍摄视频'),
                onTap: () => Navigator.pop(context, 'camera'),
              ),
              ListTile(
                leading: const Icon(Icons.video_library, color: Colors.purple),
                title: const Text('从图库选择'),
                onTap: () => Navigator.pop(context, 'gallery'),
              ),
            ],
          ),
        );
      },
    );

    if (source == null) {
      print('❌ 用户取消选择');
      return;
    }

    print('📹 选择来源: $source');

    try {
      String? videoPath;

      if (source == 'camera') {
        // 使用 image_picker 拍摄视频（相机功能正常）
        print('📹 调用相机拍摄视频...');
        final XFile? pickedFile = await _imagePicker.pickVideo(
          source: ImageSource.camera,
          maxDuration: const Duration(minutes: 5),
        );
        videoPath = pickedFile?.path;
        print('📹 拍摄结果: ${videoPath ?? "null"}');
      } else {
        // 使用 file_picker 从图库选择（兼容 Android 11+）
        print('📹 调用 FilePicker 选择视频...');
        FilePickerResult? result = await FilePicker.platform.pickFiles(
          type: FileType.video,
          allowMultiple: false,
        );

        if (result != null && result.files.single.path != null) {
          videoPath = result.files.single.path!;
          print('📹 FilePicker 返回: $videoPath');
        } else {
          print('❌ FilePicker 返回 null');
        }
      }

      if (videoPath != null) {
        print('✅ 视频选择成功: $videoPath');

        // 如果是新对话且还没有项目ID，创建新项目
        if (_currentProjectId == null) {
          await _createNewProjectWithBackend();
        }

        // 生成视频缩略图
        String? thumbnailPath;
        try {
          print('📸 生成视频缩略图...');
          final tempDir = await getTemporaryDirectory();
          thumbnailPath = await VideoThumbnail.thumbnailFile(
            video: videoPath,
            thumbnailPath: tempDir.path,
            imageFormat: ImageFormat.JPEG,
            maxWidth: 400,
            quality: 75,
          );
          print('✅ 缩略图生成成功: $thumbnailPath');
        } catch (e) {
          print('⚠️ 生成视频缩略图失败: $e');
        }

        // 添加到暂存区，不立即发送
        setState(() {
          _pendingMedia.add(
            MediaItem(
              path: videoPath!,
              type: MediaType.video,
              thumbnailPath: thumbnailPath,
            ),
          );
        });
        print('✅ 视频已添加到暂存区');
      } else {
        print('❌ 未选择视频');
      }
    } catch (e) {
      print('❌ 选择视频异常: $e');
      print('异常类型: ${e.runtimeType}');

      // 显示更详细的错误提示
      if (mounted) {
        String errorMsg = '选择视频失败';
        if (e.toString().contains('no_valid_video_uri')) {
          errorMsg = '无法访问所选视频，Android 11+ 系统限制';
        } else if (e.toString().contains('permission')) {
          errorMsg = '没有访问权限，请在设置中允许访问存储';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$errorMsg\n详情: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // 清空暂存区
  void _clearPendingMedia() {
    setState(() {
      _pendingMedia.clear();
    });
  }

  // 删除暂存区中的某个媒体项
  void _removePendingMedia(int index) {
    setState(() {
      _pendingMedia.removeAt(index);
    });
  }

  // 根据媒体路径从暂存区中删除媒体（用于反馈按钮）
  void _removeMediaFromBufferByPath(String mediaPath) {
    print('🗑️ 从缓冲区删除媒体: $mediaPath');
    setState(() {
      final initialCount = _pendingMedia.length;
      _pendingMedia.removeWhere((item) => item.path == mediaPath);
      final removedCount = initialCount - _pendingMedia.length;
      if (removedCount > 0) {
        print('✅ 已从缓冲区删除 $removedCount 个媒体，剩余: ${_pendingMedia.length}');
      } else {
        print('⚠️ 未找到要删除的媒体: $mediaPath');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    // 判断是否有活跃的会话
    final bool hasActiveSession = _currentProjectId != null;

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: ClipAppBar(
        onHistoryTap: _toggleHistory,
        onNewConversationTap: _createNewConversation,
        // 有会话时显示"新会话"，无会话时显示默认的"工作台"
        title: hasActiveSession ? '新会话' : null,
      ),
      body: Stack(
        children: [
          Column(
            children: [
              // 聊天消息列表
              Expanded(
                child: ChatMessagesSection(
                  messages: _messages,
                  scrollController: _scrollController,
                  historyProjects: _historyProjects,
                  onStartConversation: _startConversation,
                  onStyleCardMode: _onStyleCardMode,
                  onCreateStyleCardMode: _onCreateStyleCardMode,
                  userAvatarPath: _userAvatarPath,
                  onRemoveFromBuffer: _removeMediaFromBufferByPath,
                ),
              ),
              // 只有在有活跃会话时才显示媒体预览栏和输入框
              if (hasActiveSession) ...[
                // 媒体预览栏（暂存区）
                MediaPreviewBar(
                  mediaItems: _pendingMedia,
                  onClear: _clearPendingMedia,
                  onRemoveItem: _removePendingMedia,
                ),
                // 输入框
                ChatInput(
                  onSendMessage: _sendMessage,
                  onImagePick: _onImagePick,
                  onVideoPick: _onVideoPick,
                ),
              ],
            ],
          ),
          // 历史对话侧边栏
          if (_isHistoryOpen)
            AnimatedBuilder(
              animation: _historySlideAnimation,
              builder: (context, child) {
                return Positioned(
                  left:
                      _historySlideAnimation.value *
                      MediaQuery.of(context).size.width *
                      0.8,
                  top: 0,
                  bottom: 0,
                  child: SizedBox(
                    width: MediaQuery.of(context).size.width * 0.8,
                    child: HistorySidebar(
                      historyProjects: _historyProjects,
                      currentProjectId: _currentProjectId,
                      onClose: _toggleHistory,
                      onProjectTap: _enterHistoryConversation,
                      onProjectDelete: _showDeleteDialog,
                      onDeleteAll: _deleteAllHistory,
                      formatDateTime: _formatDateTime,
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }
}
