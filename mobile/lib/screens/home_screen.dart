import 'package:flutter/material.dart';
import 'package:podai/models/models.dart';
import 'package:podai/services/services.dart';
import 'package:podai/widgets/widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Podcast> allPodcasts = [];
  bool isSearching = false;
  List<Podcast> searchResults = [];
  TextEditingController searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    loadPodcasts();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_onScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.atEdge) {
      if (_scrollController.position.pixels != 0) {
        _refreshPodcasts();
      }
    }
  }

  Future<void> _refreshPodcasts() async {
    allPodcasts =
        await FetchPodcastsService().fetchAllPodcasts(forceFetch: true);
  }

  void loadPodcasts() async {
    allPodcasts = await FetchPodcastsService().fetchAllPodcasts();
    if (mounted) {
      setState(() {});
    }
  }

  void startSearch() {
    setState(() {
      isSearching = true;
      searchResults.addAll(allPodcasts);
    });
  }

  void cancelSearch() {
    setState(() {
      isSearching = false;
      searchController.clear();
      searchResults.clear();
    });
  }

  void searchPodcasts(String query) {
    if (query.isEmpty) {
      setState(() {
        searchResults.addAll(allPodcasts);
      });
      return;
    }
    final results = allPodcasts.where((podcast) {
      final titleLower = podcast.name.toLowerCase();
      final searchLower = query.toLowerCase();
      return titleLower.contains(searchLower);
    }).toList();
    setState(() {
      searchResults = results;
    });
  }

  @override
  Widget build(BuildContext context) {
    AudioService audioService = AudioService.instance;
    return Scaffold(
      body: Stack(
        children: [
          Container(
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
          Scaffold(
            backgroundColor: Colors.transparent,
            appBar: AppBar(
              leading: isSearching
                  ? IconButton(
                      icon: const Icon(Icons.arrow_back),
                      onPressed: cancelSearch,
                    )
                  : null,
              backgroundColor: Colors.transparent,
              elevation: 0,
              title: isSearching
                  ? TextField(
                      controller: searchController,
                      autofocus: true,
                      decoration: const InputDecoration(
                        hintText: 'Search Podcasts...',
                        hintStyle: TextStyle(color: Colors.white),
                        border: InputBorder.none,
                      ),
                      style: const TextStyle(color: Colors.white),
                      onChanged: searchPodcasts,
                    )
                  : const Text(
                      'Home',
                      style: TextStyle(color: Colors.white),
                    ),
              actions: isSearching
                  ? []
                  : [
                      IconButton(
                        icon: const Icon(Icons.search),
                        onPressed: startSearch,
                        color: Colors.white,
                      ),
                    ],
            ),
            body: Stack(
              children: [
                isSearching
                    ? ListView.builder(
                        itemCount: searchResults.length,
                        itemBuilder: (context, index) {
                          final podcast = searchResults[index];
                          return HorizontalPodcastCard(podcast: podcast);
                        },
                      )
                    : RefreshIndicator(
                        onRefresh: _refreshPodcasts,
                        child: SingleChildScrollView(
                          controller: _scrollController,
                          padding: EdgeInsets.only(
                              bottom: audioService.getCurrentPodcast() != null
                                  ? 200
                                  : 0),
                          child: const Column(
                            children: [
                              PodcastSection(
                                key: Key('new_releases_section'),
                                displayType: DisplayType.cards,
                                title: 'New Releases',
                                podcastType: PodcastType.user,
                              ),
                              PodcastSection(
                                key: Key('trending_section'),
                                displayType: DisplayType.list,
                                title: 'Trending',
                              ),
                            ],
                          ),
                        ),
                      ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
