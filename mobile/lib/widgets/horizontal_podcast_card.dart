import 'dart:convert';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:podai/models/models.dart';
import 'package:podai/services/services.dart';

class HorizontalPodcastCard extends StatelessWidget {
  final Podcast podcast;
  const HorizontalPodcastCard({super.key, required this.podcast});

  @override
  Widget build(BuildContext context) {
    AudioService audioService = AudioService.instance;
    Future<String> coverUrl =
        StoreService.instance.accessFile(podcast.uuid, Types.cover);

    return GestureDetector(
      onTap: () {
        audioService.setCurrentPodcast(podcast).then((_) {
          audioService.loadPodcastProgress(podcast);
        });
        Navigator.pushNamed(context, '/podcast'); // Alternative navigation
      },
      child: StreamBuilder<Podcast?>(
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
        },
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      margin: const EdgeInsets.all(8.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(15),
        color: Color(0xFF2E1760),
        boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.5), // Darker shadow color
                    spreadRadius: 1,
                    blurRadius: 5,
                    offset: Offset(2, 2), // Shadow position
                  ),
                ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(15),
              child: Container(
                width: 80.0,
                height: 80.0,
                color: Colors.grey[700],
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: double.infinity,
                      height: 20.0,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(height: 8.0),
                    Container(
                      width: 100.0,
                      height: 20.0,
                      color: Colors.grey[700],
                    ),
                    const SizedBox(height: 8.0),
                    Container(
                      width: double.infinity,
                      height: 10.0,
                      color: Colors.grey[700],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorPlaceholder() {
    return Container(
      margin: const EdgeInsets.all(8.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(15),
        color: Colors.grey[300],
      ),
      child: const Center(
        child: Icon(Icons.error, color: Colors.red),
      ),
    );
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
                  Color.fromARGB(255, 138, 84, 161)
                      .withOpacity(isCurrentPodcastPlaying ? 1 : 0),
                  const Color.fromARGB(255, 30, 30, 30).withOpacity(isCurrentPodcastPlaying ? 1 : 0),
                ],
              stops: [progressStop, progressStop],
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
            ),
          ),
          child: Card(
            color: isCurrentPodcastPlaying ? Color.fromARGB(255, 69, 29, 97) : Color.fromARGB(255, 42, 19, 60),
            elevation: 4,
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8.0),
                    child: CachedNetworkImage(
                      imageUrl: coverUrl,
                      width: 80,
                      height: 80,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: Colors.grey[700],
                        width: 80,
                        height: 80,
                      ),
                      errorWidget: (context, url, error) => Icon(Icons.error),
                    ),
                  ),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            podcast.name,
                            style: const TextStyle(
                                fontSize: 18.0, fontWeight: FontWeight.bold, color: Colors.white),
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            podcast.creator,
                            style: isCurrentPodcastPlaying
                            ? const TextStyle(
                                color: Color.fromARGB(255, 200, 200, 200))
                            : const TextStyle(color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                  ),
                  StreamBuilder<bool>(
                      stream: audioService.isPlayingStream,
                      builder: (context, snapshot) {
                        bool isPlaying = snapshot.data ?? false;
                        return IconButton(
                            icon: isCurrentPodcastPlaying && isPlaying
                                ? const Icon(Icons.pause_circle_filled)
                                : const Icon(Icons.play_circle_fill),
                            color: Colors.grey[400],
                            iconSize: 48.0,
                            onPressed: () {
                              isCurrentPodcastPlaying
                                  ? (audioService.audioPlayer.playing
                                      ? audioService.pause()
                                      : audioService.play())
                                  : audioService
                                      .setCurrentPodcast(podcast)
                                      .then((_) {
                                      audioService.loadPodcastProgress(podcast);
                                    });
                            });
                      }),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
