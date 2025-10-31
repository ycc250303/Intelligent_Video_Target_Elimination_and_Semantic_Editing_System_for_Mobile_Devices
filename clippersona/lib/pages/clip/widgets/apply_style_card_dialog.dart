import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../persona/models/persona_models.dart';
import '../../../services/style_card_service.dart';

/// 应用风格卡对话框
class ApplyStyleCardDialog extends StatefulWidget {
  const ApplyStyleCardDialog({super.key});

  @override
  State<ApplyStyleCardDialog> createState() => _ApplyStyleCardDialogState();
}

class _ApplyStyleCardDialogState extends State<ApplyStyleCardDialog> {
  StyleCard? _selectedStyleCard;
  String? _selectedVideoPath;
  bool _isLoadingVideo = false;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 700),
        decoration: BoxDecoration(
          color: const Color(0xFF1F2937),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFF374151), width: 1),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 标题栏
            _buildHeader(),

            // 内容区
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildStyleCardSelector(),
                    const SizedBox(height: 20),
                    _buildVideoSelector(),
                    const SizedBox(height: 20),
                    _buildOperationsPreview(),
                  ],
                ),
              ),
            ),

            // 底部按钮
            _buildFooter(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
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
          const Icon(Icons.auto_awesome, color: Color(0xFF8B5CF6), size: 24),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              '调用风格卡',
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
    );
  }

  Widget _buildStyleCardSelector() {
    final styleCards = StyleCardService.getLocalStyleCards();

    // 调试日志
    print('📋 加载风格卡列表:');
    print('   总数: ${styleCards.length}');
    for (var i = 0; i < styleCards.length; i++) {
      print(
        '   风格卡${i + 1}: ${styleCards[i].title}, 操作数: ${styleCards[i].operations.length}',
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '选择风格卡',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),

        if (styleCards.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF374151),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Center(
              child: Text(
                '暂无风格卡，请先创建风格卡',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
            ),
          )
        else
          Container(
            height: 120,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: styleCards.length,
              itemBuilder: (context, index) {
                final card = styleCards[index];
                final isSelected = _selectedStyleCard?.id == card.id;

                return GestureDetector(
                  onTap: () {
                    print('✅ 选择风格卡: ${card.title}');
                    print('   操作数: ${card.operations.length}');
                    for (var i = 0; i < card.operations.length; i++) {
                      final op = card.operations[i];
                      print('   操作${i + 1}: ${op.userInstruction}');
                      print(
                        '      函数: ${op.functionCalls.map((f) => f.functionName).join(", ")}',
                      );
                    }
                    setState(() {
                      _selectedStyleCard = card;
                    });
                  },
                  child: Container(
                    width: 100,
                    margin: const EdgeInsets.only(right: 12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF374151),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected
                            ? const Color(0xFF8B5CF6)
                            : Colors.transparent,
                        width: 2,
                      ),
                    ),
                    child: Column(
                      children: [
                        Expanded(
                          child: ClipRRect(
                            borderRadius: const BorderRadius.only(
                              topLeft: Radius.circular(8),
                              topRight: Radius.circular(8),
                            ),
                            child: card.imageUrl.isEmpty
                                ? Image.asset(
                                    'assets/communityPage/persona.png',
                                    fit: BoxFit.cover,
                                    width: double.infinity,
                                  )
                                : (card.imageUrl.startsWith('assets/')
                                      ? Image.asset(
                                          card.imageUrl,
                                          fit: BoxFit.cover,
                                          width: double.infinity,
                                        )
                                      : Image.file(
                                          File(card.imageUrl),
                                          fit: BoxFit.cover,
                                          width: double.infinity,
                                          errorBuilder:
                                              (context, error, stackTrace) {
                                                return Image.asset(
                                                  'assets/communityPage/persona.png',
                                                  fit: BoxFit.cover,
                                                  width: double.infinity,
                                                );
                                              },
                                        )),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.all(8),
                          child: Text(
                            card.title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _buildVideoSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '选择视频',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),

        GestureDetector(
          onTap: _isLoadingVideo ? null : _pickVideo,
          child: Container(
            height: 100,
            decoration: BoxDecoration(
              color: const Color(0xFF374151),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _selectedVideoPath != null
                    ? const Color(0xFF10B981)
                    : Colors.transparent,
                width: 2,
              ),
            ),
            child: _isLoadingVideo
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF8B5CF6)),
                  )
                : _selectedVideoPath == null
                ? Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.video_file,
                        color: Colors.grey,
                        size: 40,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '点击选择视频',
                        style: TextStyle(color: Colors.grey[400], fontSize: 14),
                      ),
                    ],
                  )
                : Row(
                    children: [
                      const Padding(
                        padding: EdgeInsets.all(16),
                        child: Icon(
                          Icons.check_circle,
                          color: Color(0xFF10B981),
                          size: 40,
                        ),
                      ),
                      Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              '已选择视频',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _selectedVideoPath!.split('/').last,
                              style: TextStyle(
                                color: Colors.grey[400],
                                fontSize: 12,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.grey),
                        onPressed: () {
                          setState(() {
                            _selectedVideoPath = null;
                          });
                        },
                      ),
                    ],
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildOperationsPreview() {
    if (_selectedStyleCard == null) {
      return const SizedBox.shrink();
    }

    print('🔍 显示操作预览:');
    print('   风格卡: ${_selectedStyleCard!.title}');
    print('   操作数: ${_selectedStyleCard!.operations.length}');
    print('   isEmpty: ${_selectedStyleCard!.operations.isEmpty}');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '将执行的操作',
          style: TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),

        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF374151),
            borderRadius: BorderRadius.circular(8),
          ),
          child: _selectedStyleCard!.operations.isEmpty
              ? Text(
                  _selectedStyleCard!.isDemoCard
                      ? '🎬 Demo风格卡，将直接返回预设效果'
                      : '该风格卡暂无操作记录',
                  style: TextStyle(
                    color: _selectedStyleCard!.isDemoCard
                        ? const Color(0xFF10B981) // 绿色表示可用
                        : Colors.grey,
                    fontSize: 14,
                  ),
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '共 ${_selectedStyleCard!.operations.length} 个操作',
                      style: TextStyle(color: Colors.grey[400], fontSize: 12),
                    ),
                    const SizedBox(height: 8),
                    ...(_selectedStyleCard!.operations.take(3).map((op) {
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.play_arrow,
                              color: Color(0xFF8B5CF6),
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                op.userInstruction,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 13,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    })),
                    if (_selectedStyleCard!.operations.length > 3)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          '...还有 ${_selectedStyleCard!.operations.length - 3} 个操作',
                          style: TextStyle(
                            color: Colors.grey[400],
                            fontSize: 12,
                          ),
                        ),
                      ),
                  ],
                ),
        ),
      ],
    );
  }

  Widget _buildFooter() {
    final canApply =
        _selectedStyleCard != null &&
        _selectedVideoPath != null &&
        // Demo风格卡不需要检查operations，因为它们在后端直接返回预设视频
        (_selectedStyleCard!.isDemoCard ||
            _selectedStyleCard!.operations.isNotEmpty);

    return Container(
      padding: const EdgeInsets.all(20),
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
            child: OutlinedButton(
              onPressed: () => Navigator.pop(context),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                side: const BorderSide(color: Color(0xFF374151)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                '取消',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton(
              onPressed: canApply ? _applyStyleCard : null,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                backgroundColor: const Color(0xFF8B5CF6),
                disabledBackgroundColor: const Color(0xFF374151),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: const Text(
                '应用',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _pickVideo() async {
    setState(() {
      _isLoadingVideo = true;
    });

    try {
      print('📂 打开视频选择器...');

      // 方案1: 先尝试直接使用 FilePicker（Android 11+ 不需要权限）
      FilePickerResult? result;

      try {
        result = await FilePicker.platform.pickFiles(
          type: FileType.video,
          allowMultiple: false,
        );
      } catch (e) {
        print('⚠️ FilePicker 失败，尝试请求权限: $e');

        // 方案2: 如果失败（可能是旧版Android），请求存储权限后重试
        if (Platform.isAndroid) {
          final status = await Permission.storage.request();

          if (status.isGranted) {
            print('✅ 存储权限已授予，重试选择视频');
            result = await FilePicker.platform.pickFiles(
              type: FileType.video,
              allowMultiple: false,
            );
          } else if (status.isPermanentlyDenied) {
            throw Exception('需要存储权限，请在设置中授权');
          } else {
            throw Exception('需要存储权限才能选择视频');
          }
        } else {
          rethrow;
        }
      }

      if (result != null) {
        if (result.files.isNotEmpty && result.files.single.path != null) {
          final selectedPath = result.files.single.path!;
          print('✅ 视频已选择: $selectedPath');
          setState(() {
            _selectedVideoPath = selectedPath;
          });
        } else {
          print('❌ 未选择有效文件');
        }
      } else {
        print('❌ 用户取消选择');
      }
    } catch (e) {
      print('❌ 选择视频失败: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('选择视频失败: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } finally {
      setState(() {
        _isLoadingVideo = false;
      });
    }
  }

  void _applyStyleCard() {
    // 返回选中的风格卡和视频路径
    Navigator.pop(context, {
      'styleCard': _selectedStyleCard,
      'videoPath': _selectedVideoPath,
    });
  }
}
