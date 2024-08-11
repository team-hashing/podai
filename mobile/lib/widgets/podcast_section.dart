import 'package:flutter/material.dart';
import 'package:podai/widgets/widgets.dart';
import 'package:podai/models/models.dart';
import 'package:podai/services/services.dart';

// Define an enum for the display types
enum DisplayType { cards, grid, list }

enum PodcastType { user, popular }

class PodcastSection extends StatefulWidget {
	final double itemWidth;
	final int gridCrossAxisCount;
	final double gridChildAspectRatio;
	final double crossAxisSpacing;
	final double mainAxisSpacing;
	final String? title;
	final TextStyle? titleStyle;
	final EdgeInsetsGeometry padding;
	final double height;
	final DisplayType displayType;
	final PodcastType podcastType;

	const PodcastSection({
		super.key,
		this.itemWidth = 150,
		this.gridCrossAxisCount = 2,
		this.gridChildAspectRatio = .8,
		this.crossAxisSpacing = 10,
		this.mainAxisSpacing = 10,
		this.title,
		this.titleStyle,
		this.padding = const EdgeInsets.all(10),
		this.height = 250,
		this.displayType = DisplayType.cards,
		this.podcastType = PodcastType.popular,
	});

	@override
	_PodcastSectionState createState() => _PodcastSectionState();
}

class _PodcastSectionState extends State<PodcastSection> {
	List<Podcast> podcasts = [];

	@override
	void initState() {
		super.initState();
		loadPodcasts();
	}

	void loadPodcasts() async {
		List<Podcast> fetchedPodcasts;
		if (widget.podcastType == PodcastType.user) {
			fetchedPodcasts = await FetchPodcastsService().fetchPodcastsByCreator();
			fetchedPodcasts.sort((a, b) => b.createdAt.compareTo(a.createdAt));
		} else {
			fetchedPodcasts = await FetchPodcastsService().fetchAllPodcasts();
			fetchedPodcasts.sort((a, b) => b.likes.compareTo(a.likes));
		}
		if (mounted) {
			setState(() {
				podcasts = fetchedPodcasts;
			});
		}
	}

	@override
	Widget build(BuildContext context) {
		Widget content;

		switch (widget.displayType) {
			case DisplayType.grid:
				double screenWidth = MediaQuery.of(context).size.width;
				double itemWidth = (screenWidth -
								(widget.crossAxisSpacing * (widget.gridCrossAxisCount - 1))) /
						widget.gridCrossAxisCount;
				content = GridView.builder(
					gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
						crossAxisCount: widget.gridCrossAxisCount,
						childAspectRatio: widget.gridChildAspectRatio,
						crossAxisSpacing: widget.crossAxisSpacing,
						mainAxisSpacing: widget.mainAxisSpacing,
					),
					shrinkWrap: true,
					physics: const NeverScrollableScrollPhysics(),
					itemCount: podcasts.length,
					itemBuilder: (context, index) {
						final podcast = podcasts[index];
						return SizedBox(
							width: itemWidth,
							height: widget.height,
							child: PodcastCard(
								key: Key(podcast.uuid),
								podcast: podcast,
							),
						);
					},
				);
				break;
			case DisplayType.list:
				content = ListView.builder(
					padding: widget.padding,
					shrinkWrap: true,
					physics: const NeverScrollableScrollPhysics(),
					itemCount: podcasts.length,
					itemBuilder: (context, index) {
						final podcast = podcasts[index];
						return SizedBox(
							child: HorizontalPodcastCard(
								key: Key(podcast.uuid),
								podcast: podcast,
							),
						);
					},
				);
				break;
			case DisplayType.cards:
			default:
				content = SizedBox(
					height: widget.height,
					child: ListView.builder(
						padding: widget.padding,
						shrinkWrap: true,
						scrollDirection: Axis.horizontal,
						itemCount: podcasts.length,
						itemBuilder: (context, index) {
							final podcast = podcasts[index];
							return SizedBox(
								width: widget.itemWidth,
								height: widget.height,
								child: PodcastCard(
									key: Key(podcast.uuid),
									podcast: podcast,
								),
							);
						},
					),
				);
				break;
		}
		return Column(
			crossAxisAlignment: CrossAxisAlignment.start,
			children: [
				if (widget.title != null)
					Padding(
						padding: const EdgeInsets.only(left: 16, bottom: 8),
						child: Text(widget.title!,
								style: widget.titleStyle ??
										const TextStyle(
												fontSize: 22,
												fontWeight: FontWeight.bold,
												color: Colors.white)),
					),
				content,
			],
		);
	}
}
