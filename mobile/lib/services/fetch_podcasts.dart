import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:podai/models/podcast_model.dart';
import 'package:podai/services/audio_service.dart';
import 'package:podai/services/auth_service.dart';
import 'package:podai/services/cache_service.dart';
import 'package:podai/constants.dart';

class FetchPodcastsService {
  final String url_by_likes = '$apiUrl/api/podcasts_by_likes';
  final String url_creator = '$apiUrl/api/podcasts';
  String userId = AuthService().getCurrentUser()!.uid;

  Future<List<Podcast>> fetchAllPodcasts({bool forceFetch = false}) async {
    List<Podcast> cachedPodcasts = [];
    /* 
    if (!forceFetch) {
      print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE');
      
      cachedPodcasts =
          await CacheService.instance.getCachedPodcasts('popular_podcasts');
      if (cachedPodcasts.isNotEmpty) {
        return cachedPodcasts;
      }
      
    }
    */

    try {
      final Map<String, dynamic> body = {
        'user_id': userId,
        'page': 0,
        'per_page': 10,
      };
      final response = await http.post(
        Uri.parse(url_by_likes),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );
      if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        List<Future<Podcast>> podcastFutures = data
            .map((podcast) => Podcast.fromMap(podcast, podcast['id']))
            .toList();
        List<Podcast> fetchedPodcasts = await Future.wait(podcastFutures);
        await AudioService.instance.loadAllPodcastProgress(fetchedPodcasts);

        // Combine cached and fetched podcasts, ensuring no duplicates
        Map<String, Podcast> podcastMap = {
          for (var podcast in cachedPodcasts) podcast.uuid: podcast
        };
        for (var podcast in fetchedPodcasts) {
          podcastMap[podcast.uuid] = podcast;
        }
        List<Podcast> updatedPodcasts = podcastMap.values.toList();

        // Cache the updated list of podcasts
        await CacheService.instance
            .cachePodcasts('popular_podcasts', updatedPodcasts);

        return updatedPodcasts;
      } else {
        print('Failed to fetch podcasts. Status code: ${response.statusCode}');
        return cachedPodcasts; // Return cached podcasts if fetch fails
      }
    } catch (e) {
      print('Error fetching podcasts: $e');
      return cachedPodcasts; // Return cached podcasts if an error occurs
    }
  }

  Future<List<Podcast>> fetchPodcastsByCreator(
      {bool forceFetch = false}) async {
    // Cache and cache verification
    List<Podcast> cachedPodcasts = [];
    if (!forceFetch) {
      cachedPodcasts =
          await CacheService.instance.getCachedPodcasts('user_podcasts');
      if (cachedPodcasts.isNotEmpty) {
        return cachedPodcasts;
      }
    }

    // Server request
    try {
      final Map<String, dynamic> body = {
        'user_id': userId,
        'page': 0,
        'per_page': 10,
      };
      final response = await http.post(
        Uri.parse(url_creator),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );
      if (response.statusCode == 200) {
        List<dynamic> data = jsonDecode(response.body);
        List<Future<Podcast>> podcastFutures = data
            .map((podcast) => Podcast.fromMap(podcast, podcast['id']))
            .toList();
        List<Podcast> fetchedPodcasts = await Future.wait(podcastFutures);
        await AudioService.instance.loadAllPodcastProgress(fetchedPodcasts);

        // Combine cached and fetched podcasts, ensuring no duplicates
        Map<String, Podcast> podcastMap = {
          for (var podcast in cachedPodcasts) podcast.uuid: podcast
        };
        for (var podcast in fetchedPodcasts) {
          podcastMap[podcast.uuid] = podcast;
        }
        List<Podcast> updatedPodcasts = podcastMap.values.toList();

        // Cache the updated list of podcasts
        await CacheService.instance
            .cachePodcasts('user_podcasts', updatedPodcasts);

        return updatedPodcasts;
      } else {
        print('Failed to fetch podcasts. Status code: ${response.statusCode}');
        return cachedPodcasts; // Return cached podcasts if fetch fails
      }
    } catch (e) {
      print('Error fetching podcasts: $e');
      return cachedPodcasts; // Return cached podcasts if an error occurs
    }
  }
}
