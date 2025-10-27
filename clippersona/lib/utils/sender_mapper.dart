import '../models/message.dart';

/// 消息发送者映射工具类
///
/// 用于前后端MessageSender类型的相互转换
class SenderMapper {
  /// 后端Sender → 前端Sender
  ///
  /// 将后端的字符串值转换为前端的枚举类型
  /// - 'assistant' 和 'system' 都映射为 MessageSender.bot
  /// - 'user' 映射为 MessageSender.user
  static MessageSender fromBackend(String sender) {
    if (sender == 'assistant' || sender == 'system') {
      return MessageSender.bot;
    }
    return MessageSender.user;
  }

  /// 前端Sender → 后端Sender
  ///
  /// 将前端的枚举类型转换为后端的字符串值
  /// - MessageSender.user → 'user'
  /// - MessageSender.bot → 'assistant'
  static String toBackend(MessageSender sender) {
    return sender == MessageSender.user ? 'user' : 'assistant';
  }
}
