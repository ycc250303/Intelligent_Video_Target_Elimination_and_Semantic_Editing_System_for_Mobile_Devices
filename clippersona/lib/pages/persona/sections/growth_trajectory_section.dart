import 'package:flutter/material.dart';
import '../models/persona_models.dart';

class GrowthTrajectorySection extends StatelessWidget {
  final List<GrowthData> growthData;
  final String milestone;

  const GrowthTrajectorySection({
    super.key,
    required this.growthData,
    required this.milestone,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('成长轨迹'),
        const SizedBox(height: 16),
        _buildGrowthChart(),
        const SizedBox(height: 16),
        _buildMilestone(),
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

  Widget _buildGrowthChart() {
    return Container(
      height: 200,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Expanded(
            child: CustomPaint(
              painter: GrowthChartPainter(growthData),
              child: Container(),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '0',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '100',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '200',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '300',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '400',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '500',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '600',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '700',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Text(
                '800',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMilestone() {
    return Text(
      milestone,
      style: const TextStyle(color: Colors.white, fontSize: 14),
    );
  }
}

class GrowthChartPainter extends CustomPainter {
  final List<GrowthData> data;

  GrowthChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    if (data.isEmpty) return;

    final paint = Paint()
      ..color = const Color(0xFF8B5CF6)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final path = Path();
    final maxValue = data.map((d) => d.value).reduce((a, b) => a > b ? a : b);
    final minValue = data.map((d) => d.value).reduce((a, b) => a < b ? a : b);

    for (int i = 0; i < data.length; i++) {
      final x = (i / (data.length - 1)) * size.width;
      final y =
          size.height -
          ((data[i].value - minValue) / (maxValue - minValue)) * size.height;

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);

    // 绘制数据点
    final pointPaint = Paint()
      ..color = const Color(0xFF8B5CF6)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < data.length; i++) {
      final x = (i / (data.length - 1)) * size.width;
      final y =
          size.height -
          ((data[i].value - minValue) / (maxValue - minValue)) * size.height;
      canvas.drawCircle(Offset(x, y), 3, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
