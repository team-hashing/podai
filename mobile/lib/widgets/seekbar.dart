import 'dart:math';

import 'package:flutter/material.dart';

class SeekBar extends StatefulWidget {
  final Duration position;
  final Duration duration;
  final ValueChanged<Duration>? onChanged;
  final ValueChanged<Duration>? onChangeEnd;
  final bool showTime;

  const SeekBar(
      {super.key,
      required this.position,
      required this.duration,
      this.onChanged,
      this.onChangeEnd,
      this.showTime = true
      });

  @override
  State<SeekBar> createState() => _SeekBarState();
}

class _SeekBarState extends State<SeekBar> {
  double? _dragValue;

  String _formatDuration(Duration? duration) {
    if (duration==null) {
      return '--:--';
    }
    final minutes = duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = duration.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Row(
        children: [
          if (widget.showTime) Text(_formatDuration(widget.position),
                    style: TextStyle(color: Colors.white)),
          Expanded(
            child: SliderTheme(
              data: SliderTheme.of(context).copyWith(
                trackHeight: 4,
                thumbShape: const RoundSliderThumbShape(
                    disabledThumbRadius: 4,
                    enabledThumbRadius: 4,
                  ),
                  overlayShape: const RoundSliderOverlayShape(
                    overlayRadius: 10
                  ),
                  activeTrackColor: Colors.purple,
                  inactiveTrackColor: Colors.grey,
                  thumbColor: Colors.purple,
                  overlayColor: Colors.purple.withAlpha(32),
                  
              ),
              child: Container(
  constraints: BoxConstraints(
    maxWidth: MediaQuery.of(context).size.width, // Ensure the slider does not overflow the parent width
  ),
  child: Slider(
                min: 0.0,
                max: widget.duration.inMilliseconds.toDouble(),
                value: min(
                    _dragValue ?? widget.position.inMilliseconds.toDouble(), 
                    widget.duration.inMilliseconds.toDouble(),
                  ),
                  onChanged: (value) {
                    setState(() {
                      _dragValue = value;
                    });
                    if (widget.onChanged != null) {
                      widget.onChanged!(
                        Duration(milliseconds: value.round())
                      );
                    }
                  },
                  onChangeEnd: (value) {
                    if (widget.onChangeEnd != null) {
                      widget.onChangeEnd!(
                        Duration(milliseconds: value.round())
                      );
                    }
                    _dragValue = null;
                  },
              )
              ),
            ),
          ),
        
          if (widget.showTime) Text(_formatDuration(widget.duration),
                    style: TextStyle(color: Colors.white)),
      ],
      ),
    );
  }
}
