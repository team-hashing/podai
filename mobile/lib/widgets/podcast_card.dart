import 'dart:convert';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:podai/services/services.dart';
import 'package:podai/models/models.dart';

import 'package:http/http.dart' as http;
import 'package:podai/constants.dart';

class PodcastCard extends StatelessWidget {
  final Podcast podcast;
  final double height;
  final double width;

  const PodcastCard({
    super.key,
    required this.podcast,
    this.height = 200,
    this.width = 150,
  });

  // final apiUrl = 'http://34.170.203.169:8000';

  @override
  Widget build(BuildContext context) {
    AudioService audioService = AudioService.instance;
    Future<String> coverUrl =
        StoreService.instance.accessFile(podcast.uuid, Types.cover);

    return StreamBuilder<Podcast?>(
        stream: audioService.currentPodcastStream,
        builder: (context, snapshot) {
          bool isCurrentPodcastPlaying =
              podcast.uuid == audioService.getCurrentPodcast()?.uuid;

          return FutureBuilder<String>(
            future: coverUrl,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return _buildPlaceholder();
              } else if (snapshot.hasError) {
                return _buildErrorPlaceholder();
              } else if (snapshot.hasData) {
                return _buildContent(
                    context, snapshot.data!, isCurrentPodcastPlaying);
              } else {
                return _buildPlaceholder();
              }
            },
          );
        });
  }

  Widget _buildPlaceholder() {
    return Card(
      elevation: 4,
      color: Color(0xFF2E1760), // Darker gray for dark mode
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              height: 100,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15),
                color: Colors.grey[700], // Darker gray for dark mode
              ),
            ),
            const SizedBox(height: 8),
            Container(
              width: 100,
              height: 20,
              color: Colors.grey[700], // Darker gray for dark mode
            ),
            const SizedBox(height: 4),
            Container(
              width: 60,
              height: 20,
              color: Colors.grey[700], // Darker gray for dark mode
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorPlaceholder() {
    final url = '$apiUrl/api/get_podcast_info';
    final userId = AuthService().getCurrentUser()!.uid;
    final podcastId = podcast.uuid;

    return FutureBuilder<String>(
      future: _fetchPodcastStatus(url, podcastId, userId),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return ClipRRect(
            borderRadius:
                BorderRadius.circular(15.0), // Adjust the radius as needed
            child: Container(
              width: width,
              height: height,
              color: Colors.grey[300], // Loading color
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
          );
        } else if (snapshot.hasError || snapshot.data == 'error') {
          return ClipRRect(
            borderRadius:
                BorderRadius.circular(15.0), // Adjust the radius as needed
            child: Container(
              width: width,
              height: height,
              color: Colors.red[900], // Darker red for dark mode
              child: const Center(
                child: Icon(Icons.error, color: Colors.white),
              ),
            ),
          );
        } else {
          // Handle other statuses if needed
          return ClipRRect(
            borderRadius:
                BorderRadius.circular(15.0), // Adjust the radius as needed
            child: Container(
              width: width,
              height: height,
              color: Colors.green[300], // Success color
              child: const Center(
                child: Icon(Icons.check, color: Colors.white),
              ),
            ),
          );
        }
      },
    );
  }

  Future<String> _fetchPodcastStatus(
      String url, String podcastId, String userId) async {
    final response = await http.post(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'podcast_id': podcastId, 'user_id': userId}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['status'];
    } else {
      throw Exception('Failed to load podcast status');
    }
  }

  Widget _buildContent(
      BuildContext context, String coverUrl, bool isCurrentPodcastPlaying) {
    AudioService audioService = AudioService.instance;
    double progressStop = 0;

    return StreamBuilder<SeekBarData>(
        stream: audioService.seekBarDataStream,
        builder: (context, snapshot) {
          if (isCurrentPodcastPlaying && snapshot.hasData) {
            final seekBarData = snapshot.data;
            progressStop = (seekBarData!.position.inMilliseconds /
                seekBarData.duration.inMilliseconds);
          }

          return Container(
            margin: const EdgeInsets.all(8.0),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(15),
              gradient: LinearGradient(
                colors: [
                  const Color.fromARGB(255, 138, 84, 161)
                      .withOpacity(isCurrentPodcastPlaying ? 1 : 0),
                  const Color.fromARGB(255, 30, 30, 30)
                      .withOpacity(isCurrentPodcastPlaying ? 1 : 0),
                ],
                stops: [progressStop, progressStop],
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.5), // Darker shadow color
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(2, 2), // Shadow position
                ),
              ],
            ),
            child: Card(
              color: isCurrentPodcastPlaying
                  ? Color.fromARGB(255, 69, 29, 97)
                  : Color.fromARGB(
                      255, 42, 19, 60), // Darker gray for dark mode
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              elevation: 10,
              child: InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () {
                  audioService.setCurrentPodcast(podcast).then((_) {
                    audioService.loadPodcastProgress(podcast);
                  });
                  Navigator.pushNamed(context, '/podcast');
                },
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      ConstrainedBox(
                        constraints: const BoxConstraints(
                          maxHeight: 100,
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8.0),
                          child: CachedNetworkImage(
                            imageUrl: coverUrl,
                            width: 100,
                            height: 100,
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(
                              color:
                                  Colors.grey[700], // Darker gray for dark mode
                              width: 100,
                              height: 100,
                            ),
                            errorWidget: (context, url, error) =>
                                Icon(Icons.error),
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        podcast.name,
                        style: const TextStyle(
                            fontWeight: FontWeight.bold, color: Colors.white),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        podcast.creator,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: isCurrentPodcastPlaying
                            ? const TextStyle(
                                color: Color.fromARGB(255, 200, 200, 200))
                            : const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        });
  }
}
