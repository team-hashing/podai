import 'package:flutter/material.dart';
import 'package:podai/screens/app.dart';
import 'package:podai/services/services.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final AuthService _authService = AuthService();
  final _formKey = GlobalKey<FormState>();
  String email = '';
  String password = '';
  String error = '';
  bool isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Container(
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
          ),
          Scaffold(
            backgroundColor: Colors.transparent,
            appBar: AppBar(
              title: const Text('Login'),
              backgroundColor: Colors.transparent,
              elevation: 0,
              iconTheme: const IconThemeData(color: Colors.white),
              titleTextStyle:
                  const TextStyle(color: Colors.white, fontSize: 20),
            ),
            body: Container(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: SingleChildScrollView(
                  child: Form(
                    key: _formKey,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                        TextFormField(
                          decoration: const InputDecoration(
                            labelText: 'Email',
                            labelStyle: TextStyle(color: Colors.white),
                          ),
                          style: const TextStyle(color: Colors.white),
                          validator: (val) =>
                              val!.isEmpty ? 'Enter an email' : null,
                          onChanged: (val) {
                            setState(() => email = val);
                          },
                        ),
                        const SizedBox(height: 20),
                        TextFormField(
                          decoration: const InputDecoration(
                            labelText: 'Password',
                            labelStyle: TextStyle(color: Colors.white),
                          ),
                          style: const TextStyle(color: Colors.white),
                          obscureText: true,
                          validator: (val) => val!.length < 6
                              ? 'Enter a password 6+ chars long'
                              : null,
                          onChanged: (val) {
                            setState(() => password = val);
                          },
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            foregroundColor: Colors.white,
                            backgroundColor: const Color.fromARGB(
                                255, 56, 39, 97), // Teal color for the button
                            padding: const EdgeInsets.symmetric(vertical: 20),
                            textStyle: const TextStyle(fontSize: 18),
                            minimumSize: const Size.fromHeight(
                                50), // Make button full width
                          ),
                          child: const Text('Login'),
                          onPressed: () async {
                            if (_formKey.currentState!.validate()) {
                              setState(() => isLoading = true);
                              dynamic result =
                                  await _authService.signIn(email, password);
                              if (result == null) {
                                setState(() {
                                  error =
                                      'Could not sign in with those credentials';
                                  isLoading = false;
                                });
                              } else {
                                Navigator.pushAndRemoveUntil(
                                  context,
                                  MaterialPageRoute(
                                      builder: (context) => const MyApp()),
                                  (route) => false,
                                );
                              }
                            }
                          },
                        ),
                        const SizedBox(height: 12.0),
                        Text(
                          error,
                          style: const TextStyle(
                              color: Colors.red, fontSize: 14.0),
                        ),
                        const SizedBox(height: 20),
                        TextButton(
                          onPressed: () {
                            Navigator.pushNamed(context, '/register');
                          },
                          child: RichText(
                            text: const TextSpan(
                              children: [
                                TextSpan(
                                  text: 'Don\'t have an account? ',
                                  style: TextStyle(color: Colors.white),
                                ),
                                TextSpan(
                                  text: 'Register',
                                  style: TextStyle(
                                    color: Color.fromARGB(255, 168, 98, 208),
                                    decoration: TextDecoration.underline,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
