import 'package:flutter/material.dart';
import 'package:podai/screens/authenticate_screen.dart';
import 'package:podai/screens/screens.dart';
import 'package:podai/widgets/widgets.dart';
import 'package:firebase_auth/firebase_auth.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.black, // Set the background color to black
      ),
      
      home: StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.active) {
            User? user = snapshot.data;
            if (user == null) {
              return AuthenticateScreen();
            }
            return NavBar(pages: [HomeScreen(), CreateScreen(), ProfileScreen()]);
          }
          return const CircularProgressIndicator(); // Loading state
        },
      ),
      
      routes: {
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/podcast': (context) => const PodcastScreen(),
        '/settings': (context) => const SettingsScreen(),
      },
    );
  }

}

