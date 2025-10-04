import 'package:flutter/material.dart';
import 'sections/account_section.dart';
import 'sections/editing_preferences_section.dart';
import 'sections/other_settings_section.dart';
import '../../services/avatar_service.dart';
import 'dart:io';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  String _userName = "ADFGJJ9";
  String? _avatarPath;

  // 设置状态
  bool _communityUpdates = true;
  bool _darkMode = true;
  String _exportFormat = "1080p";
  String _frameRate = "30fps";
  String _language = "中文";

  @override
  void initState() {
    super.initState();
    _loadAvatar();
  }

  Future<void> _loadAvatar() async {
    final avatarPath = await AvatarService.getAvatarPath();
    if (mounted) {
      setState(() {
        _avatarPath = avatarPath;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('设置'),
        centerTitle: true,
        foregroundColor: Colors.white,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.transparent,
              Colors.transparent,
              Colors.transparent,
            ],
          ),
        ),
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            children: [
              // 账户管理部分
              AccountSection(
                userName: _userName,
                onEditTap: _showEditDialog,
                avatarPath: _avatarPath,
                onAvatarTap: _handleAvatarTap,
              ),
              SizedBox(height: 15),

              // 剪辑偏好部分
              EditingPreferencesSection(
                exportFormat: _exportFormat,
                frameRate: _frameRate,
                communityUpdates: _communityUpdates,
                onExportFormatChanged: (value) {
                  setState(() {
                    _exportFormat = value;
                  });
                },
                onFrameRateChanged: (value) {
                  setState(() {
                    _frameRate = value;
                  });
                },
                onCommunityUpdatesChanged: (value) {
                  setState(() {
                    _communityUpdates = value;
                  });
                },
              ),
              SizedBox(height: 15),

              // 其他设置部分
              OtherSettingsSection(
                darkMode: _darkMode,
                language: _language,
                onDarkModeChanged: (value) {
                  setState(() {
                    _darkMode = value;
                  });
                },
                onLanguageChanged: (value) {
                  setState(() {
                    _language = value;
                  });
                },
                onHelpPressed: () {
                  // TODO: 实现帮助功能
                },
                onFeedbackPressed: () {
                  // TODO: 实现反馈功能
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _handleAvatarTap() async {
    try {
      final File? selectedImage = await AvatarService.showAvatarPickerDialog(
        context,
      );
      if (selectedImage != null && mounted) {
        final String? savedPath = await AvatarService.saveAvatar(selectedImage);
        if (savedPath != null && mounted) {
          setState(() {
            _avatarPath = savedPath;
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('头像更新成功'),
              backgroundColor: Color(0xFF4CAF50),
            ),
          );
        } else if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('头像保存失败'), backgroundColor: Colors.red),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('头像选择失败: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showEditDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('编辑用户名'),
          content: TextField(
            decoration: InputDecoration(labelText: '用户名'),
            controller: TextEditingController(text: _userName),
            onChanged: (value) => _userName = value,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('取消'),
            ),
            TextButton(
              onPressed: () {
                setState(() {});
                Navigator.pop(context);
              },
              child: Text('保存'),
            ),
          ],
        );
      },
    );
  }
}
