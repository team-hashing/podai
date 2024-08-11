import 'package:flutter/material.dart';
import 'package:podai/models/models.dart';
import 'package:podai/services/services.dart';

import '../widgets/widgets.dart';

class PodcastProvider with ChangeNotifier {
  List<Podcast> _podcasts = [];

  List<Podcast> get podcasts => _podcasts;

  Future<void> fetchPodcasts(PodcastType type) async {
    List<Podcast> fetchedPodcasts;
    if (type == PodcastType.user) {
      fetchedPodcasts = await FetchPodcastsService().fetchPodcastsByCreator();
      fetchedPodcasts.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    } else {
      fetchedPodcasts = await FetchPodcastsService().fetchAllPodcasts();
      fetchedPodcasts.sort((a, b) => b.likes.compareTo(a.likes));
    }
    _podcasts = fetchedPodcasts;
    notifyListeners();
  }
}