import 'dart:convert';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:podai/services/services.dart';
import 'package:podai/widgets/player_buttons.dart';
import 'package:podai/widgets/seekbar.dart';
import 'package:http/http.dart' as http;
import 'package:podai/constants.dart';

class AudioPlayerWidget extends StatefulWidget {
  const AudioPlayerWidget({super.key});

  @override
  _AudioPlayerWidgetState createState() => _AudioPlayerWidgetState();
}

class _AudioPlayerWidgetState extends State<AudioPlayerWidget> {
  bool isFavorite = false; // State variable for favorite status
  // final String apiUrl = 'http://34.170.203.169:8000';
  final String userId = AuthService().getCurrentUser()!.uid;
  final String podcastId = AudioService.instance.getCurrentPodcast()!.uuid;

  Future<void> toggleFavorite() async {
    setState(() {
      isFavorite = !isFavorite; // Immediately toggle favorite state
      if (isFavorite) {
        AudioService.instance.getCurrentPodcast()!.likedBy.add(userId);
      } else {
        AudioService.instance.getCurrentPodcast()!.likedBy.remove(userId);
      }
    });

    final url =
        isFavorite ? '$apiUrl/api/like_podcast' : '$apiUrl/api/unlike_podcast';

    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'podcast_id': podcastId,
      }),
    );

    if (response.statusCode != 200) {
      // Revert the favorite state if the API call fails
      setState(() {
        isFavorite = !isFavorite;
      });
      // Handle error
      print('Failed to update favorite status: ${response.statusCode}');
    }
  }

  @override
  Widget build(BuildContext context) {
    double screenWidth = MediaQuery.of(context).size.width;
    AudioService audioService = AudioService.instance;
    final podcast = audioService.getCurrentPodcast();
    // get list from podcast.likedBy or empty list if null
    final podcastLikedBy = podcast?.likedBy ?? [];
    // Check if podcast.likedBy contains the current user's ID
    if (podcast != null &&
        podcastLikedBy.contains(AuthService().getCurrentUser()!.uid)) {
      isFavorite = true; // Step 2: Set favorite state to true
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 40.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: FutureBuilder<String>(
              future: StoreService.instance.accessFile(
                  audioService.getCurrentPodcast()!.uuid, Types.cover),
              builder: (context, snapshot) {
                if (snapshot.hasData) {
                  String coverUrl = snapshot.data!;
                  return Container(
                    height: screenWidth * 0.9,
                    width: screenWidth * 0.9,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20.0),
                      image: DecorationImage(
                        image: CachedNetworkImageProvider(coverUrl),
                        fit: BoxFit.cover,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black26,
                          blurRadius: 10.0,
                          offset: Offset(0, 10),
                        ),
                      ],
                    ),
                    child: CachedNetworkImage(
                      imageUrl: coverUrl,
                      placeholder: (context, url) => Container(
                        color: Colors.grey[300],
                        width: screenWidth * 0.9,
                        height: screenWidth * 0.9,
                      ),
                      errorWidget: (context, url, error) => Icon(Icons.error),
                    ),
                  );
                } else {
                  return Container(
                    width: screenWidth * 0.8,
                    height: screenWidth * 0.8,
                    color: Colors.grey[300],
                  );
                }
              },
            ),
          ),
          const Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      audioService.getCurrentPodcast()!.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                      overflow: TextOverflow.ellipsis, // Prevents text overflow
                    ),
                    const SizedBox(height: 10.0),
                    Text(
                      audioService.getCurrentPodcast()!.creator,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: Icon(isFavorite ? Icons.favorite : Icons.favorite_border),
                color: Colors.red, // Optional: Customize color
                onPressed: () {
                  toggleFavorite();
                  /*
									setState(() {
										isFavorite = !isFavorite; // Step 3: Toggle favorite state
									});
					*/
                },
              ),
              IconButton(
                icon: const Icon(Icons.share),
                color: Colors.white, // Optional: Customize color
                onPressed: () {
                  setState(() {
                    //TODO: create an URL for each podcast on frontend
                    //Share.share(audioService.getCurrentPodcast()?.url ?? '');
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 20.0),
          StreamBuilder<SeekBarData>(
              stream: audioService.seekBarDataStream,
              builder: (context, snapshot) {
                final positionData = snapshot.data;
                return SeekBar(
                  position: positionData?.position ?? Duration.zero,
                  duration: positionData?.duration ?? Duration.zero,
                  onChangeEnd: audioService.seek,
                );
              }),
          const SizedBox(height: 20.0),
          PlayerButtons(),
          const SizedBox(height: 20.0),
        ],
      ),
    );
  }
}
