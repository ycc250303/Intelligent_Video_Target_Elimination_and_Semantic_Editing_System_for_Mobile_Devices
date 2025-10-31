import 'package:flutter/material.dart';
import 'models/persona_models.dart';
import 'sections/style_card_management_section.dart';
import 'sections/growth_trajectory_section.dart';
import '../../services/style_card_service.dart';

class PersonaPage extends StatefulWidget {
  const PersonaPage({super.key});

  @override
  State<PersonaPage> createState() => _PersonaPageState();
}

class _PersonaPageState extends State<PersonaPage> {
  List<StyleCard> _styleCards = [];

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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Persona'),
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
            const SizedBox(height: 32),

            // 成长轨迹部分
            GrowthTrajectorySection(
              growthData: _growthData,
              milestone: '里程碑:完成100次调整',
            ),
          ],
        ),
      ),
    );
  }
}
