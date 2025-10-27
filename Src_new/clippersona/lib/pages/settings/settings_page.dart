import 'package:flutter/material.dart';
import 'sections/account_section.dart';
import 'sections/editing_preferences_section.dart';
import 'sections/other_settings_section.dart';
import 'sections/language_section.dart';
import '../../services/avatar_service.dart';
import '../../config/app_locales.dart';
import '../../config/locale_manager.dart';
import '../../config/settings_manager.dart';
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
  bool _darkMode = true;
  String _exportFormat = "1080p";
  String _frameRate = "30fps";
  final LocaleManager _localeManager = LocaleManager();
  final SettingsManager _settingsManager = SettingsManager();

  @override
  void initState() {
    super.initState();
    _loadAvatar();
    // 监听设置变化
    _settingsManager.addListener(_onSettingsChanged);
  }

  @override
  void dispose() {
    _settingsManager.removeListener(_onSettingsChanged);
    super.dispose();
  }

  void _onSettingsChanged() {
    setState(() {}); // 重新构建UI
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
        title: Text(appLocales.settingsTitle),
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
                communityUpdates: _settingsManager.communityUpdatesEnabled,
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
                  _settingsManager.setCommunityUpdates(value);
                },
              ),
              SizedBox(height: 15),

              // 语言设置部分
              LanguageSection(
                currentLocale: _localeManager.currentLocale,
                onLocaleChanged: (locale) {
                  setState(() {
                    _localeManager.setLocale(locale);
                  });
                },
              ),
              SizedBox(height: 15),

              // 其他设置部分
              OtherSettingsSection(
                darkMode: _darkMode,
                onDarkModeChanged: (value) {
                  setState(() {
                    _darkMode = value;
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
              content: Text(appLocales.avatarUpdated),
              backgroundColor: const Color(0xFF4CAF50),
            ),
          );
        } else if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(appLocales.avatarSaveFailed),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${appLocales.avatarSelectFailed}: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showEditDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(appLocales.edit),
          content: TextField(
            decoration: InputDecoration(labelText: appLocales.accountSettings),
            controller: TextEditingController(text: _userName),
            onChanged: (value) => _userName = value,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(appLocales.cancel),
            ),
            TextButton(
              onPressed: () {
                setState(() {});
                Navigator.pop(context);
              },
              child: Text(appLocales.save),
            ),
          ],
        );
      },
    );
  }
}
