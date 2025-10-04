import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../widgets/setting_dropdown.dart';
import '../widgets/setting_switch.dart';
import '../widgets/setting_button.dart';

class OtherSettingsSection extends StatelessWidget {
  final bool darkMode;
  final String language;
  final ValueChanged<bool> onDarkModeChanged;
  final ValueChanged<String> onLanguageChanged;
  final VoidCallback onHelpPressed;
  final VoidCallback onFeedbackPressed;

  const OtherSettingsSection({
    super.key,
    required this.darkMode,
    required this.language,
    required this.onDarkModeChanged,
    required this.onLanguageChanged,
    required this.onHelpPressed,
    required this.onFeedbackPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(20)),
      child: Stack(
        children: [
          Positioned.fill(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Opacity(
                opacity: 0.6,
                child: SvgPicture.asset(
                  'assets/settingPage/edit.svg',
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ),
          Positioned(
            left: 30,
            bottom: 30,
            child: Opacity(
              opacity: 0.1,
              child: Image.asset(
                'assets/settingPage/flower.png',
                width: 80,
                height: 80,
              ),
            ),
          ),
          Positioned(
            right: 12,
            top: 12,
            child: Opacity(
              opacity: 0.1,
              child: Image.asset(
                'assets/settingPage/ball.png',
                width: 88,
                height: 88,
              ),
            ),
          ),
          // 主要内容
          Padding(
            padding: EdgeInsets.fromLTRB(20, 30, 20, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '其他',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 16),
                SettingSwitch(
                  title: '深色模式',
                  value: darkMode,
                  onChanged: onDarkModeChanged,
                ),
                SettingDropdown(
                  title: '语言',
                  value: language,
                  options: const ['中文', 'English'],
                  onChanged: onLanguageChanged,
                ),
                SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    SettingButton(text: '帮助', onPressed: onHelpPressed),
                    SettingButton(text: '反馈', onPressed: onFeedbackPressed),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
