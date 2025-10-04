import 'package:flutter/material.dart';
import '../models/persona_models.dart';

class StyleCardManagementSection extends StatelessWidget {
  final List<StyleCard> styleCards;
  final double styleFusionRatio;
  final ValueChanged<double> onStyleFusionRatioChanged;

  const StyleCardManagementSection({
    super.key,
    required this.styleCards,
    required this.styleFusionRatio,
    required this.onStyleFusionRatioChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('风格卡管理'),
        const SizedBox(height: 16),
        _buildStyleCards(),
        const SizedBox(height: 24),
        _buildStyleFusionRatio(),
      ],
    );
  }

  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 20,
          decoration: const BoxDecoration(
            color: Color(0xFF8B5CF6),
            borderRadius: BorderRadius.all(Radius.circular(2)),
          ),
        ),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildStyleCards() {
    return Row(
      children: styleCards
          .map(
            (card) => Expanded(
              child: Container(
                margin: const EdgeInsets.only(right: 8),
                child: _buildStyleCard(card),
              ),
            ),
          )
          .toList(),
    );
  }

  Widget _buildStyleCard(StyleCard card) {
    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF374151),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(12),
                  topRight: Radius.circular(12),
                ),
              ),
              child: const Center(
                child: Icon(Icons.image, color: Colors.grey, size: 32),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Column(
              children: [
                Text(
                  card.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  height: 32,
                  child: ElevatedButton(
                    onPressed: () {
                      // 处理下载
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF8B5CF6),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      '下载',
                      style: TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStyleFusionRatio() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '风格融合比例',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        SliderTheme(
          data: const SliderThemeData(
            activeTrackColor: Color(0xFF8B5CF6),
            inactiveTrackColor: Color(0xFF374151),
            thumbColor: Colors.white,
            overlayColor: Color(0xFF8B5CF6),
          ),
          child: Slider(
            value: styleFusionRatio,
            onChanged: onStyleFusionRatioChanged,
            min: 0.0,
            max: 1.0,
          ),
        ),
        Text(
          '${(styleFusionRatio * 100).toInt()}% 我的风格',
          style: const TextStyle(color: Colors.white, fontSize: 14),
        ),
      ],
    );
  }
}
