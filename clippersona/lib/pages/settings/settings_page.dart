import 'package:flutter/material.dart';
import 'sections/account_section.dart';
import 'sections/editing_preferences_section.dart';
import 'sections/other_settings_section.dart';
import 'sections/language_section.dart';
import '../../services/avatar_service.dart';
import '../../services/user_service.dart';
import '../../services/backend_session_service.dart';
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
  String _userName = "USER_NAME";
  String? _avatarPath;

  // 设置状态
  bool _darkMode = true;
  final LocaleManager _localeManager = LocaleManager();
  final SettingsManager _settingsManager = SettingsManager();

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
    // 监听设置变化
    _settingsManager.addListener(_onSettingsChanged);
    // 监听头像变化
    AvatarService.avatarPathNotifier.addListener(_onAvatarChanged);
    // 监听昵称变化
    UserService.userNameNotifier.addListener(_onUserNameChanged);
  }

  @override
  void dispose() {
    _settingsManager.removeListener(_onSettingsChanged);
    AvatarService.avatarPathNotifier.removeListener(_onAvatarChanged);
    UserService.userNameNotifier.removeListener(_onUserNameChanged);
    super.dispose();
  }

  void _onSettingsChanged() {
    setState(() {}); // 重新构建UI
  }

  void _onAvatarChanged() {
    if (mounted) {
      setState(() {
        _avatarPath = AvatarService.avatarPathNotifier.value;
      });
    }
  }

  void _onUserNameChanged() {
    if (mounted) {
      setState(() {
        _userName = UserService.userNameNotifier.value;
      });
    }
  }

  Future<void> _loadUserInfo() async {
    // 加载头像
    final avatarPath = await AvatarService.getAvatarPath();
    // 加载昵称
    final userName = await UserService.getUserName();

    if (mounted) {
      setState(() {
        _avatarPath = avatarPath;
        _userName = userName;
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
                communityUpdates: _settingsManager.communityUpdatesEnabled,
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
                onTestConnectionPressed: _testConnection,
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
    final TextEditingController controller = TextEditingController(
      text: _userName,
    );
    String tempUserName = _userName;

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(appLocales.edit),
          content: TextField(
            decoration: InputDecoration(labelText: appLocales.accountSettings),
            controller: controller,
            onChanged: (value) => tempUserName = value,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(appLocales.cancel),
            ),
            TextButton(
              onPressed: () async {
                // 保存昵称到SharedPreferences
                final success = await UserService.saveUserName(tempUserName);
                if (success) {
                  setState(() {
                    _userName = tempUserName;
                  });
                  if (mounted) {
                    ScaffoldMessenger.of(
                      context,
                    ).showSnackBar(const SnackBar(content: Text('昵称保存成功')));
                  }
                } else {
                  if (mounted) {
                    ScaffoldMessenger.of(
                      context,
                    ).showSnackBar(const SnackBar(content: Text('昵称保存失败')));
                  }
                }
                if (mounted) {
                  Navigator.pop(context);
                }
              },
              child: Text(appLocales.save),
            ),
          ],
        );
      },
    );
  }

  /// 测试后端连接
  Future<void> _testConnection() async {
    // 显示加载对话框
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          content: Row(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(width: 20),
              Expanded(child: Text(appLocales.testing)),
            ],
          ),
        );
      },
    );

    try {
      // 尝试获取会话列表来测试连接
      final sessions = await BackendSessionService.loadAllSessions();

      // 关闭加载对话框
      if (mounted) Navigator.pop(context);

      // 显示结果
      if (mounted) {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green, size: 28),
                  const SizedBox(width: 10),
                  Expanded(child: Text(appLocales.connectionSuccess)),
                ],
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '✅ 基础连接测试通过\n\n'
                      '📡 服务器信息:\n'
                      '   API地址: ${BackendSessionService.baseUrl}\n'
                      '   会话数量: ${sessions.length}\n\n'
                      '📚 API文档地址:\n'
                      '   ${BackendSessionService.baseUrl}/docs\n\n'
                      '💡 提示:\n'
                      '   - 如果视频处理失败，请在浏览器中访问上述文档地址\n'
                      '   - 确认 /sessions/process-multimodal 接口存在',
                      style: TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(appLocales.confirm),
                ),
              ],
            );
          },
        );
      }
    } catch (e) {
      // 关闭加载对话框
      if (mounted) Navigator.pop(context);

      // 显示错误信息
      if (mounted) {
        showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: Row(
                children: [
                  Icon(Icons.error, color: Colors.red, size: 28),
                  const SizedBox(width: 10),
                  Expanded(child: Text(appLocales.connectionFailed)),
                ],
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${appLocales.connectionErrorDetail}\n\n'
                      '📡 服务器配置:\n'
                      '   ${BackendSessionService.baseUrl}\n\n'
                      '❌ 错误信息:\n'
                      '   $e\n\n'
                      '🔧 排查步骤:\n'
                      '   1. 确认后端启动: python run_server.py\n'
                      '   2. 检查IP是否正确（当前配置的IP）\n'
                      '   3. 确认手机和电脑在同一WiFi\n'
                      '   4. 访问文档: ${BackendSessionService.baseUrl}/docs',
                      style: TextStyle(fontSize: 13),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(appLocales.confirm),
                ),
              ],
            );
          },
        );
      }
    }
  }
}
