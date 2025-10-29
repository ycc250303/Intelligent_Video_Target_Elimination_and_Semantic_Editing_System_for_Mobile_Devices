import 'package:flutter/material.dart';
import 'models/persona_models.dart';
import 'sections/my_persona_section.dart';
import 'sections/style_card_management_section.dart';
import 'sections/my_sharing_section.dart';
import 'sections/growth_trajectory_section.dart';
import '../../services/backend_session_service.dart';
import '../../services/project_service.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  double _styleFusionRatio = 0.7;

  // 🆕 真实人格数据
  Map<String, dynamic>? _personaData;
  bool _isLoading = true;
  String? _errorMessage;

  // 模拟数据（作为fallback）
  final List<Persona> _personas = [
    Persona(
      id: '1',
      title: '理性讲师',
      tag: '理性',
      tagColor: Colors.yellow,
      progress: 0.85,
      icon: Icons.person,
    ),
    Persona(
      id: '2',
      title: '搞笑弹幕',
      tag: '搞笑',
      tagColor: Colors.orange,
      progress: 0.45,
      icon: Icons.chat_bubble_outline,
    ),
  ];

  final List<StyleCard> _styleCards = [
    StyleCard(id: '1', title: '毒蛇型', imageUrl: '', isDownloaded: false),
    StyleCard(id: '2', title: '理性讲师', imageUrl: '', isDownloaded: true),
  ];

  final List<SharedPersona> _sharedPersonas = [
    SharedPersona(
      id: '1',
      title: '毒蛇型',
      downloads: 300,
      comments: 15,
      isEnabled: true,
    ),
  ];

  final List<GrowthData> _growthData = [
    GrowthData(value: 1, label: '0'),
    GrowthData(value: 2, label: '100'),
    GrowthData(value: 3, label: '200'),
    GrowthData(value: 2.5, label: '300'),
    GrowthData(value: 2.8, label: '400'),
    GrowthData(value: 3.2, label: '500'),
    GrowthData(value: 3.5, label: '600'),
    GrowthData(value: 3.8, label: '700'),
    GrowthData(value: 4.0, label: '800'),
  ];

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
        title: Text('Persona'),
        centerTitle: true,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(Icons.search),
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
            // 🆕 真实人格数据显示
            if (_isLoading)
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text(
                        '正在加载你的剪辑人格...',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ],
                  ),
                ),
              )
            else if (_errorMessage != null)
              Container(
                padding: EdgeInsets.all(16),
                margin: EdgeInsets.only(bottom: 24),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ],
                ),
              )
            else if (_personaData != null)
              _buildRealPersonaCard(_personaData!),

            // 我的Persona部分
            MyPersonaSection(personas: _personas),
            const SizedBox(height: 32),

            // 风格卡管理部分
            StyleCardManagementSection(
              styleCards: _styleCards,
              styleFusionRatio: _styleFusionRatio,
              onStyleFusionRatioChanged: (value) {
                setState(() {
                  _styleFusionRatio = value;
                });
              },
            ),
            const SizedBox(height: 32),

            // 我的共享部分
            MySharingSection(sharedPersonas: _sharedPersonas),
            const SizedBox(height: 32),

            // 成长轨迹部分
            GrowthTrajectorySection(
              growthData: _growthData,
              milestone: '里程请:完成100次调整',
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
