import 'locale_manager.dart';

/// 应用文本配置类 - 中英文对照
class AppLocales {
  final LocaleManager _localeManager = LocaleManager();

  // ==================== 通用 ====================
  String get appName => _getText('CoEdit', 'CoEdit');
  String get confirm => _getText('确定', 'Confirm');
  String get cancel => _getText('取消', 'Cancel');
  String get delete => _getText('删除', 'Delete');
  String get save => _getText('保存', 'Save');
  String get edit => _getText('编辑', 'Edit');
  String get back => _getText('返回', 'Back');
  String get loading => _getText('加载中...', 'Loading...');
  String get error => _getText('错误', 'Error');
  String get success => _getText('成功', 'Success');

  // ==================== 聊天页面 ====================
  String get chatPageTitle => _getText('智能视频编辑', 'Video Editing');
  String get newProject => _getText('新建项目', 'New Project');
  String get inputHint => _getText('输入消息...', 'Type a message...');
  String get send => _getText('发送', 'Send');
  String get pickImage => _getText('选择图片', 'Pick Image');
  String get pickVideo => _getText('选择视频', 'Pick Video');
  String get viewImage => _getText('查看图片', 'View Image');
  String get playVideo => _getText('播放视频', 'Play Video');
  String get downloadImage => _getText('下载图片', 'Download');
  String get saveFeatureInDev =>
      _getText('保存功能开发中...', 'Save feature coming soon...');
  String get imageLoadFailed => _getText('图片加载失败', 'Image load failed');
  String get videoLoadFailed => _getText('视频加载失败', 'Video load failed');
  String get loadingVideo => _getText('加载视频中...', 'Loading video...');
  String get retry => _getText('重试', 'Retry');

  // ==================== 历史记录 ====================
  String get historyTitle => _getText('历史项目', 'History');
  String get noHistory => _getText('暂无历史记录', 'No history yet');
  String get clearAllHistory => _getText('清空所有历史', 'Clear All');
  String get confirmClearHistory => _getText('确认清空', 'Confirm Clear');
  String get clearHistoryWarning => _getText(
    '确定要清空所有历史对话吗？此操作不可恢复。',
    'Are you sure to clear all chat history? This cannot be undone.',
  );
  String get historyCleared => _getText('历史记录已清空', 'History cleared');

  // ==================== 媒体预览 ====================
  String get mediaPreview => _getText('已选择', 'Selected');
  String get clearAll => _getText('全部删除', 'Clear All');
  String get removeMedia => _getText('移除', 'Remove');

  // ==================== 设置页面 ====================
  String get settingsTitle => _getText('设置', 'Settings');
  String get accountSettings => _getText('账户设置', 'Account');
  String get languageSettings => _getText('语言设置', 'Language');
  String get currentLanguage => _getText('当前语言', 'Current Language');
  String get switchLanguage => _getText('切换语言', 'Switch Language');
  String get chinese => _getText('中文', 'Chinese');
  String get english => _getText('英文', 'English');
  String get aboutApp => _getText('关于应用', 'About');
  String get version => _getText('版本', 'Version');
  String get otherSettings => _getText('其他', 'Other');
  String get darkMode => _getText('深色模式', 'Dark Mode');
  String get help => _getText('帮助', 'Help');
  String get feedback => _getText('反馈', 'Feedback');
  String get testConnection => _getText('测试连接', 'Test Connection');
  String get testing => _getText('测试中...', 'Testing...');
  String get connectionSuccess => _getText('连接成功！', 'Connection Successful!');
  String get connectionFailed => _getText('连接失败', 'Connection Failed');
  String get connectionErrorDetail => _getText(
    '无法连接到服务器，请检查：\n1. 电脑IP地址是否正确\n2. 后端服务是否启动\n3. 手机和电脑是否在同一网络',
    'Cannot connect to server. Please check:\n1. Computer IP address is correct\n2. Backend service is running\n3. Phone and computer are on same network',
  );
  String get deleteAllSessions => _getText('清空后端会话', 'Clear Backend Sessions');
  String get deletingAllSessions => _getText('清空中...', 'Clearing...');
  String get deleteAllSessionsConfirm => _getText(
    '确认清空后端所有会话？\n\n这将删除服务器上的所有会话数据，但不影响本地历史记录。',
    'Confirm to clear all backend sessions?\n\nThis will delete all session data on the server, but will not affect local history.',
  );
  String get deleteAllSessionsSuccess =>
      _getText('后端会话已清空', 'Backend sessions cleared');
  String get deleteAllSessionsFailed => _getText('清空失败', 'Clear failed');
  String get copy => _getText('复制', 'Copy');
  String get copied => _getText('已复制', 'Copied');
  String get saveToGallery => _getText('保存到相册', 'Save to Gallery');
  String get savedToGallery => _getText('已保存到相册', 'Saved to Gallery');
  String get saveFailed => _getText('保存失败', 'Save Failed');
  String get noMediaToSave => _getText('没有媒体可保存', 'No media to save');
  String get editingPreferences => _getText('剪辑偏好', 'Editing Preferences');
  String get exportFormat => _getText('导出格式', 'Export Format');
  String get frameRate => _getText('帧率', 'Frame Rate');
  String get communityUpdates => _getText('社区动态', 'Community Updates');
  String get account => _getText('账户', 'Account');
  String get username => _getText('用户名', 'Username');
  String get editUsername => _getText('编辑用户名', 'Edit Username');
  String get avatarUpdated => _getText('头像更新成功', 'Avatar updated');
  String get avatarSaveFailed => _getText('头像保存失败', 'Avatar save failed');
  String get avatarSelectFailed =>
      _getText('头像选择失败', 'Avatar selection failed');

  // ==================== 底部导航栏 ====================
  String get navPersona => _getText('Persona', 'Persona');
  String get navClip => _getText('剪辑', 'Clip');
  String get navCommunity => _getText('社区', 'Community');
  String get navSettings => _getText('设置', 'Settings');

  // ==================== Persona页面 ====================
  String get personaTitle => _getText('智能助手', 'AI Assistant');
  String get personaDescription =>
      _getText('您的专属视频编辑助手', 'Your personal video editing assistant');

  // ==================== 社区页面 ====================
  String get communityTitle => _getText('社区', 'Community');
  String get share => _getText('分享', 'Share');
  String get like => _getText('点赞', 'Like');
  String get comment => _getText('评论', 'Comment');

  // ==================== 视频控制 ====================
  String get play => _getText('播放', 'Play');
  String get pause => _getText('暂停', 'Pause');
  String get forward10s => _getText('快进10秒', 'Forward 10s');
  String get backward10s => _getText('后退10秒', 'Backward 10s');

  // ==================== 错误提示 ====================
  String get networkError => _getText('网络错误', 'Network Error');
  String get fileNotFound => _getText('文件不存在', 'File Not Found');
  String get permissionDenied => _getText('权限被拒绝', 'Permission Denied');

  /// 根据当前语言获取文本
  String _getText(String zh, String en) {
    return _localeManager.isChinese ? zh : en;
  }

  // 单例
  static final AppLocales _instance = AppLocales._internal();
  factory AppLocales() => _instance;
  AppLocales._internal();
}

/// 全局访问点
final appLocales = AppLocales();
