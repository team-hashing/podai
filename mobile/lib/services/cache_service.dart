import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/podcast_model.dart';
import 'package:dio/dio.dart';

class CacheService {
  static final CacheService _instance = CacheService._internal();
  static CacheService get instance => _instance;
  final Dio _dio = Dio();

  CacheService._internal();

  Future<void> cachePodcasts(String key, List<Podcast> podcasts) async {
    final prefs = await SharedPreferences.getInstance();
    final String encodedData = jsonEncode(podcasts.map((p) => p.toMap()).toList());
    await prefs.setString(key, encodedData);
  }

  Future<List<Podcast>> getCachedPodcasts(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final String? encodedData = prefs.getString(key);
    if (encodedData != null) {
      final List<dynamic> decodedData = jsonDecode(encodedData);
      return decodedData.map((data) => Podcast.fromCacheMap(data)).toList();
    }
    return [];
  }


  Future<String> getCachedFilePath(String url) async {
    final directory = await getApplicationDocumentsDirectory();
    final filePath = '${directory.path}/${url.hashCode}.wav';
    return filePath;
  }


  Future<File> downloadFile(String url) async {
    final filePath = await getCachedFilePath(url);
    final file = File(filePath);

    if (await file.exists()) {
      return file;
    } else {
      final response = await _dio.download(url, filePath);
      if (response.statusCode == 200) {
        return file;
      } else {
        throw Exception('Failed to download file');
      }
    }
  }
}