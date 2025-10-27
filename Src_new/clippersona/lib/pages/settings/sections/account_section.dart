import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../../config/app_locales.dart';
import 'dart:io';

class AccountSection extends StatelessWidget {
  final String userName;
  final VoidCallback onEditTap;
  final String? avatarPath;
  final VoidCallback onAvatarTap;

  const AccountSection({
    super.key,
    required this.userName,
    required this.onEditTap,
    this.avatarPath,
    required this.onAvatarTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 215,
      decoration: BoxDecoration(borderRadius: BorderRadius.circular(20)),
      child: Stack(
        children: [
          Positioned.fill(
            child: ClipRRect(
              child: SvgPicture.asset(
                'assets/settingPage/account_background.svg',
                fit: BoxFit.cover,
              ),
            ),
          ),
          // 主要内容布局
          Padding(
            padding: EdgeInsets.fromLTRB(20, 40, 20, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  appLocales.accountSettings,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.black,
                  ),
                ),
                SizedBox(height: 24),
                Row(
                  children: [
                    GestureDetector(
                      onTap: onAvatarTap,
                      child: Stack(
                        children: [
                          CircleAvatar(
                            radius: 25,
                            backgroundColor: Colors.white,
                            backgroundImage: avatarPath != null
                                ? FileImage(File(avatarPath!))
                                : AssetImage('assets/settingPage/flower.png'),
                          ),
                          Positioned(
                            right: 0,
                            bottom: 0,
                            child: Container(
                              width: 16,
                              height: 16,
                              decoration: BoxDecoration(
                                color: Color(0xFF4CAF50),
                                shape: BoxShape.circle,
                                border: Border.all(
                                  color: Colors.white,
                                  width: 2,
                                ),
                              ),
                              child: Icon(
                                Icons.camera_alt,
                                size: 8,
                                color: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(width: 16),
                    Text(
                      userName,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                      ),
                    ),
                    SizedBox(width: 8),
                    GestureDetector(
                      onTap: onEditTap,
                      child: Icon(Icons.edit, color: Colors.white, size: 22),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Wallet 装饰
          Positioned(
            right: 40,
            top: 72,
            child: SizedBox(
              width: 64,
              height: 64,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SvgPicture.asset(
                    'assets/settingPage/wallet.svg',
                    width: 64,
                    height: 64,
                  ),
                  Image.asset(
                    'assets/settingPage/shadow.png',
                    width: 64,
                    height: 64,
                    fit: BoxFit.contain,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            left: 12,
            top: 12,
            child: SvgPicture.asset(
              'assets/settingPage/account_decoration.svg',
              width: 56,
              height: 56,
            ),
          ),
        ],
      ),
    );
  }
}
