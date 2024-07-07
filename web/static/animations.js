document.addEventListener('DOMContentLoaded', () => {
    const podcastCards = document.querySelectorAll('.podcast-card');
    const audioPlayer = document.getElementById('audio-player');
    const audioElement = document.getElementById('audio-element');
    const currentPodcastImage = document.getElementById('current-podcast-image');
    const currentPodcastTitle = document.getElementById('current-podcast-title');
    const currentPodcastAuthor = document.getElementById('current-podcast-author');

    podcastCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.animation = 'cardPop 0.3s forwards';
        });

        card.addEventListener('mouseleave', () => {
            card.style.animation = 'cardUnpop 0.3s forwards';
        });

        const playButton = card.querySelector('.play-button');
        playButton.addEventListener('click', (e) => {
            e.preventDefault();
            const podcastId = card.dataset.podcastId;
            const podcastName = card.querySelector('.podcast-title').textContent;
            const podcastImage = card.querySelector('.podcast-image').src;
            playPodcast(podcastId, podcastName, podcastImage);
        });
    });

    async function playPodcast(podcastId, podcastName, podcastImage) {
        try {
            const userId = 'user1'; // TODO Replace with actual user ID when you have user authentication
            const response = await fetch(`/audio/${userId}/${podcastId}`);

            if (response.ok) {
                const data = await response.json();
                audioElement.src = data.audioUrl;
                audioElement.play();
                currentPodcastImage.src = podcastImage;
                currentPodcastTitle.textContent = podcastName;
                currentPodcastAuthor.textContent = 'Podcast Author'; // TODO
                audioPlayer.classList.add('active');
            } else {
                showErrorNotification('Audio file not found');
            }
        } catch (error) {
            showErrorNotification('Error playing podcast');
        }
    }

    function showErrorNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        // Trigger reflow to ensure the transition works
        notification.offsetHeight;

        notification.classList.add('active');

        setTimeout(() => {
            notification.classList.remove('active');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    const generatePodcastBtn = document.getElementById('generate-podcast-btn');
    const generatePodcastMenu = document.getElementById('generate-podcast-menu');
    const generatePodcastForm = document.getElementById('generate-podcast-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const closeMenuBtn = document.getElementById('close-menu-btn');

    generatePodcastBtn.addEventListener('click', () => {
        generatePodcastMenu.classList.add('active');
    });

    closeMenuBtn.addEventListener('click', () => {
        generatePodcastMenu.classList.remove('active');
    });

    generatePodcastForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const podcastName = document.getElementById('podcast-name').value;
        const podcastSubject = document.getElementById('podcast-subject').value;

        // Close the menu
        generatePodcastMenu.classList.remove('active');

        // Create and add a loading podcast card
        const loadingCard = createLoadingPodcastCard(podcastName);
        const podcastGrid = document.querySelector('.podcast-grid');
        podcastGrid.appendChild(loadingCard);

        try {
            const response = await fetch('/generate-podcast', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: podcastName, subject: podcastSubject }),
            });

            if (response.ok) {
                const newPodcast = await response.json();
                updatePodcastCard(loadingCard, newPodcast);
            } else {
                showErrorNotification('Failed to generate podcast');
                loadingCard.remove();
            }
        } catch (error) {
            showErrorNotification('Error generating podcast');
            loadingCard.remove();
        }
    });

    function createLoadingPodcastCard(podcastName) {
        const card = document.createElement('div');
        card.className = 'podcast-card loading';
        card.innerHTML = `
            <div class="podcast-image-container">
                <img src="/static/images/placeholder.jpg" alt="${podcastName} cover image" class="podcast-image">
                <div class="podcast-overlay">
                    <button class="play-button" disabled>▶</button>
                </div>
            </div>
            <h3 class="podcast-title">${podcastName}</h3>
        `;
        return card;
    }

    function updatePodcastCard(card, podcast) {
        card.dataset.podcastId = podcast.id;
        card.querySelector('img').src = podcast.image;
        card.querySelector('.podcast-title').textContent = podcast.name;
        card.querySelector('.play-button').disabled = false;
        card.classList.remove('loading');

        // Add event listeners for hover and play button
        addCardEventListeners(card);
    }

    function addCardEventListeners(card) {
        card.addEventListener('mouseenter', () => {
            card.style.animation = 'cardPop 0.3s forwards';
        });

        card.addEventListener('mouseleave', () => {
            card.style.animation = 'cardUnpop 0.3s forwards';
        });

        const playButton = card.querySelector('.play-button');
        playButton.addEventListener('click', (e) => {
            e.preventDefault();
            const podcastId = card.dataset.podcastId;
            const podcastName = card.querySelector('.podcast-title').textContent;
            const podcastImage = card.querySelector('.podcast-image').src;
            playPodcast(podcastId, podcastName, podcastImage);
        });
    }

    function addNewPodcastCard(podcast) {
        const podcastGrid = document.querySelector('.podcast-grid');
        const newCard = document.createElement('div');
        newCard.className = 'podcast-card loading';
        newCard.dataset.podcastId = podcast.id;
        newCard.innerHTML = `
            <div class="podcast-image-container">
                <img src="${podcast.image}" alt="${podcast.name} cover image" class="podcast-image">
                <div class="podcast-overlay">
                    <button class="play-button">▶</button>
                </div>
                <div class="loading-spinner"></div>
            </div>
            <h3 class="podcast-title">${podcast.name}</h3>
        `;
        podcastGrid.appendChild(newCard);

        // Simulate async loading (remove this in production and use real async operations)
        setTimeout(() => {
            newCard.classList.remove('loading');
            newCard.querySelector('.loading-spinner').remove();
        }, 5000); // Simulating 5 seconds of loading time
    }
});


// Add these keyframe animations to your CSS file
const style = document.createElement('style');
style.textContent = `
    @keyframes cardPop {
        0% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
        100% {
            transform: scale(1.03);
        }
    }

    @keyframes cardUnpop {
        0% {
            transform: scale(1.03);
        }
        100% {
            transform: scale(1);
        }
    }
`;
document.head.appendChild(style);