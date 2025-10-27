import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../../config/app_locales.dart';
import '../widgets/setting_dropdown.dart';
import '../widgets/setting_switch.dart';

class EditingPreferencesSection extends StatelessWidget {
  final String exportFormat;
  final String frameRate;
  final bool communityUpdates;
  final ValueChanged<String> onExportFormatChanged;
  final ValueChanged<String> onFrameRateChanged;
  final ValueChanged<bool> onCommunityUpdatesChanged;

  const EditingPreferencesSection({
    super.key,
    required this.exportFormat,
    required this.frameRate,
    required this.communityUpdates,
    required this.onExportFormatChanged,
    required this.onFrameRateChanged,
    required this.onCommunityUpdatesChanged,
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
            right: 12,
            top: 12,
            child: Opacity(
              opacity: 0.2,
              child: Image.asset(
                'assets/settingPage/bubble.png',
                width: 250,
                height: 250,
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
                  appLocales.editingPreferences,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                SettingDropdown(
                  title: appLocales.exportFormat,
                  value: exportFormat,
                  options: const ['720p', '1080p', '4K'],
                  onChanged: onExportFormatChanged,
                ),
                SettingDropdown(
                  title: appLocales.frameRate,
                  value: frameRate,
                  options: const ['24fps', '30fps', '60fps'],
                  onChanged: onFrameRateChanged,
                ),
                const SizedBox(height: 16),
                SettingSwitch(
                  title: appLocales.communityUpdates,
                  value: communityUpdates,
                  onChanged: onCommunityUpdatesChanged,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
