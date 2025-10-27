/// 时间格式转换工具类
///
/// 用于DateTime和ISO8601字符串的相互转换
class TimeConverter {
  /// DateTime → ISO8601字符串
  ///
  /// 将Dart的DateTime对象转换为ISO8601格式字符串
  static String toIso(DateTime dt) => dt.toIso8601String();

  /// ISO8601字符串 → DateTime
  ///
  /// 将ISO8601格式字符串解析为Dart的DateTime对象
  static DateTime fromIso(String iso) => DateTime.parse(iso);
}
