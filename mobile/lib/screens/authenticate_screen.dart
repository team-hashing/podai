import 'dart:math';

import 'package:flutter/material.dart';
import 'package:podai/graphics/AI_waveform_painter.dart';
import 'package:podai/graphics/custom_page_route.dart';
import 'package:podai/screens/screens.dart';

class AuthenticateScreen extends StatefulWidget {
  const AuthenticateScreen({super.key});

  @override
  _AuthenticateScreenState createState() => _AuthenticateScreenState();
}

class _AuthenticateScreenState extends State<AuthenticateScreen>
    with SingleTickerProviderStateMixin {
  double _amplitude = 50.0;

  void _onButtonPressed() {
    //something can be done to reflect on the animation that a button was pressed
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
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
        child: Column(
          children: <Widget>[
            const Expanded(
              child: Center(
                child: Text(
                  'podAI',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 60, // Increased font size
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            Expanded(
              flex: 2,
              child: Center(
                child: SineWaveWidget(amplitude: _amplitude),
              ),
            ),
            Expanded(
              flex: 1,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: <Widget>[
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        foregroundColor: Colors.white,
                        backgroundColor: const Color.fromARGB(255, 56, 39, 97),
                        padding: const EdgeInsets.symmetric(vertical: 20),
                        textStyle: const TextStyle(fontSize: 18),
                        minimumSize: const Size.fromHeight(50),
                      ),
                      child: const Text('Login'),
                      onPressed: () {
                        Navigator.of(context)
                            .push(CustomPageRoute(page: const LoginScreen()));
                      },
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        foregroundColor: Colors.white,
                        backgroundColor: const Color.fromARGB(255, 56, 39, 97),
                        padding: const EdgeInsets.symmetric(vertical: 20),
                        textStyle: const TextStyle(fontSize: 18),
                        minimumSize: const Size.fromHeight(50),
                      ),
                      child: const Text('Register'),
                      onPressed: () {
                        _onButtonPressed();
                        Navigator.of(context).push(
                            CustomPageRoute(page: const RegisterScreen()));
                      },
                    ),
                    const SizedBox(height: 40), // Add some space at the bottom
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
