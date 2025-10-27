import 'dart:io';
import 'package:flutter/material.dart';
import '../../../config/app_locales.dart';
import 'image_viewer.dart';
import 'video_player_screen.dart';

/// 媒体文件信息
class MediaItem {
  final String path;
  final MediaType type;
  final String? thumbnailPath;

  MediaItem({required this.path, required this.type, this.thumbnailPath});
}

enum MediaType { image, video }

/// 媒体预览栏 - 显示已选择但未发送的媒体文件
class MediaPreviewBar extends StatelessWidget {
  final List<MediaItem> mediaItems;
  final VoidCallback onClear;
  final Function(int) onRemoveItem;

  const MediaPreviewBar({
    super.key,
    required this.mediaItems,
    required this.onClear,
    required this.onRemoveItem,
  });

  @override
  Widget build(BuildContext context) {
    if (mediaItems.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      height: 100,
      color: const Color(0xFF1A1A2E),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${appLocales.mediaPreview} ${mediaItems.length}',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              TextButton(
                onPressed: onClear,
                child: Text(
                  appLocales.clearAll,
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Expanded(
            child: Builder(
              builder: (context) => ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: mediaItems.length,
                itemBuilder: (ctx, index) {
                  return _buildMediaPreviewWithContext(
                    context,
                    mediaItems[index],
                    index,
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  // 构建单个媒体预览项（带 context）
  Widget _buildMediaPreviewWithContext(
    BuildContext context,
    MediaItem item,
    int index,
  ) {
    return Container(
      width: 90,
      height: 60,
      margin: const EdgeInsets.only(right: 8),
      child: Stack(
        children: [
          GestureDetector(
            onTap: () {
              if (item.type == MediaType.image) {
                final isLocalFile =
                    item.path.startsWith('/') || item.path.contains(':\\');
                ImageViewer.show(context, item.path, isLocalFile);
              } else {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) =>
                        VideoPlayerScreen(videoPath: item.path),
                  ),
                );
              }
            },
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Container(
                width: 90,
                height: 60,
                color: Colors.grey[800],
                child: item.type == MediaType.image
                    ? Image.file(
                        File(item.path),
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(Icons.image, color: Colors.white54);
                        },
                      )
                    : item.thumbnailPath != null
                    ? Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.file(
                            File(item.thumbnailPath!),
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return const Icon(
                                Icons.videocam,
                                color: Colors.white54,
                              );
                            },
                          ),
                          const Center(
                            child: Icon(
                              Icons.play_circle_outline,
                              color: Colors.white,
                              size: 24,
                            ),
                          ),
                        ],
                      )
                    : const Icon(Icons.videocam, color: Colors.white54),
              ),
            ),
          ),
          // 删除按钮
          Positioned(
            top: -4,
            right: -4,
            child: GestureDetector(
              onTap: () => onRemoveItem(index),
              child: Container(
                width: 20,
                height: 20,
                decoration: const BoxDecoration(
                  color: Colors.red,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.close, size: 14, color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
