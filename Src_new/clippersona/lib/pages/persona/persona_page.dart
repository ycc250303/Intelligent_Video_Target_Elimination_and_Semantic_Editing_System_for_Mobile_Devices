import 'package:flutter/material.dart';
import 'models/persona_models.dart';
import 'sections/my_persona_section.dart';
import 'sections/style_card_management_section.dart';
import 'sections/my_sharing_section.dart';
import 'sections/growth_trajectory_section.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  double _styleFusionRatio = 0.7;

  // 模拟数据
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
}
