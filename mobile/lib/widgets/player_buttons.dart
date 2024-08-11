import 'package:flutter/material.dart';
import 'package:podai/services/audio_service.dart';
import 'dart:async';

class PlayerButtons extends StatefulWidget {
  const PlayerButtons({Key? key}) : super(key: key);

  @override
  _PlayerButtonsState createState() => _PlayerButtonsState();
}

class _PlayerButtonsState extends State<PlayerButtons> {
  AudioService audioService = AudioService.instance;
  double _selectedSpeed = 1.0;
  double _timerDuration = 0;
  Timer? _timer;
  ValueNotifier<Duration> _remainingTime = ValueNotifier(Duration.zero);

  void _startTimer() {
    _timer?.cancel();
    if (_timerDuration > 0) {
      _remainingTime.value = Duration(minutes: _timerDuration.toInt());
      _timer = Timer.periodic(Duration(seconds: 1), (timer) {
        if (_remainingTime.value.inSeconds > 0) {
          _remainingTime.value -= Duration(seconds: 1);
        } else {
          _timer?.cancel();
          audioService.pause();
        }
      });
    }
  }

  void _cancelTimer() {
    _timer?.cancel();
    _remainingTime.value = Duration.zero;
  }

  @override
  void dispose() {
    _timer?.cancel();
    _remainingTime.dispose();
    super.dispose();
  }

  void _showTimerPopup() {
    showDialog(
      barrierColor: Color.fromARGB(70, 33, 8, 37),
      context: context,
      builder: (BuildContext context) {
        double tempTimerDuration = _timerDuration;
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: Color.fromARGB(255, 53, 9, 66),
                title: Text('Set Timer (${tempTimerDuration.toStringAsFixed(0)} minutes)', style: TextStyle(color: Colors.white)),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Slider(
                    value: tempTimerDuration,
                    min: 0,
                    max: 120,
                    divisions: 120,
                    label: tempTimerDuration.round().toString(),
                    onChanged: (double value) {
                      setState(() {
                        tempTimerDuration = value;
                      });
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  child: const Text('Cancel',
                    style: TextStyle(color: Colors.white)),
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                ),
                TextButton(
                  child: const Text('Set',
                    style: TextStyle(color: Colors.white)),
                  onPressed: () {
                    setState(() {
                      _timerDuration = tempTimerDuration;
                      _startTimer();
                    });
                    Navigator.of(context).pop();
                  },
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Timer button
            Column(
              children: [
                IconButton(
                  icon: const Icon(Icons.timer),
                  color: Colors.white,
                  onPressed: _showTimerPopup,
                ),
                ValueListenableBuilder<Duration>(
                  valueListenable: _remainingTime,
                  builder: (context, value, child) {
                    if (value > Duration.zero) {
                      return Text(
                        '${value.inMinutes}:${(value.inSeconds % 60).toString().padLeft(2, '0')}',
                        style: TextStyle(fontSize: 12.0, color: Colors.white),
                      );
                    } else {
                      return Container();
                    }
                  },
                ),
              ],
            ),
            // Back 10 seconds button
            IconButton(
              icon: const Icon(Icons.replay_10),
              color: Colors.white,
              iconSize: 48.0,
              onPressed: () {
                audioService.seekBackward10Seconds();
              },
            ),
            // Play/Pause button
            StreamBuilder<bool>(
              stream: audioService.audioPlayer.playingStream,
              builder: (context, snapshot) {
                final isPlaying = snapshot.data ?? false;
                return IconButton(
                  icon: isPlaying
                      ? const Icon(Icons.pause_circle_filled)
                      : const Icon(Icons.play_circle_fill),
                  color: Colors.white,
                  iconSize: 48.0,
                  onPressed: () {
                    if (isPlaying) {
                      audioService.pause();
                      _cancelTimer();
                    } else {
                      audioService.play();
                    }
                  },
                );
              },
            ),
            // Forward 10 seconds button
            IconButton(
              icon: const Icon(Icons.forward_10),
              color: Colors.white,
              iconSize: 48.0,
              onPressed: () {
                audioService.seekForward10Seconds();
              },
            ),
            // Speed dropdown
            DropdownButton<double>(
              value: _selectedSpeed,
              items: [0.5, 1.0, 1.5, 2.0].map((double speed) {
                return DropdownMenuItem<double>(
                  value: speed,
                  child: Text(
                    '${speed}x',
                    style: TextStyle(color: Colors.white)
                  ),
                );
              }).toList(),
              onChanged: (double? newSpeed) {
                if (newSpeed != null) {
                  setState(() {
                    _selectedSpeed = newSpeed;
                  });
                  audioService.setSpeed(newSpeed);
                }
              },
            ),
          ],
        ),
      ],
    );
  }
}