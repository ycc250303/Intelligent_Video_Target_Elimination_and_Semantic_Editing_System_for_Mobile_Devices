import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import '../../services/style_card_service.dart';
import '../../services/backend_session_service.dart';
import '../persona/models/persona_models.dart';
import '../../models/operation_record.dart';

/// 创建风格卡导出页面
class CreateStyleCardExportPage extends StatefulWidget {
  final List<OperationRecord> operations; // 记录的剪辑操作（包含函数调用信息）

  const CreateStyleCardExportPage({super.key, required this.operations});

  @override
  State<CreateStyleCardExportPage> createState() =>
      _CreateStyleCardExportPageState();
}

class _CreateStyleCardExportPageState extends State<CreateStyleCardExportPage> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();
  final ImagePicker _imagePicker = ImagePicker();

  String? _imageUrl; // 上传的图片路径
  bool _isGeneratingImage = false; // 是否正在生成图片
  bool _isSaving = false; // 是否正在保存

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  /// 选择图片
  Future<void> _pickImage() async {
    try {
      final XFile? pickedFile = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (pickedFile != null) {
        setState(() {
          _imageUrl = pickedFile.path;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('选择图片失败: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  /// AI生成图片
  Future<void> _generateImage() async {
    final name = _nameController.text.trim();
    final description = _descriptionController.text.trim();

    if (name.isEmpty || description.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请先输入风格卡名称和描述'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isGeneratingImage = true;
    });

    try {
      print('🎨 开始AI生图:');
      print('   名称: $name');
      print('   描述: $description');
      print('   操作数: ${widget.operations.length}');

      // 提取操作的用户指令
      final operationTexts = widget.operations
          .map((op) => op.userInstruction)
          .toList();

      // 调用后端AI生图接口
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${BackendSessionService.baseUrl}/generate-style-card-image'),
      );

      request.fields['title'] = name;
      request.fields['description'] = description;
      request.fields['operations'] = jsonEncode(operationTexts);

      print('📤 发送生图请求到后端...');

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      print('📥 收到响应: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        final relativePath = data['image_path'] as String;
        print('✅ 生图成功，相对路径: $relativePath');

        // 下载图片到本地
        final localPath = await _downloadImageToLocal(relativePath);

        if (localPath != null) {
          print('✅ 图片已下载到本地: $localPath');

          if (mounted) {
            setState(() {
              _imageUrl = localPath;
            });

            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('AI生成图片成功！'),
                backgroundColor: Color(0xFF10B981),
              ),
            );
          }
        } else {
          throw Exception('下载图片到本地失败');
        }
      } else {
        print('❌ 生图失败: ${response.statusCode}');
        throw Exception('生成失败: ${response.body}');
      }
    } catch (e) {
      print('❌ 生图异常: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('生成图片失败: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGeneratingImage = false;
        });
      }
    }
  }

  /// 下载图片到本地
  ///
  /// [relativePath] 相对于后端data目录的路径，例如 "style_card_images/裁剪_xxx.png"
  /// 返回本地绝对路径
  Future<String?> _downloadImageToLocal(String relativePath) async {
    try {
      // 构建URL
      final imageUrl = '${BackendSessionService.baseUrl}/media/$relativePath';
      print('🌐 下载图片: $imageUrl');

      // 下载图片
      final response = await http.get(Uri.parse(imageUrl));

      if (response.statusCode != 200) {
        print('❌ 下载失败: ${response.statusCode}');
        return null;
      }

      // 获取应用文档目录
      final appDir = await getApplicationDocumentsDirectory();
      final styleCardImagesDir = Directory('${appDir.path}/style_card_images');

      // 创建目录（如果不存在）
      if (!styleCardImagesDir.existsSync()) {
        styleCardImagesDir.createSync(recursive: true);
        print('📁 创建目录: ${styleCardImagesDir.path}');
      }

      // 保存图片
      final fileName = path.basename(relativePath);
      final localFile = File('${styleCardImagesDir.path}/$fileName');
      await localFile.writeAsBytes(response.bodyBytes);

      print('💾 图片已保存到: ${localFile.path}');
      return localFile.path;
    } catch (e) {
      print('❌ 下载图片异常: $e');
      return null;
    }
  }

  /// 保存风格卡
  Future<void> _saveStyleCard() async {
    final name = _nameController.text.trim();
    final description = _descriptionController.text.trim();

    if (name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请输入风格卡名称'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    if (description.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('请输入风格卡描述'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      // 如果没有上传图片，先生成图片
      if (_imageUrl == null || _imageUrl!.isEmpty) {
        // TODO: 调用AI生图
        await _generateImage();
      }

      // 创建风格卡
      print('💾 准备保存风格卡:');
      print('   名称: $name');
      print('   描述: $description');
      print('   操作数量: ${widget.operations.length}');
      for (var i = 0; i < widget.operations.length; i++) {
        print('   操作${i + 1}: ${widget.operations[i].userInstruction}');
      }

      final newStyleCard = StyleCard.local(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        title: name,
        imageUrl: _imageUrl ?? '',
        description: description,
        operations: widget.operations, // 传递记录的操作
      );

      print('📦 风格卡创建完成: ${newStyleCard.id}');
      print('   operations字段: ${newStyleCard.operations.length} 个操作');

      // 保存到服务
      StyleCardService.addStyleCard(newStyleCard);
      print('✅ 已添加到StyleCardService');

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('风格卡创建成功！'),
            backgroundColor: Color(0xFF10B981),
          ),
        );

        // 返回到欢迎页面：返回两层（导出页面->创建风格卡页面->欢迎页面）
        // 使用'exit_to_welcome'标记来通知ClipPage退出创建模式
        Navigator.pop(context, 'exit_to_welcome');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('保存失败: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true, // 让body延伸到AppBar后面
      appBar: AppBar(
        title: const Text('导出风格卡'),
        centerTitle: true,
        foregroundColor: Colors.white,
        backgroundColor: Colors.transparent, // 透明背景
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/common/background.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 风格卡名称
                _buildSectionTitle('风格卡名称', required: true),
                const SizedBox(height: 8),
                _buildTextField(
                  controller: _nameController,
                  hintText: '请输入风格卡名称',
                  maxLength: 20,
                ),
                const SizedBox(height: 16),

                // 风格卡描述
                _buildSectionTitle('风格卡描述', required: true),
                const SizedBox(height: 8),
                _buildTextField(
                  controller: _descriptionController,
                  hintText: '请描述这个风格卡的特点和用途',
                  maxLines: 2,
                  maxLength: 100,
                ),
                const SizedBox(height: 16),

                // 记录的操作（点击查看）
                _buildOperationsButton(),
                const SizedBox(height: 16),

                // 风格卡图片
                _buildSectionTitle('风格卡图片', subtitle: '可选，留空将自动生成'),
                const SizedBox(height: 8),
                _buildImageSection(),
                const SizedBox(height: 24),

                // 保存按钮
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isSaving ? null : _saveStyleCard,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: Colors.grey,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isSaving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.white,
                              ),
                            ),
                          )
                        : const Text(
                            '保存风格卡',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
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

  /// 构建操作记录按钮（点击查看）
  Widget _buildOperationsButton() {
    return GestureDetector(
      onTap: () {
        // 显示操作记录对话框
        showDialog(
          context: context,
          builder: (context) => _buildOperationsDialog(),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1F2937),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF374151)),
        ),
        child: Row(
          children: [
            const Icon(Icons.list_alt, color: Color(0xFF8B5CF6), size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '记录的操作',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.operations.isEmpty
                        ? '暂无记录的操作'
                        : '共记录 ${widget.operations.length} 个操作',
                    style: TextStyle(color: Colors.grey[400], fontSize: 12),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey, size: 24),
          ],
        ),
      ),
    );
  }

  /// 构建操作记录对话框
  Widget _buildOperationsDialog() {
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
                  const Icon(
                    Icons.list_alt,
                    color: Color(0xFF8B5CF6),
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      '记录的操作',
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

            // 操作列表
            Expanded(
              child: widget.operations.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.inbox_outlined,
                            size: 64,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            '暂无记录的操作',
                            style: TextStyle(
                              color: Colors.grey[500],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: widget.operations.length,
                      itemBuilder: (context, index) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 28,
                                height: 28,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF8B5CF6),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: Center(
                                  child: Text(
                                    '${index + 1}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF374151),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    widget.operations[index].getDisplayText(),
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  /// 构建标题
  Widget _buildSectionTitle(
    String title, {
    bool required = false,
    String? subtitle,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (required) ...[
              const SizedBox(width: 4),
              const Text(
                '*',
                style: TextStyle(color: Colors.red, fontSize: 16),
              ),
            ],
          ],
        ),
        if (subtitle != null) ...[
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: TextStyle(color: Colors.grey[400], fontSize: 12),
          ),
        ],
      ],
    );
  }

  /// 构建文本输入框
  Widget _buildTextField({
    required TextEditingController controller,
    required String hintText,
    int maxLines = 1,
    int? maxLength,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF374151)),
      ),
      child: TextField(
        controller: controller,
        maxLines: maxLines,
        maxLength: maxLength,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(color: Colors.grey[500]),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.all(16),
          counterStyle: TextStyle(color: Colors.grey[600]),
        ),
      ),
    );
  }

  /// 构建图片上传区域
  Widget _buildImageSection() {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF374151)),
      ),
      child: Column(
        children: [
          // 图片预览区域
          if (_imageUrl != null && _imageUrl!.isNotEmpty)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(12),
              ),
              child: Image.file(
                File(_imageUrl!),
                width: double.infinity,
                height: 120,
                fit: BoxFit.cover,
              ),
            )
          else
            Container(
              width: double.infinity,
              height: 140,
              decoration: BoxDecoration(
                color: const Color(0xFF374151),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.image_outlined, size: 48, color: Colors.grey[600]),
                  const SizedBox(height: 8),
                  Text(
                    '未上传图片，将自动生成',
                    style: TextStyle(color: Colors.grey[500], fontSize: 13),
                  ),
                ],
              ),
            ),

          // 操作按钮
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _pickImage,
                    icon: const Icon(Icons.upload_file, size: 18),
                    label: const Text('上传图片', style: TextStyle(fontSize: 13)),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Color(0xFF8B5CF6)),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isGeneratingImage ? null : _generateImage,
                    icon: _isGeneratingImage
                        ? const SizedBox(
                            width: 14,
                            height: 14,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.auto_awesome, size: 18),
                    label: Text(
                      _isGeneratingImage ? '生成中...' : 'AI生成',
                      style: const TextStyle(fontSize: 13),
                    ),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF10B981),
                      side: const BorderSide(color: Color(0xFF10B981)),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
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
}
