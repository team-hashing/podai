import 'dart:ui';

import 'package:flutter/material.dart';
import 'dart:math';
class SineWavePainter extends CustomPainter {
  final double phase;
  final double amplitude;

  SineWavePainter({required this.phase, required this.amplitude});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final path1 = Path();
    final path2 = Path();
    final path3 = Path();

    for (double x = 0; x < size.width; x++) {
      double progress = x / size.width;
      double wavelength1 = lerpDouble(0.05, 0.02, progress)!;
      double wavelength2 = lerpDouble(0.06, 0.02, progress)!;
      double wavelength3 = lerpDouble(0.07, 0.02, progress)!;
      double amplitude1 = lerpDouble(amplitude, 30, progress)!;
      double amplitude2 = lerpDouble(amplitude, 30, progress)!;
      double amplitude3 = lerpDouble(amplitude, 30, progress)!;

      final y1 = size.height / 2 + amplitude1 * sin((x * wavelength1) + phase);
      final y2 = size.height / 2 + amplitude2 * sin((x * wavelength2) + phase + pi / 3);
      final y3 = size.height / 2 + amplitude3 * sin((x * wavelength3) + phase + 2 * pi / 3);

      if (x == 0) {
        path1.moveTo(x, y1);
        path2.moveTo(x, y2);
        path3.moveTo(x, y3);
      } else {
        path1.lineTo(x, y1);
        path2.lineTo(x, y2);
        path3.lineTo(x, y3);
      }
    }

    canvas.drawPath(path1, paint);
    canvas.drawPath(path2, paint);
    canvas.drawPath(path3, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}

class SineWaveWidget extends StatefulWidget {
  final double amplitude;

  SineWaveWidget({required this.amplitude});

  @override
  _SineWaveWidgetState createState() => _SineWaveWidgetState();
}
class _SineWaveWidgetState extends State<SineWaveWidget> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void stopAnimation() {
    _controller.stop();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          painter: SineWavePainter(
            phase: _controller.value * 2 * pi,
            amplitude: widget.amplitude,
          ),
          child: Container(),
        );
      },
    );
  }
}