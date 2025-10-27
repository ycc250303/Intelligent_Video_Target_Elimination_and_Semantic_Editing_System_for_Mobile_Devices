import 'package:flutter/material.dart';
import '../../../config/locale_manager.dart';
import '../../../config/app_locales.dart';

/// 语言设置部分
class LanguageSection extends StatelessWidget {
  final AppLocale currentLocale;
  final Function(AppLocale) onLocaleChanged;

  const LanguageSection({
    super.key,
    required this.currentLocale,
    required this.onLocaleChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Color(0xFF1E1E2F),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.language, color: Color(0xFF7C3AED)),
                SizedBox(width: 8),
                Text(
                  appLocales.languageSettings,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            _buildLanguageTile(
              context,
              AppLocale.zh,
              '中文',
              Icons.radio_button_checked,
              Icons.radio_button_unchecked,
            ),
            Divider(color: Colors.white24),
            _buildLanguageTile(
              context,
              AppLocale.en,
              'English',
              Icons.radio_button_checked,
              Icons.radio_button_unchecked,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLanguageTile(
    BuildContext context,
    AppLocale locale,
    String label,
    IconData selectedIcon,
    IconData unselectedIcon,
  ) {
    final isSelected = currentLocale == locale;
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(
        isSelected ? selectedIcon : unselectedIcon,
        color: isSelected ? Color(0xFF7C3AED) : Colors.white54,
      ),
      title: Text(
        label,
        style: TextStyle(
          color: isSelected ? Colors.white : Colors.white70,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      onTap: () {
        onLocaleChanged(locale);
      },
    );
  }
}
