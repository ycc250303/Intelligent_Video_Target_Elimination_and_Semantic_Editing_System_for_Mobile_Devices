import 'package:flutter/material.dart';
import '../../../models/project_models.dart';

class DeleteDialog extends StatelessWidget {
  final Project project;
  final VoidCallback onCancel;
  final VoidCallback onConfirm;

  const DeleteDialog({
    super.key,
    required this.project,
    required this.onCancel,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1F2937),
      title: const Text('删除对话', style: TextStyle(color: Colors.white)),
      content: Text(
        '确定要删除"${project.title}"吗？此操作无法撤销。',
        style: const TextStyle(color: Colors.grey),
      ),
      actions: [
        TextButton(
          onPressed: onCancel,
          child: const Text('取消', style: TextStyle(color: Colors.grey)),
        ),
        TextButton(
          onPressed: onConfirm,
          child: const Text('删除', style: TextStyle(color: Colors.red)),
        ),
      ],
    );
  }
}
