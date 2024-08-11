import 'dart:convert'; // Import this for jsonEncode
import 'package:http/http.dart' as http;
import 'package:podai/services/services.dart';
import 'package:podai/constants.dart';


class CreatePodcastService {
  final String url = '$apiUrl/api/generate_podcast';

  Future<bool> generatePodcast(String subject, String podcastName) async {
    String userId = AuthService().getCurrentUser()!.uid;

    final Map<String, String> body = {
      'user_id': userId,
      'subject': subject,
      'podcast_name': podcastName,
    };

    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'}, // Set the content type to JSON
        body: jsonEncode(body), // Encode the body to JSON
      );
      if (response.statusCode == 200) {
        // Podcast generation successful
        print('Podcast generated successfully');
        return true;
      } else {
        // Handle error
        print('Failed to generate podcast. Status code: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      // Handle exception
      print('Error generating podcast: $e');
      return false;
    }
  }
}