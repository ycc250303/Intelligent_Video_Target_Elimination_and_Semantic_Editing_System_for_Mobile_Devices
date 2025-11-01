import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../pages/persona/models/persona_models.dart';
import '../models/operation_record.dart';

/// 风格卡持久化存储服务
class StyleCardStorageService {
  static const String _storageKey = 'style_cards_storage';

  /// 保存所有风格卡到本地
  static Future<bool> saveStyleCards(List<StyleCard> styleCards) async {
    try {
      debugPrint('💾 保存风格卡到SharedPreferences:');
      debugPrint('   风格卡数量: ${styleCards.length}');

      final prefs = await SharedPreferences.getInstance();

      // 将风格卡列表转换为JSON
      final List<Map<String, dynamic>> jsonList = styleCards.map((card) {
        debugPrint('   - ${card.title}: ${card.operations.length} 个操作');
        return {
          'id': card.id,
          'title': card.title,
          'imageUrl': card.imageUrl,
          'description': card.description,
          'operations': card.operations.map((op) => op.toJson()).toList(),
          'status': card.status.toString(),
          'downloads': card.downloads,
          'comments': card.comments,
          'isShared': card.isShared,
          'isShareEnabled': card.isShareEnabled,
        };
      }).toList();

      final String jsonString = jsonEncode(jsonList);
      final result = await prefs.setString(_storageKey, jsonString);
      debugPrint('✅ SharedPreferences保存${result ? "成功" : "失败"}');
      return result;
    } catch (e) {
      debugPrint('❌ 保存风格卡失败: $e');
      return false;
    }
  }

  /// 从本地加载所有风格卡
  static Future<List<StyleCard>> loadStyleCards() async {
    try {
      debugPrint('📂 从SharedPreferences加载风格卡...');
      final prefs = await SharedPreferences.getInstance();
      final String? jsonString = prefs.getString(_storageKey);

      if (jsonString == null || jsonString.isEmpty) {
        debugPrint('   没有找到保存的风格卡');
        return [];
      }

      final List<dynamic> jsonList = jsonDecode(jsonString);
      debugPrint('   找到 ${jsonList.length} 个风格卡');

      final styleCards = jsonList.map((json) {
        // 解析status
        final statusString = json['status'] as String;
        StyleCardStatus status;
        if (statusString.contains('local')) {
          status = StyleCardStatus.local;
        } else if (statusString.contains('shared')) {
          status = StyleCardStatus.shared;
        } else {
          status = StyleCardStatus.downloadable;
        }

        // 解析operations
        final operations =
            (json['operations'] as List<dynamic>?)
                ?.map(
                  (e) => OperationRecord.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            [];

        debugPrint('   - ${json['title']}: ${operations.length} 个操作');

        return StyleCard(
          id: json['id'],
          title: json['title'],
          imageUrl: json['imageUrl'] ?? '',
          description: json['description'] ?? '',
          operations: operations,
          status: status,
          downloads: json['downloads'] ?? 0,
          comments: json['comments'] ?? 0,
          isShared: json['isShared'] ?? false,
          isShareEnabled: json['isShareEnabled'] ?? false,
        );
      }).toList();

      debugPrint('✅ 风格卡加载完成');
      return styleCards;
    } catch (e) {
      debugPrint('❌ 加载风格卡失败: $e');
      return [];
    }
  }

  /// 清空所有风格卡
  static Future<bool> clearStyleCards() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return await prefs.remove(_storageKey);
    } catch (e) {
      debugPrint('清空风格卡失败: $e');
      return false;
    }
  }
}
