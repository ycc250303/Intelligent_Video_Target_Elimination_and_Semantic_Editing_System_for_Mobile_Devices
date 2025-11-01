import 'package:flutter/material.dart';
import '../../../models/recommendation.dart';

/// 智能推荐卡片组件
class RecommendationChips extends StatelessWidget {
  final List<Recommendation> recommendations;
  final Function(String action, String displayName) onRecommendationTap;
  final VoidCallback? onClose;

  const RecommendationChips({
    super.key,
    required this.recommendations,
    required this.onRecommendationTap,
    this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    if (recommendations.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFF667EEA).withOpacity(0.15),
            const Color(0xFF764BA2).withOpacity(0.15),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF667EEA).withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // 标题栏（精简版）
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF667EEA).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Color(0xFF667EEA),
                  size: 16,
                ),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  '💡 智能推荐',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (onClose != null)
                IconButton(
                  icon: const Icon(
                    Icons.close,
                    color: Colors.white70,
                    size: 18,
                  ),
                  onPressed: onClose,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  visualDensity: VisualDensity.compact,
                ),
            ],
          ),
          const SizedBox(height: 8),

          // 推荐操作卡片
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: recommendations.take(5).map((rec) {
              return _buildRecommendationChip(rec);
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationChip(Recommendation rec) {
    // 根据置信度选择颜色
    Color chipColor;
    if (rec.confidence >= 0.8) {
      chipColor = const Color(0xFF10B981); // 绿色 - 高置信度
    } else if (rec.confidence >= 0.6) {
      chipColor = const Color(0xFF3B82F6); // 蓝色 - 中置信度
    } else {
      chipColor = const Color(0xFF8B5CF6); // 紫色 - 低置信度
    }

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => onRecommendationTap(rec.action, rec.actionDisplayName),
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: chipColor.withOpacity(0.2),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: chipColor.withOpacity(0.4), width: 1.5),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 置信度圆环
              Container(
                width: 20,
                height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: chipColor.withOpacity(0.3),
                ),
                child: Center(
                  child: Text(
                    '${rec.confidencePercent}',
                    style: TextStyle(
                      color: chipColor,
                      fontSize: 9,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 6),
              // 操作名称
              Text(
                rec.actionDisplayName,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 工作流模板组件
class WorkflowTemplatesList extends StatelessWidget {
  final List<WorkflowTemplate> templates;
  final Function(WorkflowTemplate template) onTemplateTap;

  const WorkflowTemplatesList({
    super.key,
    required this.templates,
    required this.onTemplateTap,
  });

  @override
  Widget build(BuildContext context) {
    if (templates.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 4),
            child: Row(
              children: [
                const Icon(Icons.auto_fix_high, color: Colors.amber, size: 16),
                const SizedBox(width: 4),
                const Text(
                  '⚡ 常用工作流',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          ...templates.take(2).map((template) {
            return _buildTemplateCard(template);
          }),
        ],
      ),
    );
  }

  Widget _buildTemplateCard(WorkflowTemplate template) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => onTemplateTap(template),
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: Colors.amber.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                // 图标
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Icon(
                    Icons.playlist_play,
                    color: Colors.amber,
                    size: 16,
                  ),
                ),
                const SizedBox(width: 8),
                // 工作流信息
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        template.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        template.stepsDisplay,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.7),
                          fontSize: 11,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                // 置信度标签
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 6,
                    vertical: 3,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.amber.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    '${template.confidencePercent}%',
                    style: const TextStyle(
                      color: Colors.amber,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
