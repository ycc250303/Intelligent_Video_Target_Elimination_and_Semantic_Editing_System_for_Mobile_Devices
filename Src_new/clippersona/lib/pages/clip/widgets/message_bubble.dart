import 'dart:io';
import 'package:flutter/material.dart';
import '../../../models/message.dart';
import '../../../config/app_locales.dart';
import 'image_viewer.dart';
import 'video_player_screen.dart';

class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.sender == MessageSender.user;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 16.0),
      child: Row(
        mainAxisAlignment: isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.blue,
              child: Icon(Icons.smart_toy, size: 20, color: Colors.white),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.7,
              ),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser
                    ? Colors.blue.withValues(alpha: 0.8)
                    : Colors.grey[200]?.withValues(alpha: 0.8),
                borderRadius: BorderRadius.circular(18).copyWith(
                  bottomLeft: isUser
                      ? const Radius.circular(18)
                      : const Radius.circular(4),
                  bottomRight: isUser
                      ? const Radius.circular(4)
                      : const Radius.circular(18),
                ),
              ),
              child: _buildMessageContent(context),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: Colors.green,
              child: Icon(Icons.person, size: 20, color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMessageContent(BuildContext context) {
    switch (message.type) {
      case MessageType.text:
        return Text(
          message.content,
          style: TextStyle(
            color: message.sender == MessageSender.user
                ? Colors.white
                : Colors.black87,
            fontSize: 16,
          ),
        );
      case MessageType.multimodal:
        return _buildMultimodalContent(context);
      case MessageType.image:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (message.content.isNotEmpty)
              Text(
                message.content,
                style: TextStyle(
                  color: message.sender == MessageSender.user
                      ? Colors.white
                      : Colors.black87,
                  fontSize: 16,
                ),
              ),
            if (message.content.isNotEmpty) const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _onImageTap(context),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: _buildImageWidget(),
              ),
            ),
          ],
        );
      case MessageType.video:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (message.content.isNotEmpty)
              Text(
                message.content,
                style: TextStyle(
                  color: message.sender == MessageSender.user
                      ? Colors.white
                      : Colors.black87,
                  fontSize: 16,
                ),
              ),
            if (message.content.isNotEmpty) const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _onVideoTap(context),
              child: _buildVideoWidget(),
            ),
          ],
        );
      case MessageType.voice:
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.mic,
              color: message.sender == MessageSender.user
                  ? Colors.white
                  : Colors.black87,
            ),
            const SizedBox(width: 8),
            Text(
              message.content.isNotEmpty ? message.content : '语音消息',
              style: TextStyle(
                color: message.sender == MessageSender.user
                    ? Colors.white
                    : Colors.black87,
                fontSize: 16,
              ),
            ),
            if (message.voiceDuration != null) ...[
              const SizedBox(width: 8),
              Text(
                _formatDuration(message.voiceDuration!),
                style: TextStyle(
                  color: message.sender == MessageSender.user
                      ? Colors.white70
                      : Colors.black54,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        );
    }
  }

  String _formatDuration(Duration duration) {
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    final minutes = twoDigits(duration.inMinutes.remainder(60));
    final seconds = twoDigits(duration.inSeconds.remainder(60));
    return '$minutes:$seconds';
  }

  // 构建图片显示组件
  Widget _buildImageWidget() {
    if (message.mediaPath == null || message.mediaPath!.isEmpty) {
      return _buildPlaceholder(Icons.image, appLocales.imageLoadFailed);
    }

    try {
      // 判断是否为本地文件路径
      if (message.mediaPath!.startsWith('/') ||
          message.mediaPath!.contains(':\\')) {
        // 本地文件系统路径
        return Image.file(
          File(message.mediaPath!),
          width: 200,
          height: 150,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildPlaceholder(
              Icons.broken_image,
              appLocales.imageLoadFailed,
            );
          },
        );
      } else {
        // Assets 资源路径
        return Image.asset(
          message.mediaPath!,
          width: 200,
          height: 150,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) {
            return _buildPlaceholder(
              Icons.broken_image,
              appLocales.imageLoadFailed,
            );
          },
        );
      }
    } catch (e) {
      return _buildPlaceholder(Icons.error, appLocales.error);
    }
  }

  // 构建视频显示组件
  Widget _buildVideoWidget() {
    return Container(
      width: 200,
      height: 150,
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 显示视频缩略图（第一帧）
            if (message.thumbnailPath != null &&
                message.thumbnailPath!.isNotEmpty)
              Image.file(
                File(message.thumbnailPath!),
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return _buildVideoPlaceholder();
                },
              )
            else
              _buildVideoPlaceholder(),
            // 半透明遮罩
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.1),
                    Colors.black.withValues(alpha: 0.3),
                  ],
                ),
              ),
            ),
            // 播放按钮
            Center(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.6),
                  shape: BoxShape.circle,
                ),
                padding: const EdgeInsets.all(12),
                child: const Icon(
                  Icons.play_arrow,
                  color: Colors.white,
                  size: 40,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建视频占位符（无缩略图时显示）
  Widget _buildVideoPlaceholder() {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Colors.grey[800]!, Colors.grey[900]!],
        ),
      ),
      child: const Center(
        child: Icon(Icons.videocam, size: 40, color: Colors.white54),
      ),
    );
  }

  // 构建占位符组件
  Widget _buildPlaceholder(IconData icon, String text) {
    return Container(
      width: 200,
      height: 150,
      decoration: BoxDecoration(
        color: Colors.grey[300],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 50, color: Colors.grey[600]),
          const SizedBox(height: 8),
          Text(text, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        ],
      ),
    );
  }

  // 处理图片点击事件
  void _onImageTap(BuildContext context) {
    if (message.mediaPath == null || message.mediaPath!.isEmpty) {
      return;
    }

    final isLocalFile =
        message.mediaPath!.startsWith('/') ||
        message.mediaPath!.contains(':\\');

    ImageViewer.show(context, message.mediaPath!, isLocalFile);
  }

  // 处理视频点击事件
  void _onVideoTap(BuildContext context) {
    if (message.mediaPath == null || message.mediaPath!.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('视频路径无效')));
      return;
    }

    // 直接调用 Navigator，绕过静态方法缓存问题
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => VideoPlayerScreen(videoPath: message.mediaPath!),
      ),
    );
  }

  // 构建多模态内容（文本 + 多个媒体）
  Widget _buildMultimodalContent(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 显示文本（如果有）
        if (message.content.isNotEmpty) ...[
          Text(
            message.content,
            style: TextStyle(
              color: message.sender == MessageSender.user
                  ? Colors.white
                  : Colors.black87,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
        ],
        // 显示所有媒体文件
        if (message.mediaList != null && message.mediaList!.isNotEmpty)
          ...message.mediaList!.map((media) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: GestureDetector(
                onTap: () {
                  if (media.type == 'image') {
                    final isLocalFile =
                        media.path.startsWith('/') ||
                        media.path.contains(':\\');
                    ImageViewer.show(context, media.path, isLocalFile);
                  } else {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            VideoPlayerScreen(videoPath: media.path),
                      ),
                    );
                  }
                },
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: media.type == 'image'
                      ? _buildMultimodalImage(media)
                      : _buildMultimodalVideo(media),
                ),
              ),
            );
          }).toList(),
      ],
    );
  }

  // 构建多模态消息中的图片
  Widget _buildMultimodalImage(MessageMedia media) {
    return Image.file(
      File(media.path),
      width: 200,
      height: 150,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) {
        return _buildPlaceholder(
          Icons.broken_image,
          appLocales.imageLoadFailed,
        );
      },
    );
  }

  // 构建多模态消息中的视频
  Widget _buildMultimodalVideo(MessageMedia media) {
    return Container(
      width: 200,
      height: 150,
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 显示视频缩略图
            if (media.thumbnailPath != null && media.thumbnailPath!.isNotEmpty)
              Image.file(
                File(media.thumbnailPath!),
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return _buildVideoPlaceholder();
                },
              )
            else
              _buildVideoPlaceholder(),
            // 半透明遮罩
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.1),
                    Colors.black.withValues(alpha: 0.3),
                  ],
                ),
              ),
            ),
            // 播放按钮
            Center(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.6),
                  shape: BoxShape.circle,
                ),
                padding: const EdgeInsets.all(12),
                child: const Icon(
                  Icons.play_arrow,
                  color: Colors.white,
                  size: 40,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
