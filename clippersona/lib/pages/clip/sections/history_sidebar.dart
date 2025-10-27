import 'package:flutter/material.dart';
import '../../../models/project_models.dart';
import '../../../config/app_locales.dart';

class HistorySidebar extends StatelessWidget {
  final List<Project> historyProjects;
  final String? currentProjectId;
  final VoidCallback onClose;
  final Function(Project) onProjectTap;
  final Function(Project) onProjectDelete;
  final VoidCallback onDeleteAll; // 新增：删除所有历史
  final String Function(DateTime) formatDateTime;

  const HistorySidebar({
    super.key,
    required this.historyProjects,
    required this.currentProjectId,
    required this.onClose,
    required this.onProjectTap,
    required this.onProjectDelete,
    required this.onDeleteAll,
    required this.formatDateTime,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1F2937),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 10,
            offset: const Offset(2, 0),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 侧边栏头部
          Container(
            padding: const EdgeInsets.all(16),
            decoration: const BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Color(0xFF374151), width: 1),
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Text(
                      appLocales.historyTitle,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white),
                      onPressed: onClose,
                      tooltip: appLocales.back,
                    ),
                  ],
                ),
                // 一键删除所有按钮
                if (historyProjects.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: onDeleteAll,
                      icon: const Icon(Icons.delete_sweep, size: 18),
                      label: Text(appLocales.clearAllHistory),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red[700],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 10),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
          // 历史对话列表
          Expanded(
            child: historyProjects.isEmpty
                ? Center(
                    child: Text(
                      appLocales.noHistory,
                      style: const TextStyle(color: Colors.grey, fontSize: 16),
                    ),
                  )
                : ListView.builder(
                    itemCount: historyProjects.length,
                    itemBuilder: (context, index) {
                      final project = historyProjects[index];
                      return _buildProjectItem(context, project);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildProjectItem(BuildContext context, Project project) {
    final isCurrentProject = project.id == currentProjectId;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isCurrentProject ? const Color(0xFF374151) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        border: isCurrentProject
            ? Border.all(color: Colors.green.withValues(alpha: 0.3), width: 1)
            : null,
      ),
      child: ListTile(
        leading: Text(project.icon, style: const TextStyle(fontSize: 24)),
        title: Text(
          project.title,
          style: const TextStyle(color: Colors.white, fontSize: 16),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          formatDateTime(project.updatedAt),
          style: const TextStyle(color: Colors.grey, fontSize: 12),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (isCurrentProject)
              const Icon(Icons.check_circle, color: Colors.green, size: 20),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(
                Icons.delete_outline,
                color: Colors.red,
                size: 20,
              ),
              onPressed: () => onProjectDelete(project),
              tooltip: appLocales.delete,
            ),
          ],
        ),
        onTap: () => onProjectTap(project),
      ),
    );
  }
}
