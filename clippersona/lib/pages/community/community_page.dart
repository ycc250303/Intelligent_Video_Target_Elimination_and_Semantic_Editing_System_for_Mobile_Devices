import 'package:flutter/material.dart';
import 'sections/posts_section.dart';
import 'widgets/community_header.dart';
import 'persona_detail_page.dart';
import '../persona/models/persona_models.dart';
import '../../services/avatar_service.dart';
import '../../services/style_card_service.dart';

class CommunityPage extends StatefulWidget {
  const CommunityPage({super.key});

  @override
  State<CommunityPage> createState() => _CommunityPageState();
}

class _CommunityPageState extends State<CommunityPage> {
  String? _userAvatarPath; // 用户头像路径
  List<StyleCard> _sharedStyleCards = [];
  List<Map<String, dynamic>> _posts = [];

  @override
  void initState() {
    super.initState();
    _initialize();

    // 监听头像变化
    AvatarService.avatarPathNotifier.addListener(_onAvatarChanged);
    // 监听风格卡变化
    StyleCardService.styleCardsNotifier.addListener(_onStyleCardsChanged);
  }

  @override
  void dispose() {
    AvatarService.avatarPathNotifier.removeListener(_onAvatarChanged);
    StyleCardService.styleCardsNotifier.removeListener(_onStyleCardsChanged);
    super.dispose();
  }

  /// 初始化数据加载
  Future<void> _initialize() async {
    await _loadUserAvatar();
    _loadSharedStyleCards();
  }

  /// 风格卡变化回调
  void _onStyleCardsChanged() {
    if (mounted) {
      _loadSharedStyleCards();
    }
  }

  /// 加载用户头像
  Future<void> _loadUserAvatar() async {
    final avatarPath = await AvatarService.getAvatarPath();
    if (mounted) {
      setState(() {
        _userAvatarPath = avatarPath;
      });
    }
  }

  /// 头像变化回调
  void _onAvatarChanged() {
    if (mounted) {
      final newAvatarPath = AvatarService.avatarPathNotifier.value;
      setState(() {
        _userAvatarPath = newAvatarPath;

        // 更新已经存在的"我"的帖子的头像
        for (var post in _posts) {
          if (post['user'] == '我') {
            post['avatar'] = newAvatarPath ?? 'assets/personaPage/robot.png';
          }
        }
      });
    }
  }

  /// 加载共享的风格卡并添加到 posts 列表
  void _loadSharedStyleCards() {
    if (!mounted) return;

    setState(() {
      // 从StyleCardService获取共享的风格卡
      _sharedStyleCards = StyleCardService.getSharedStyleCards();

      // 清空现有的风格卡帖子
      _posts.removeWhere((post) => post['isStyleCard'] == true);

      // 将共享的风格卡转换为 post 格式
      for (var styleCard in _sharedStyleCards) {
        _posts.insert(0, {
          'title': styleCard.title,
          'user': '我', // 当前用户
          'avatar':
              _userAvatarPath ?? 'assets/personaPage/robot.png', // 使用用户头像或默认头像
          'time': '刚刚',
          'content': styleCard.title,
          'likes': styleCard.comments,
          'comments': styleCard.comments,
          'image': styleCard.imageUrl.isEmpty
              ? 'assets/communityPage/persona.png' // 默认风格卡图片
              : styleCard.imageUrl,
          'isStyleCard': true, // 标记这是风格卡
          'styleCard': styleCard, // 保存原始风格卡数据
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CommunityHeader(
        onSearchPressed: _handleSearch,
        onAddPressed: _handleAddPost,
      ),
      body: PostsSection(posts: _posts, onPostTap: _handlePostTap),
    );
  }

  void _handleSearch() {
    // 处理搜索功能
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('搜索'),
        content: TextField(
          decoration: InputDecoration(
            hintText: '搜索帖子、用户或标签...',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('搜索'),
          ),
        ],
      ),
    );
  }

  void _handleAddPost() {
    // 处理发布功能
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('发布功能开发中...'), backgroundColor: Color(0xFF3498DB)),
    );
  }

  void _handlePostTap(Map<String, dynamic> post) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => PersonaDetailPage(persona: post)),
    );
  }
}
