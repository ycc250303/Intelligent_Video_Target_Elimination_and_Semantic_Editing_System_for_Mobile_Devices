import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:path_provider/path_provider.dart';
import '../../models/message.dart';
import '../../models/project_models.dart';
import '../../services/project_service.dart';
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
  bool _isRecording = false;
  String? _currentProjectId;
  bool _isHistoryOpen = false;
  List<Project> _historyProjects = [];
  late AnimationController _historyAnimationController;
  late Animation<double> _historySlideAnimation;

  @override
  void initState() {
    super.initState();
    _initializeProject();
    _loadHistoryProjects();
    _initializeAnimations();
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
      final project = await ProjectService.instance.createNewProject();
      setState(() {
        _currentProjectId = project.id;
      });
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

    // 根据内容生成机器人回复
    String botResponseTrigger = text.trim().isNotEmpty
        ? text
        : (hadMedia ? '图片视频' : '');
    _simulateBotResponse(botResponseTrigger);
  }

  void _simulateBotResponse(String userMessage) {
    Future.delayed(const Duration(seconds: 1), () {
      setState(() {
        _messages.add(
          Message.text(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: _getBotResponse(userMessage),
            sender: MessageSender.bot,
          ),
        );
      });
      _scrollToBottom();
      _saveMessages();
    });
  }

  String _getBotResponse(String userMessage) {
    final message = userMessage.toLowerCase();

    if (message.contains('视频') || message.contains('剪辑')) {
      return '我收到了你的视频剪辑需求。请上传你的视频文件，我会帮你分析并提供剪辑建议。';
    } else if (message.contains('图片') || message.contains('照片')) {
      return '我看到了你的图片。我可以帮你进行图片编辑、滤镜处理或者制作图片合集。';
    } else if (message.contains('语音') || message.contains('音频')) {
      return '我收到了你的语音消息。我可以帮你进行音频处理、降噪或者音频剪辑。';
    } else if (message.contains('帮助') || message.contains('功能')) {
      return '我可以帮你：\n• 视频剪辑和编辑\n• 图片处理和美化\n• 音频处理和剪辑\n• 提供剪辑建议和技巧\n• 回答剪辑相关问题';
    } else {
      return '我理解你的需求。请告诉我具体想要进行什么剪辑操作，或者上传相关素材，我会为你提供帮助。';
    }
  }

  void _onVoiceStart() {
    setState(() {
      _isRecording = true;
    });
  }

  void _onVoiceStop() {
    setState(() {
      _isRecording = false;
    });

    // 模拟语音识别结果
    _sendMessage('[语音消息] 用户发送了一段语音');
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
    final project = await ProjectService.instance.createNewProject();
    setState(() {
      _currentProjectId = project.id;
      _messages.clear();
      _isHistoryOpen = false;
    });
    _loadHistoryProjects(); // 重新加载历史项目
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
      // 删除所有历史项目
      for (final project in _historyProjects) {
        await ProjectService.instance.deleteProject(project.id);
      }

      // 创建新对话
      await _createNewConversation();

      // 重新加载历史
      await _loadHistoryProjects();

      // 关闭侧边栏
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

  // 开始对话
  void _startConversation() {
    _sendMessage('你好，我想开始剪辑工作');
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
          final project = await ProjectService.instance.createNewProject();
          setState(() {
            _currentProjectId = project.id;
          });
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
                onVoiceStart: _onVoiceStart,
                onVoiceStop: _onVoiceStop,
                onImagePick: _onImagePick,
                onVideoPick: _onVideoPick,
                isRecording: _isRecording,
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
