import 'package:flutter/material.dart';
import 'package:podai/widgets/widgets.dart';

class CreateScreen extends StatefulWidget {
  const CreateScreen({super.key});

  @override
  _CreateScreenState createState() => _CreateScreenState();
}
class _CreateScreenState extends State<CreateScreen> {
  final TextEditingController _textController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4, // The number of tabs / length of the TabBar
      child: Stack(
        children: [
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color.fromARGB(255, 36, 23, 56), // Purple
                    Color(0xFF000000), // Black
                  ],
                ),
              ),
            ),
          ),
          Scaffold(
            backgroundColor: Colors.transparent, // Make Scaffold background transparent
            appBar: AppBar(
              backgroundColor: Colors.transparent,

              bottom: TabBar(
                labelColor: Colors.purple[300],
                unselectedLabelColor: Colors.white,
                indicatorColor: const Color.fromARGB(255, 132, 40, 148),
                dividerColor: Colors.transparent,
                tabs: const [
                  Tab(text: 'Text'),
                  Tab(text: 'URL'),
                  Tab(text: 'Category'),
                  Tab(text: 'PDF'),
                ],
              ),
            ),
            body: const TabBarView(
              children: [
                // Add your tab views here
                CreateWidgetTextInputTab(),
                Center(child: Text('URL Tab')),
                Center(child: Text('Category Tab')),
                Center(child: Text('PDF Tab')),
              ],
            ),
          ),
        ],
      ),
    );
  }
}