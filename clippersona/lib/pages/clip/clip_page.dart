import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:path_provider/path_provider.dart';
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
    if (_pendingMedia.isNotEmpty && text.trim().isNotEmpty) {
      // 多模态消息：文本 + 媒体
      setState(() {
        _messages.add(
          Message.multimodal(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: text,
            sender: MessageSender.user,
            mediaList: mediaList,
          ),
        );
      });
    } else if (_pendingMedia.isNotEmpty) {
      // 仅媒体消息
      setState(() {
        _messages.add(
          Message.multimodal(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: '',
            sender: MessageSender.user,
            mediaList: mediaList,
          ),
        );
      });
    } else {
      // 仅文本消息
      setState(() {
        _messages.add(
          Message.text(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: text,
            sender: MessageSender.user,
          ),
        );
      });
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
    final processingMessageId = DateTime.now().millisecondsSinceEpoch
        .toString();
    setState(() {
      _messages.add(
        Message.text(
          id: processingMessageId,
          content: '正在处理您的请求，请稍候...',
          sender: MessageSender.bot,
        ),
      );
    });
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
        // 处理失败
        _updateBotMessage(
          processingMessageId,
          '处理失败：${result?.errorMessage ?? "未知错误"}',
        );
      }
    } catch (e) {
      _updateBotMessage(processingMessageId, '处理出错：$e');
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
        print('🔄 轮询次数: $retryCount, 获取任务状态...');
        final taskStatus = await BackendSessionService.getTaskStatus(taskId);

        if (taskStatus == null) {
          print('❌ 无法获取任务状态');
          _updateBotMessage(messageId, '无法获取任务状态');
          return;
        }

        print('📊 任务状态: ${taskStatus.status}');
        print('📊 videoUrl: ${taskStatus.videoUrl}');
        print('📊 outputPath: ${taskStatus.outputPath}');

        if (taskStatus.isCompleted) {
          // 任务完成
          print('✅ 任务完成！');
          if (taskStatus.videoUrl != null && taskStatus.videoUrl!.isNotEmpty) {
            print('📹 开始下载视频: ${taskStatus.videoUrl}');
            // 下载视频
            _downloadAndShowVideo(taskStatus.videoUrl!, messageId);
          } else {
            print('⚠️ 任务完成但videoUrl为空');
            print('   outputPath: ${taskStatus.outputPath}');
            _updateBotMessage(
              messageId,
              '视频处理完成，但未返回结果\noutputPath: ${taskStatus.outputPath ?? "null"}',
            );
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
    if (result.videoUrl != null) {
      _downloadAndShowVideo(result.videoUrl!, messageId);
    } else {
      _updateBotMessage(messageId, result.response ?? '处理完成');
    }
  }

  /// 下载并显示处理后的视频
  void _downloadAndShowVideo(String videoUrl, String messageId) async {
    try {
      _updateBotMessage(messageId, '正在下载处理后的视频...');

      final localPath = await BackendSessionService.downloadVideo(
        videoUrl: videoUrl,
      );

      if (localPath != null) {
        // 生成视频缩略图
        String? thumbnailPath;
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

        // 删除旧的处理中消息
        setState(() {
          _messages.removeWhere((msg) => msg.id == messageId);
        });

        // 添加包含视频和缩略图的消息
        setState(() {
          _messages.add(
            Message.media(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: '视频处理完成！',
              type: MessageType.video,
              sender: MessageSender.bot,
              mediaPath: localPath,
              thumbnailPath: thumbnailPath,
            ),
          );
        });

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
    setState(() {
      final index = _messages.indexWhere((msg) => msg.id == messageId);
      if (index != -1) {
        _messages[index] = Message.text(
          id: messageId,
          content: newContent,
          sender: MessageSender.bot,
          timestamp: _messages[index].timestamp,
        );
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

  // 开始对话 - 创建新会话
  Future<void> _startConversation() async {
    await _createNewProjectWithBackend();
    setState(() {
      _messages.clear();
    });
    await _loadHistoryProjects(); // 重新加载历史项目
  }

  Future<void> _onImagePick() async {
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
    // 显示选择对话框：相机或图库
    final ImageSource? source = await showDialog<ImageSource>(
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
                onTap: () => Navigator.pop(context, ImageSource.camera),
              ),
              ListTile(
                leading: const Icon(Icons.video_library, color: Colors.purple),
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
      // 从选择的来源获取视频
      final XFile? pickedFile = await _imagePicker.pickVideo(
        source: source,
        maxDuration: const Duration(minutes: 5),
      );

      if (pickedFile != null) {
        // 如果是新对话且还没有项目ID，创建新项目
        if (_currentProjectId == null) {
          await _createNewProjectWithBackend();
        }

        // 生成视频缩略图
        String? thumbnailPath;
        try {
          final tempDir = await getTemporaryDirectory();
          thumbnailPath = await VideoThumbnail.thumbnailFile(
            video: pickedFile.path,
            thumbnailPath: tempDir.path,
            imageFormat: ImageFormat.JPEG,
            maxWidth: 400,
            quality: 75,
          );
        } catch (e) {
          debugPrint('生成视频缩略图失败: $e');
        }

        // 添加到暂存区，不立即发送
        setState(() {
          _pendingMedia.add(
            MediaItem(
              path: pickedFile.path,
              type: MediaType.video,
              thumbnailPath: thumbnailPath,
            ),
          );
        });
      }
    } catch (e) {
      // 显示错误提示
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('选择视频失败: $e'), backgroundColor: Colors.red),
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: ClipAppBar(
        onHistoryTap: _toggleHistory,
        onNewConversationTap: _createNewConversation,
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
                  userAvatarPath: _userAvatarPath,
                ),
              ),
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
