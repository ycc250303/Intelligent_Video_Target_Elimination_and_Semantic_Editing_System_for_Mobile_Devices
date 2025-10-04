import 'package:flutter/material.dart';
import '../../models/message.dart';
import '../../models/project_models.dart';
import '../../services/project_service.dart';
import 'widgets/chat_input.dart';
import 'widgets/delete_dialog.dart';
import 'widgets/clip_app_bar.dart';
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
    if (text.trim().isEmpty) return;

    // 如果是新对话且还没有项目ID，创建新项目
    if (_currentProjectId == null) {
      final project = await ProjectService.instance.createNewProject();
      setState(() {
        _currentProjectId = project.id;
      });
    }

    setState(() {
      _messages.add(
        Message.text(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: text,
          sender: MessageSender.user,
        ),
      );
    });

    _scrollToBottom();
    _saveMessages();
    _simulateBotResponse(text);
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

  void _onImagePick() {
    // 模拟图片选择
    setState(() {
      _messages.add(
        Message.media(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: '我上传了一张图片',
          type: MessageType.image,
          sender: MessageSender.user,
          mediaPath: 'assets/placeholder.png',
        ),
      );
    });
    _scrollToBottom();
    _simulateBotResponse('图片');
  }

  void _onVideoPick() {
    // 模拟视频选择
    setState(() {
      _messages.add(
        Message.media(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: '我上传了一个视频',
          type: MessageType.video,
          sender: MessageSender.user,
          mediaPath: 'assets/placeholder.mp4',
        ),
      );
    });
    _scrollToBottom();
    _simulateBotResponse('视频');
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
