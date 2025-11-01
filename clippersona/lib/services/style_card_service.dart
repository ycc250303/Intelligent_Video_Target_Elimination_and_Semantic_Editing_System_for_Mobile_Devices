import 'package:flutter/foundation.dart';
import '../pages/persona/models/persona_models.dart';
import 'style_card_storage_service.dart';

/// 风格卡服务 - 管理风格卡的全局状态
class StyleCardService {
  // 单例模式
  static final StyleCardService _instance = StyleCardService._internal();
  factory StyleCardService() => _instance;
  StyleCardService._internal();

  // 风格卡列表（全局状态）
  // 不再初始化demo风格卡，用户可以自己创建
  static final ValueNotifier<List<StyleCard>> styleCardsNotifier =
      ValueNotifier<List<StyleCard>>([]);

  // 初始化标志
  static bool _isInitialized = false;

  /// 初始化服务（从本地加载风格卡）
  static Future<void> initialize() async {
    if (_isInitialized) return;

    debugPrint('🔄 初始化风格卡服务...');

    // 加载用户创建的风格卡
    final loadedStyleCards = await StyleCardStorageService.loadStyleCards();
    debugPrint('   从存储加载了 ${loadedStyleCards.length} 个用户风格卡');

    // 获取 Demo 风格卡（初始值中的第一个）
    final demoCards = styleCardsNotifier.value
        .where((card) => card.isDemoCard)
        .toList();
    debugPrint('   保留 ${demoCards.length} 个 Demo 风格卡');

    // 合并：Demo 卡 + 加载的用户卡
    final allCards = [...demoCards, ...loadedStyleCards];
    styleCardsNotifier.value = allCards;

    _isInitialized = true;
    debugPrint('✅ 风格卡服务初始化完成，共 ${allCards.length} 个风格卡');

    // 调试：打印每个风格卡的操作数量
    for (var card in allCards) {
      debugPrint('   - ${card.title}: ${card.operations.length} 个操作');
    }
  }

  /// 保存当前风格卡列表到本地
  static Future<void> _saveToStorage() async {
    // 只保存用户创建的风格卡，不保存Demo卡
    final userStyleCards = styleCardsNotifier.value
        .where((card) => !card.isDemoCard)
        .toList();
    debugPrint('💾 保存用户风格卡: ${userStyleCards.length} 个');
    await StyleCardStorageService.saveStyleCards(userStyleCards);
  }

  /// 获取所有风格卡
  static List<StyleCard> getAllStyleCards() {
    return styleCardsNotifier.value;
  }

  /// 获取已共享的风格卡（已共享到社区的本地风格卡）
  static List<StyleCard> getSharedStyleCards() {
    return styleCardsNotifier.value.where((card) => card.isShared).toList();
  }

  /// 获取本地风格卡
  static List<StyleCard> getLocalStyleCards() {
    return styleCardsNotifier.value
        .where((card) => card.status == StyleCardStatus.local)
        .toList();
  }

  /// 共享风格卡到社区（保持本地状态，只标记为已共享）
  static Future<void> shareStyleCard(String cardId) async {
    final cards = List<StyleCard>.from(styleCardsNotifier.value);
    final index = cards.indexWhere((card) => card.id == cardId);

    if (index != -1) {
      final oldCard = cards[index];
      // 保持本地状态，只标记为已共享
      cards[index] = StyleCard.local(
        id: oldCard.id,
        title: oldCard.title,
        imageUrl: oldCard.imageUrl,
        description: oldCard.description,
        operations: oldCard.operations,
        isSharedToCommunity: true, // 标记为已共享到社区
      );
      styleCardsNotifier.value = cards;
      await _saveToStorage(); // 保存到本地
    }
  }

  /// 取消共享风格卡（保持本地状态，取消共享标记）
  static Future<void> unshareStyleCard(String cardId) async {
    final cards = List<StyleCard>.from(styleCardsNotifier.value);
    final index = cards.indexWhere((card) => card.id == cardId);

    if (index != -1) {
      final oldCard = cards[index];
      // 保持本地状态，取消共享标记
      cards[index] = StyleCard.local(
        id: oldCard.id,
        title: oldCard.title,
        imageUrl: oldCard.imageUrl,
        description: oldCard.description,
        operations: oldCard.operations,
        isSharedToCommunity: false, // 取消共享标记
      );
      styleCardsNotifier.value = cards;
      await _saveToStorage(); // 保存到本地
    }
  }

  /// 删除风格卡
  static Future<void> deleteStyleCard(String cardId) async {
    final cards = List<StyleCard>.from(styleCardsNotifier.value);
    cards.removeWhere((card) => card.id == cardId);
    styleCardsNotifier.value = cards;
    await _saveToStorage(); // 保存到本地
  }

  /// 添加风格卡
  static Future<void> addStyleCard(StyleCard card) async {
    debugPrint('➕ 添加风格卡到服务:');
    debugPrint('   ID: ${card.id}');
    debugPrint('   标题: ${card.title}');
    debugPrint('   操作数量: ${card.operations.length}');

    final cards = List<StyleCard>.from(styleCardsNotifier.value);
    cards.add(card);
    styleCardsNotifier.value = cards;

    debugPrint('   当前总风格卡数: ${cards.length}');

    await _saveToStorage(); // 保存到本地
    debugPrint('✅ 风格卡已保存到本地存储');
  }
}
