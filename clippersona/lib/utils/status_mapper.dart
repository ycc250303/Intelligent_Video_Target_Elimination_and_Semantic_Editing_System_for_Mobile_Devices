/// 状态映射工具类
///
/// 用于前后端状态值的相互转换
class StatusMapper {
  /// 后端状态 → 前端状态
  ///
  /// 将后端的英文枚举值转换为前端的中文字符串
  static String fromBackend(String backendStatus) {
    const map = {
      'active': '进行中',
      'idle': '空闲',
      'processing': '处理中',
      'completed': '已完成',
      'error': '错误',
    };
    return map[backendStatus] ?? '进行中';
  }

  /// 前端状态 → 后端状态
  ///
  /// 将前端的中文字符串转换为后端的英文枚举值
  static String toBackend(String frontendStatus) {
    const map = {
      '进行中': 'active',
      '空闲': 'idle',
      '处理中': 'processing',
      '已完成': 'completed',
      '错误': 'error',
    };
    return map[frontendStatus] ?? 'active';
  }
}
