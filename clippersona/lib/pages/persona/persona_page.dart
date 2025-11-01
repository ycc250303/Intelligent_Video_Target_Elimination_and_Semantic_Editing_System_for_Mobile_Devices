import 'package:flutter/material.dart';
import 'models/persona_models.dart';
import 'sections/style_card_management_section.dart';
import '../../services/style_card_service.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  List<StyleCard> _styleCards = [];

  @override
  void initState() {
    super.initState();
    // 加载风格卡
    _loadStyleCards();
    // 监听风格卡变化
    StyleCardService.styleCardsNotifier.addListener(_onStyleCardsChanged);
  }

  @override
  void dispose() {
    StyleCardService.styleCardsNotifier.removeListener(_onStyleCardsChanged);
    super.dispose();
  }

  void _loadStyleCards() {
    setState(() {
      _styleCards = StyleCardService.getAllStyleCards();
      print('🔄 PersonaPage加载风格卡: ${_styleCards.length} 个');
      for (var card in _styleCards) {
        print('   - ${card.title}: ${card.operations.length} 个操作');
      }
    });
  }

  void _onStyleCardsChanged() {
    if (mounted) {
      setState(() {
        _styleCards = StyleCardService.getAllStyleCards();
        print('🔔 PersonaPage监听到风格卡变化: ${_styleCards.length} 个');
        for (var card in _styleCards) {
          print('   - ${card.title}: ${card.operations.length} 个操作');
        }
      });
    }
  }

  void _handleDownload(String cardId) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('下载功能开发中...'),
        duration: Duration(seconds: 1),
      ),
    );
  }

  void _handleDelete(String cardId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除这个风格卡吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              StyleCardService.deleteStyleCard(cardId);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('已删除'),
                  duration: Duration(seconds: 1),
                  backgroundColor: Color(0xFFEF4444),
                ),
              );
            },
            child: const Text('删除', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _handleShare(String cardId) {
    StyleCardService.shareStyleCard(cardId);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已共享到社区'),
        duration: Duration(seconds: 1),
        backgroundColor: Color(0xFF10B981),
      ),
    );
  }

  void _handleUnshare(String cardId) {
    StyleCardService.unshareStyleCard(cardId);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('已取消共享'),
        duration: Duration(seconds: 1),
        backgroundColor: Color(0xFFF59E0B),
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    _loadPersonaData();
  }

  /// 🆕 加载人格数据
  Future<void> _loadPersonaData() async {
    try {
      // 获取最近的会话ID
      final projects = await ProjectService.instance.getAllProjects();
      if (projects.isEmpty) {
        setState(() {
          _isLoading = false;
          _errorMessage = '暂无编辑数据，开始使用后系统会自动分析你的剪辑习惯';
        });
        return;
      }

      final sessionId = projects.first.id;

      // 获取人格数据
      final personaData = await BackendSessionService.getPersonaData(
        sessionId: sessionId,
      );

      if (mounted) {
        setState(() {
          _personaData = personaData;
          _isLoading = false;
          if (personaData == null) {
            _errorMessage = '人格数据正在生成中，需要更多操作记录（建议至少50次操作）';
          }
        });
      }
    } catch (e) {
      print('❌ 加载人格数据失败: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = '加载失败，请稍后重试';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('风格卡'),
        centerTitle: true,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // 处理搜索
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 风格卡管理部分（已合并"我的共享"功能）
            StyleCardManagementSection(
              styleCards: _styleCards,
              onDownload: _handleDownload,
              onDelete: _handleDelete,
              onShare: _handleShare,
              onUnshare: _handleUnshare,
            ),
          ],
        ),
      ),
    );
  }

  /// 🆕 构建真实人格数据卡片
  Widget _buildRealPersonaCard(Map<String, dynamic> personaData) {
    final statistics = personaData['statistics'] as Map<String, dynamic>? ?? {};
    final preferences =
        personaData['preferences'] as Map<String, dynamic>? ?? {};
    final totalOps = personaData['total_operations'] ?? 0;

    // 获取最常用操作
    final mostCommon =
        (statistics['most_common_actions'] as List?)?.take(5).toList() ?? [];

    // 获取效果偏好
    final effectTendencies =
        preferences['effect_tendencies'] as Map<String, dynamic>? ?? {};
    final topEffects = effectTendencies.entries.toList()
      ..sort((a, b) => (b.value as num).compareTo(a.value as num));

    return Container(
      margin: EdgeInsets.only(bottom: 24),
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF667EEA).withOpacity(0.2),
            Color(0xFF764BA2).withOpacity(0.2),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Color(0xFF667EEA).withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 标题
          Row(
            children: [
              Icon(Icons.auto_awesome, color: Color(0xFF667EEA), size: 24),
              SizedBox(width: 12),
              Text(
                '📊 你的剪辑人格',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 20),

          // 总操作数
          _buildStatRow(
            icon: Icons.edit,
            label: '总操作次数',
            value: '$totalOps 次',
            color: Colors.blue,
          ),
          SizedBox(height: 12),

          // 最常用操作
          if (mostCommon.isNotEmpty) ...[
            Text(
              '🎯 最常用操作',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 12),
            ...mostCommon.map((item) {
              final action = item[0] as String;
              final count = item[1] as int;
              final actionName = _getActionDisplayName(action);
              return Padding(
                padding: EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: Color(0xFF10B981),
                        shape: BoxShape.circle,
                      ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        actionName,
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                    Text(
                      '$count 次',
                      style: TextStyle(
                        color: Color(0xFF10B981),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              );
            }),
            SizedBox(height: 16),
          ],

          // 风格偏好
          if (topEffects.isNotEmpty) ...[
            Text(
              '🎨 你的风格特点',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            SizedBox(height: 12),
            ...topEffects.take(3).map((entry) {
              final effect = entry.key;
              final score = (entry.value as num).toDouble();
              final stars = (score * 5).round();
              return Padding(
                padding: EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        _getEffectDisplayName(effect),
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                    Row(
                      children: List.generate(5, (index) {
                        return Icon(
                          index < stars ? Icons.star : Icons.star_border,
                          color: Colors.amber,
                          size: 16,
                        );
                      }),
                    ),
                  ],
                ),
              );
            }),
          ],

          SizedBox(height: 16),

          // 刷新按钮
          Center(
            child: TextButton.icon(
              onPressed: () {
                setState(() {
                  _isLoading = true;
                });
                _loadPersonaData();
              },
              icon: Icon(Icons.refresh, color: Color(0xFF667EEA)),
              label: Text('重新分析', style: TextStyle(color: Color(0xFF667EEA))),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        SizedBox(width: 12),
        Text(label, style: TextStyle(color: Colors.white70)),
        Spacer(),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ],
    );
  }

  String _getActionDisplayName(String action) {
    const names = {
      'trim': '裁剪',
      'color_grading': '调色',
      'add_music': '添加音乐',
      'fast_cut': '快剪',
      'text_overlay': '字幕',
      'slow_motion': '慢动作',
      'filters': '滤镜',
      'transitions': '转场',
    };
    return names[action] ?? action;
  }

  String _getEffectDisplayName(String effect) {
    const names = {
      'cinematic_feel': '电影感',
      'warm_tone': '温暖色调',
      'rhythm_boost': '节奏感',
      'calm_warmth': '舒缓氛围',
      'epic_emotion': '史诗感',
      'speed_up': '快节奏',
      'clarity': '清晰度',
      'smooth_motion': '平滑运镜',
    };
    return names[effect] ?? effect;
  }
}
