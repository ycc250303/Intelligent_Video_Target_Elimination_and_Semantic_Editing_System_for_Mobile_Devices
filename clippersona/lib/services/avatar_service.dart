import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:permission_handler/permission_handler.dart';

class AvatarService {
  static const String _avatarFileName = 'user_avatar.jpg';

  /// 检查并请求权限
  static Future<bool> _checkPermissions() async {
    // 检查相机权限
    var cameraStatus = await Permission.camera.status;
    if (!cameraStatus.isGranted) {
      cameraStatus = await Permission.camera.request();
    }

    // 检查存储权限
    var storageStatus = await Permission.storage.status;
    if (!storageStatus.isGranted) {
      storageStatus = await Permission.storage.request();
    }

    // 检查照片权限 (Android 13+)
    var photosStatus = await Permission.photos.status;
    if (!photosStatus.isGranted) {
      photosStatus = await Permission.photos.request();
    }

    return cameraStatus.isGranted &&
        (storageStatus.isGranted || photosStatus.isGranted);
  }

  /// 选择头像图片
  static Future<File?> pickAvatarImage() async {
    // 检查权限
    if (!await _checkPermissions()) {
      throw Exception('权限被拒绝，无法访问相册');
    }

    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 200,
      maxHeight: 200,
      imageQuality: 85,
    );

    if (image != null) {
      return File(image.path);
    }
    return null;
  }

  /// 拍照获取头像
  static Future<File?> takeAvatarPhoto() async {
    // 检查权限
    if (!await _checkPermissions()) {
      throw Exception('权限被拒绝，无法使用相机');
    }

    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 200,
      maxHeight: 200,
      imageQuality: 85,
    );

    if (image != null) {
      return File(image.path);
    }
    return null;
  }

  /// 保存头像到本地
  static Future<String?> saveAvatar(File imageFile) async {
    try {
      final Directory appDir = await getApplicationDocumentsDirectory();
      final String avatarPath = path.join(appDir.path, _avatarFileName);

      await imageFile.copy(avatarPath);
      return avatarPath;
    } catch (e) {
      debugPrint('保存头像失败: $e');
      return null;
    }
  }

  /// 获取保存的头像路径
  static Future<String?> getAvatarPath() async {
    try {
      final Directory appDir = await getApplicationDocumentsDirectory();
      final String avatarPath = path.join(appDir.path, _avatarFileName);
      final File avatarFile = File(avatarPath);

      if (await avatarFile.exists()) {
        return avatarPath;
      }
    } catch (e) {
      debugPrint('获取头像路径失败: $e');
    }
    return null;
  }

  /// 删除头像
  static Future<bool> deleteAvatar() async {
    try {
      final Directory appDir = await getApplicationDocumentsDirectory();
      final String avatarPath = path.join(appDir.path, _avatarFileName);
      final File avatarFile = File(avatarPath);

      if (await avatarFile.exists()) {
        await avatarFile.delete();
        return true;
      }
    } catch (e) {
      debugPrint('删除头像失败: $e');
    }
    return false;
  }

  /// 显示头像选择对话框
  static Future<File?> showAvatarPickerDialog(BuildContext context) async {
    return await showModalBottomSheet<File>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A1A),
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              margin: EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Text(
              '选择头像',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildPickerOption(
                  context,
                  icon: Icons.photo_library,
                  label: '相册',
                  onTap: () async {
                    Navigator.pop(context);
                    final file = await pickAvatarImage();
                    if (file != null && context.mounted) {
                      Navigator.pop(context, file);
                    }
                  },
                ),
                _buildPickerOption(
                  context,
                  icon: Icons.camera_alt,
                  label: '拍照',
                  onTap: () async {
                    Navigator.pop(context);
                    final file = await takeAvatarPhoto();
                    if (file != null && context.mounted) {
                      Navigator.pop(context, file);
                    }
                  },
                ),
              ],
            ),
            SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  static Widget _buildPickerOption(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 100,
        height: 100,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Colors.white.withValues(alpha: 0.2),
            width: 1,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 32),
            SizedBox(height: 8),
            Text(label, style: TextStyle(color: Colors.white, fontSize: 14)),
          ],
        ),
      ),
    );
  }
}
