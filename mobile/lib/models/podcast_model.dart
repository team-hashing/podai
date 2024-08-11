import 'package:podai/services/services.dart';

class Podcast {
	final String uuid;
	final String name;
	final String creator;
	int _progress;
	DateTime createdAt;
	int likes;
	List<String> likedBy;

	Podcast({
		required this.uuid,
		required this.name,
		required this.creator,
		required int progress, // Use a parameter for progress
		required this.createdAt,
		required this.likes,
		required this.likedBy,
	}) : _progress = progress; // Initialize the private field

	// Getter for progress
	int get progress => _progress;

	// Setter for progress
	set progress(int value) {
		_progress = value;
	}

	// Calculate progress percentage
	double getProgressPercentage(Duration duration) {
		if (duration.inMilliseconds == 0) return 0;
		return (_progress / duration.inMilliseconds) * 100;
	}

	// Convert a Podcast object into a map
	Map<String, dynamic> toMap() {
		return {
			'uuid': uuid,
			'title': name,
			'creator': creator,
			'progress': _progress,
			'createdAt': createdAt.toIso8601String(),
			'likes': likes,
			'likedBy': likedBy,
		};
	}
	

	// Create a Podcast object from a map
	static Future<Podcast> fromMap(Map<String, dynamic> map, String uuid) async {
		return Podcast(
			uuid: uuid,
			name: map['name'],
			creator: map['username'],
			progress: 0,
			createdAt: DateTime.now(), //mocked
			likes: map['likes'],
			likedBy: List<String>.from(map['liked_by']),
		);
	}

	//create a podcast object from the cache map
	factory Podcast.fromCacheMap(Map<String, dynamic> map) {
		return Podcast(
			uuid: map['uuid'],
			name: map['title'],
			creator: map['creator'],
			progress: map['progress'],
			createdAt: DateTime.parse(map['createdAt']),
			likes: map['likes'],
      likedBy: List<String>.from(map['liked_by'] ?? []),
		);
	}

	static List<Podcast> podcastMocks = [
		Podcast(
			uuid: 'BkofQvdg2EdktqL1tYfu',
			name: 'The first podcast',
			creator: 'John Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
		Podcast(
			uuid: 'b710ea43-49d9-4142-9d75-a6ef6120f336',
			name: 'The second podcast',
			creator: 'Jane Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
		Podcast(
			uuid: '3',
			name: 'The third podcast',
			creator: 'John Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
		Podcast(
			uuid: '4',
			name: 'The fourth podcast',
			creator: 'Jane Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
		Podcast(
			uuid: '5',
			name: 'The fifth podcast',
			creator: 'John Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
		Podcast(
			uuid: '6',
			name: 'The sixth podcast',
			creator: 'Jane Doe',
			progress: 0,
			createdAt: DateTime.now(),
			likes: 0,
			likedBy: [],
		),
	];
}
