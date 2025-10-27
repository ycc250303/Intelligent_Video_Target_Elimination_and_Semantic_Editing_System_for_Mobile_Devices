import 'dart:io';
import 'package:flutter/material.dart';
import 'package:photo_view/photo_view.dart';
import '../../../config/app_locales.dart';

/// 图片全屏查看器
class ImageViewer extends StatelessWidget {
  final String imagePath;
  final bool isLocalFile;

  const ImageViewer({
    super.key,
    required this.imagePath,
    this.isLocalFile = true,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black.withValues(alpha: 0.5),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          appLocales.viewImage,
          style: const TextStyle(color: Colors.white),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.download, color: Colors.white),
            onPressed: () {
              // TODO: 实现图片保存功能
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(appLocales.saveFeatureInDev)),
              );
            },
          ),
        ],
      ),
      body: Center(
        child: PhotoView(
          imageProvider: isLocalFile
              ? FileImage(File(imagePath))
              : AssetImage(imagePath) as ImageProvider,
          minScale: PhotoViewComputedScale.contained,
          maxScale: PhotoViewComputedScale.covered * 3,
          backgroundDecoration: const BoxDecoration(color: Colors.black),
          loadingBuilder: (context, event) => Center(
            child: CircularProgressIndicator(
              value: event == null
                  ? 0
                  : event.cumulativeBytesLoaded /
                        (event.expectedTotalBytes ?? 1),
            ),
          ),
          errorBuilder: (context, error, stackTrace) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.broken_image,
                    size: 100,
                    color: Colors.white54,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    appLocales.imageLoadFailed,
                    style: const TextStyle(color: Colors.white54, fontSize: 16),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  /// 显示图片查看器
  static void show(BuildContext context, String imagePath, bool isLocalFile) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            ImageViewer(imagePath: imagePath, isLocalFile: isLocalFile),
      ),
    );
  }
}
