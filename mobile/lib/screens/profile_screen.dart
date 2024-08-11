import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:podai/services/auth_service.dart';
import 'package:podai/widgets/widgets.dart';

class ProfileScreen extends StatelessWidget {
  final AuthService _authService = AuthService();

  @override
  Widget build(BuildContext context) {
    final user = _authService.getCurrentUser();

    return Scaffold(
      body: Stack(
        children: [
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color.fromARGB(255, 36, 23, 56), // Purple
                  Color(0xFF000000), // Black
                ],
              ),
            ),
          ),
          Column(
            children: [
              AppBar(
                backgroundColor: Colors.transparent,
                title: const Text(
                  'Profile',
                  style: TextStyle(color: Colors.white),
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.settings, color: Colors.white),
                    onPressed: () {
                      Navigator.pushNamed(context, '/settings');
                    },
                  ),
                ],
              ),
              Expanded(
                child: ListView(
                  children: [
                    ProfileHeader(
                      username: user?.displayName ?? 'Unknown',
                      profileImageUrl: user?.photoURL ??
                          "https://st3.depositphotos.com/9998432/13335/v/450/depositphotos_133351928-stock-illustration-default-placeholder-man-and-woman.jpg",
                    ),
                    const PodcastSection(
                      key: Key('my podcasts'),
                      displayType: DisplayType.cards,
                      title: 'My podcasts',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
