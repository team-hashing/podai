import 'package:flutter/material.dart';
import 'package:podai/screens/login_screen.dart';

import '../services/services.dart'; 

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: [
          ListTile(
            title: const Text('Account Preferences'),
            onTap: () {
              // Navigate to account preferences page or show dialog
            },
          ),
          ListTile(
            title: const Text('App Preferences'),
            onTap: () {
              // Navigate to app preferences page or show dialog
            },
          ),
          ListTile(
            title: const Text('Logout'),
            onTap: () async {
              await AuthService().signOut();
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
          ),
        ],
      ),
    );
  }
}