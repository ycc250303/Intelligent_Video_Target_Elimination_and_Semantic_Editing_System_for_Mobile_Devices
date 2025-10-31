import 'package:flutter/material.dart';
import '../../persona/models/persona_models.dart';
import '../../../services/style_card_service.dart';

/// 风格卡选择器对话框
class StyleCardSelectorDialog extends StatefulWidget {
  const StyleCardSelectorDialog({super.key});

  @override
  State<StyleCardSelectorDialog> createState() =>
      _StyleCardSelectorDialogState();
}

class _StyleCardSelectorDialogState extends State<StyleCardSelectorDialog> {
  List<StyleCard> _styleCards = [];
  String? _selectedCardId;

  @override
  void initState() {
    super.initState();
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
    });
  }

  void _onStyleCardsChanged() {
    if (mounted) {
      _loadStyleCards();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 600),
        decoration: BoxDecoration(
          color: const Color(0xFF1F2937),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFF374151), width: 1),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 标题栏
            Container(
              padding: const EdgeInsets.all(20),
              decoration: const BoxDecoration(
                color: Color(0xFF111827),
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
              ),
              child: Row(
                children: [
                  const Icon(Icons.style, color: Color(0xFF8B5CF6), size: 24),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      '选择风格卡',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),

            // 风格卡列表
            Expanded(
              child: _styleCards.isEmpty
                  ? _buildEmptyState()
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _styleCards.length,
                      itemBuilder: (context, index) {
                        final card = _styleCards[index];
                        return _buildStyleCardItem(card);
                      },
                    ),
            ),

            // 底部按钮
            Container(
              padding: const EdgeInsets.all(16),
              decoration: const BoxDecoration(
                color: Color(0xFF111827),
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(20),
                  bottomRight: Radius.circular(20),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      style: TextButton.styleFrom(
                        backgroundColor: const Color(0xFF374151),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: const Text('取消'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _selectedCardId != null
                          ? () {
                              Navigator.pop(context);
                              // 暂时只提示，不实际调用
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('已选择风格卡，调用功能开发中...'),
                                  backgroundColor: const Color(0xFF8B5CF6),
                                ),
                              );
                            }
                          : null,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF8B5CF6),
                        foregroundColor: Colors.white,
                        disabledBackgroundColor: const Color(0xFF374151),
                        disabledForegroundColor: Colors.grey,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: const Text('调用'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建风格卡项
  Widget _buildStyleCardItem(StyleCard card) {
    final isSelected = _selectedCardId == card.id;

    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedCardId = card.id;
        });
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF8B5CF6).withOpacity(0.2)
              : const Color(0xFF374151),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? const Color(0xFF8B5CF6) : Colors.transparent,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            // 缩略图
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: const Color(0xFF1F2937),
                borderRadius: BorderRadius.circular(8),
                image: DecorationImage(
                  image: AssetImage(
                    card.imageUrl.isEmpty
                        ? 'assets/communityPage/persona.png'
                        : card.imageUrl,
                  ),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(width: 12),

            // 信息
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        card.title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      _buildStatusBadge(card.status),
                    ],
                  ),
                  if (card.isShared) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(
                          Icons.download,
                          color: Colors.grey,
                          size: 12,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${card.downloads}',
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 11,
                          ),
                        ),
                        const SizedBox(width: 12),
                        const Icon(Icons.comment, color: Colors.grey, size: 12),
                        const SizedBox(width: 4),
                        Text(
                          '${card.comments}',
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),

            // 选中指示器
            if (isSelected)
              const Icon(Icons.check_circle, color: Color(0xFF8B5CF6), size: 24)
            else
              const Icon(
                Icons.radio_button_unchecked,
                color: Colors.grey,
                size: 24,
              ),
          ],
        ),
      ),
    );
  }

  /// 状态标签
  Widget _buildStatusBadge(StyleCardStatus status) {
    Color color;
    String text;

    switch (status) {
      case StyleCardStatus.local:
        color = const Color(0xFF6B7280);
        text = '本地';
        break;
      case StyleCardStatus.shared:
        color = const Color(0xFF10B981);
        text = '已共享';
        break;
      case StyleCardStatus.downloadable:
        color = const Color(0xFF3B82F6);
        text = '社区';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color, width: 1),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// 空状态
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.style_outlined,
            size: 80,
            color: Colors.grey.withOpacity(0.3),
          ),
          const SizedBox(height: 16),
          Text(
            '暂无风格卡',
            style: TextStyle(color: Colors.grey.withOpacity(0.5), fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            '前往 Persona 页面创建风格卡',
            style: TextStyle(color: Colors.grey.withOpacity(0.4), fontSize: 14),
          ),
        ],
      ),
    );
  }
}
