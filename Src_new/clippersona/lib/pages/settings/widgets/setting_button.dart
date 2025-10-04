import 'package:flutter/material.dart';

class SettingButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;

  const SettingButton({super.key, required this.text, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      child: Text(
        text,
        style: TextStyle(
          color: Colors.blue.shade300,
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}
