import 'package:flutter/material.dart';


class PlaceholderTab extends StatelessWidget {
  final String text;

  const PlaceholderTab(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text(text),
    );
  }
}