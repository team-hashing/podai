import 'dart:math';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:podai/models/models.dart';
import 'package:podai/widgets/widgets.dart';

import 'package:podai/services/services.dart';

class BottomPlayer extends StatelessWidget {
  final AudioService audioService = AudioService.instance;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Podcast?>(
      stream: audioService.currentPodcastStream, // Assuming you have a stream for currentPodcast
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const SizedBox.shrink(); // Show nothing while waiting for data
        }

        final currentPodcast = snapshot.data;

        if (currentPodcast == null) {
          return const SizedBox.shrink(); // Show nothing if there's no podcast
        }

        return  GestureDetector(
                onVerticalDragUpdate: (details) {
                  // Check if the drag is downwards, details.delta.dy is positive when dragging down
                  if (details.delta.dy < 10) {
                    // Execute the desired action on sliding up
                    Navigator.pushNamed(context, '/podcast');
                  } else if (details.delta.dy > 10) {
                    // Execute the desired action on sliding down
                    audioService.pause();
                    audioService.stopPositionListener();
                  }
                },
                child: SizedBox(
      height: max(MediaQuery.of(context).size.height * 0.1, 100),
      width: MediaQuery.of(context).size.width * 0.95,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(8.0),
          color: Color.fromARGB(255, 69, 29, 97),
        ),
        child: InkWell(
                  onTap: () {
                    Navigator.of(context).pushNamed('/podcast');
                  },
                  child: Row(
                    children: [
                      Center(
                        child: Container(
                          margin: const EdgeInsets.symmetric(horizontal: 10),
                          height: MediaQuery.of(context).size.width * 0.15,
                          width: MediaQuery.of(context).size.width * 0.15,
                          child: FutureBuilder<String>(
                            future: StoreService.instance.accessFile(
                                audioService.getCurrentPodcast()!.uuid,
                                Types.cover),
                            builder: (context, snapshot) {
                              if (snapshot.hasData) {
                                String coverUrl = snapshot.data!;
                                return ClipRRect(
                                  borderRadius: BorderRadius.circular(8.0),
                                  child: CachedNetworkImage(
                                    imageUrl: coverUrl,
                                    width: MediaQuery.of(context).size.width *
                                        0.15,
                                    height: MediaQuery.of(context).size.width *
                                        0.15,
                                    fit: BoxFit.cover,
                                    placeholder: (context, url) => Container(
                                      color: Colors.grey[700],
                                      width: MediaQuery.of(context).size.width *
                                          0.15,
                                      height:
                                          MediaQuery.of(context).size.width *
                                              0.15,
                                    ),
                                    errorWidget: (context, url, error) =>
                                        const Icon(Icons.error),
                                  ),
                                );
                              } else {
                                return Container(
                                  height: 60,
                                  width: 60,
                                  decoration: BoxDecoration(
                                    borderRadius: BorderRadius.circular(8.0),
                                    color: Colors.grey[700],
                                  ),
                                );
                              }
                            },
                          ),
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            margin: const EdgeInsets.only(top: 15, left: 10),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                SizedBox(
                                  width:
                                      MediaQuery.of(context).size.width * 0.35,
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        snapshot.data!.name,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: 1,
                                      ),
                                      Text(
                                        snapshot.data!.creator,
                                        style: const TextStyle(
                                          color: Colors.white70,
                                          fontSize: 14,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        maxLines: 1,
                                      ),
                                    ],
                                  ),
                                ),
                                  Row(
                                    children: [
                                      IconButton(
                                        icon: const Icon(Icons.replay_10,
                                            color: Colors.white),
                                        onPressed: () => audioService
                                            .seekBackward10Seconds(),
                                      ),
                                      StreamBuilder<bool>(
                                        stream: audioService.isPlayingStream,
                                        builder: (context, snapshot) {
                                          bool isPlaying =
                                              snapshot.data ?? false;
                                          return IconButton(
                                            icon: Icon(
                                              isPlaying
                                                  ? Icons.pause
                                                  : Icons.play_arrow,
                                              color: Colors.white,
                                            ),
                                            onPressed: () {
                                              if (isPlaying) {
                                                audioService.pause();
                                              } else {
                                                audioService.play();
                                              }
                                            },
                                          );
                                        },
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.forward_10,
                                            color: Colors.white),
                                        onPressed: () =>
                                            audioService.seekForward10Seconds(),
                                      ),
                                    ],
                                  ),
                              ],
                            ),
                          ),
                          SizedBox(
                            width: MediaQuery.of(context).size.width * 0.7,
                            child: StreamBuilder<SeekBarData>(
                              stream: audioService.seekBarDataStream,
                              builder: (context, snapshot) {
                                if (snapshot.hasData) {
                                  final seekBarData = snapshot.data!;
                                  return SeekBar(
                                    duration: seekBarData.duration,
                                    position: seekBarData.position,
                                    onChangeEnd: (newPosition) {
                                      audioService.seek(newPosition);
                                    },
                                    showTime: false,
                                  );
                                } else {
                                  return const CircularProgressIndicator();
                                }
                              },
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
              ),
        ),
        ),

      );
      },
    );
  }
}
