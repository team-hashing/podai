import 'dart:io';
import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:just_audio/just_audio.dart';
import 'package:podai/services/services.dart';
import 'package:rxdart/rxdart.dart';
import '../models/models.dart';
import 'dart:async';


class AudioService {
  static final AudioService _instance = AudioService._internal();
  final AudioPlayer _audioPlayer = AudioPlayer();
  static AudioService get instance => _instance;
  final BehaviorSubject<Podcast?> _currentPodcastSubject = BehaviorSubject<Podcast?>();


  int currentProgress = 0;	

  AudioService._internal();

  AudioPlayer get audioPlayer => _audioPlayer;
  StreamSubscription<Duration>? _positionSubscription;
  Stream<Podcast?> get currentPodcastStream => _currentPodcastSubject.stream;
  Stream<bool> get isPlayingStream => _audioPlayer.playingStream;
  Podcast? get _currentPodcast => _currentPodcastSubject.valueOrNull;  
  set _currentPodcast(Podcast? podcast) => _currentPodcastSubject.add(podcast);

  Future<void> initialize(List<Podcast> podcasts) async {
    await loadAllPodcastProgress(podcasts);
  }

Future<void> setCurrentPodcast(Podcast podcast) async {
  try {
    stopPositionListener();
    _currentPodcast = podcast;
    String audioUrl = await StoreService.instance.accessFile(podcast.uuid, Types.audio);
    print('Setting audio URL: $audioUrl');
    print('Initial position: ${podcast.progress} ms');

    await audioPlayer.setUrl(audioUrl).then((_) async {
      // After setting the audio source, seek to the last known position
      Duration initialPosition = Duration(milliseconds: podcast.progress);
      await audioPlayer.seek(initialPosition).then(
        (_) => _setupPositionListener(),
      );
    });
  } catch (e) {
    print('Error setting current podcast: $e');
    // Handle the error appropriately, e.g., show a message to the user
  }
}


  Stream<SeekBarData> get seekBarDataStream => Rx.combineLatest2<Duration, Duration?, SeekBarData>(
        _audioPlayer.positionStream,
        _audioPlayer.durationStream,
        (Duration position, Duration? duration) {
          return SeekBarData(position, duration ?? Duration.zero);
        },
      );
  
  Podcast? getCurrentPodcast() {
    return _currentPodcast; 
  }

  void _setupPositionListener() {
    _positionSubscription = _audioPlayer.positionStream.listen((position) {
      int progress = position.inMilliseconds;
      currentProgress = progress;
    });
  }
  
  void stopPositionListener() {
    updatePodcastProgress();
    _positionSubscription?.cancel();
    _positionSubscription = null;
    _currentPodcast = null;
  }

void updatePodcastProgress() async {
  if (_currentPodcast != null) {
    _currentPodcast!.progress = currentProgress;
    SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setInt('progress_${_currentPodcast!.uuid}', currentProgress);
  }
}

Future<void> loadPodcastProgress(Podcast podcast) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  podcast.progress = prefs.getInt('progress_${podcast.uuid}') ?? 0;
}

Future<void> loadAllPodcastProgress(List<Podcast> podcasts) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  for (Podcast podcast in podcasts) {
    podcast.progress = prefs.getInt('progress_${podcast.uuid}') ?? 0;
  }
}

  void play() {
    _audioPlayer.play();
  }

  void pause() {
    _audioPlayer.pause();
  }

  void seek(Duration position) {
    _audioPlayer.seek(position);
  }

  void seekToBeginning() {
    _audioPlayer.seek(Duration.zero, index: _audioPlayer.effectiveIndices?.first);
  }

  void seekForward10Seconds() {
    final position = _audioPlayer.position;
    final newPosition = min(_audioPlayer.duration?.inMilliseconds ?? 0, position.inMilliseconds + const Duration(seconds: 10).inMilliseconds);
    _audioPlayer.seek(Duration(milliseconds: newPosition));
  }

  void seekBackward10Seconds() {
    final position = _audioPlayer.position;
    final newPosition = max(0, position.inMilliseconds - const Duration(seconds: 10).inMilliseconds);
    _audioPlayer.seek(Duration(milliseconds: newPosition));
  }


  void setSpeed(double speed) {
    _audioPlayer.setSpeed(speed);
  }

  void dispose() {
    _audioPlayer.dispose();
    _currentPodcastSubject.close();
  }

  Stream<Duration> get positionStream => _audioPlayer.positionStream;

  Future<Duration?> get duration async => _audioPlayer.duration;
}

class SeekBarData {
  final Duration position;
  final Duration duration;

  SeekBarData(this.position, this.duration);
}
