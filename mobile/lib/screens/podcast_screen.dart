import 'package:flutter/material.dart';
import 'package:podai/services/audio_service.dart';
import 'package:podai/widgets/audio_player.dart';

import 'package:podai/widgets/widgets.dart';
import 'package:podai/services/services.dart';

class PodcastScreen extends StatefulWidget {

  const PodcastScreen({super.key});

  @override
  State<PodcastScreen> createState() => _PodcastScreenState();
}

class _PodcastScreenState extends State<PodcastScreen> {
  AudioService audioService = AudioService.instance;


  @override
  void initState() {
    super.initState();
  }


  @override
  Widget build(BuildContext context) {
    return Container(

      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF4A148C), // Purple
            Color(0xFF000000), // Black
          ],
        ),
      ),
      child: Scaffold(
        appBar: AppBar(
        title: const Text('Now playing', style: TextStyle(color: Colors.white)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () {
            Navigator.pop(context);
          },
        ),
        backgroundColor: Colors.transparent,
        ),
        backgroundColor: Colors.transparent,
        body: const AudioPlayerWidget(),
      ),
    );
  }

}

