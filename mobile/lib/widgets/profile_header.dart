import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';



class ProfileHeader extends StatelessWidget {
  final String username;
  final String profileImageUrl;

  const ProfileHeader({
    super.key,
    required this.username,
    required this.profileImageUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: CircleAvatar(
            radius: 50,
            backgroundImage: CachedNetworkImageProvider(profileImageUrl),
          ),
        ),
        Text(
          username,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}