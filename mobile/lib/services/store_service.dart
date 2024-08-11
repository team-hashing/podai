import 'package:firebase_storage/firebase_storage.dart';

enum Types {
  audio,
  cover,
}

class StoreService {
  StoreService._privateConstructor();
  static final StoreService _instance = StoreService._privateConstructor();

  static StoreService get instance => _instance; // Static getter for the instance

  final Map<String, String> _urlCache = {}; // Cache for URLs

  Future<String> accessFile(String id, Types type) async {
    // Create a reference to the file
    FirebaseStorage storage = FirebaseStorage.instance;
    String filePath = id + (type == Types.audio ? '/audio.wav' : '/image.png');
    String cacheKey = '$id-${type.toString()}';

    // Check cache first
    if (_urlCache.containsKey(cacheKey)) {
      return _urlCache[cacheKey]!;
    }

    Reference ref = storage.refFromURL('gs://podai-425012.appspot.com/podcasts/$filePath');

    // To get a URL to the file
    try {
      String fileURL = await ref.getDownloadURL();
      _urlCache[cacheKey] = fileURL; // Update cache
      return fileURL;
      // Use the file URL to download, stream, or display the file
    } catch (e) {
      print('Error accessing file: $e');
      throw e;
    }
  }
}