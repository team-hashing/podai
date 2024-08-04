document.addEventListener('DOMContentLoaded', () => {
    const podcastCards = document.querySelectorAll('.podcast-card');
    const audioPlayer = document.getElementById('audio-player');
    const audioElement = document.getElementById('audio-element');
    const currentPodcastImage = document.getElementById('current-podcast-image');
    const currentPodcastTitle = document.getElementById('current-podcast-title');
    const currentPodcastAuthor = document.getElementById('current-podcast-author');

    let index = 0;
    podcastCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.animation = 'cardPop 0.3s forwards';
        });

        card.addEventListener('mouseleave', () => {
            card.style.animation = 'cardUnpop 0.3s forwards';
        });

        const playButton = card.querySelector('.play-button');
        if (playButton) {
            playButton.addEventListener('click', (e) => {
                e.preventDefault();
                const podcastId = card.dataset.podcastId;
                const podcastName = card.querySelector('.podcast-title').textContent;
                const podcastImage = card.querySelector('.podcast-image').src;
                const podcastAuthor = card.querySelector('.podcast-author').textContent;
                playPodcast(podcastId, podcastName, podcastImage, podcastAuthor);
            });
        }

        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
        index++;

    });


    const likedSection = document.querySelector('#liked .podcast-grid');
    let userInfoElement = document.getElementById('user_info');
    const likeButtons = document.querySelectorAll('.like-button');

    console.log(userInfoElement)
    let userInfo = {};
    
    if (userInfoElement) {
        let userInfoText = userInfoElement.textContent;
        if (userInfoText) {
            try {
                userInfo = JSON.parse(userInfoText);
            } catch (error) {
                console.error("Error parsing JSON:", error);
            }
        } else {
            console.warn("User info element is empty.");
        }
    } else {
        console.warn("User info element not found.");
    }

    // if not userInfo.liked_podcasts, create it TODO
    if (!userInfo.liked_podcasts) {
        userInfo.liked_podcasts = [];
    }


    likeButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const podcastId = button.dataset.podcastId;
            const isLiked = button.classList.contains('liked');

            try {

                // Toggle liked state
                button.classList.toggle('liked');

                // Add animation class
                button.classList.add(isLiked ? 'unliking' : 'liking');

                // Remove animation class after animation completes
                setTimeout(() => {
                    button.classList.remove('liking', 'unliking');
                }, 500);

                // Update userInfo.liked_podcasts
                if (isLiked) {
                    userInfo.liked_podcasts = userInfo.liked_podcasts.filter(id => id !== podcastId);
                } else {
                    
                    userInfo.liked_podcasts.push(podcastId);
                }

                // Update the liked section
                updateLikedSection(podcastId, isLiked);

            } catch (error) {
                console.error('Error updating like status:', error);
                // Optionally, show an error message to the user
            }

            const response = await fetch(`/${isLiked ? 'unlike' : 'like'}_podcast/${podcastId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // Include any necessary authentication headers
                },
            });

            if (!response.ok) {
                throw new Error('Failed to update like status');
            }
        });
    });

    function updateLikedSection(podcastId, wasLiked) {
        const podcastCard = document.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        if (!podcastCard) {
            return;
        }
    
        if (wasLiked) {
            // Remove from liked section
            const likedCard = likedSection.querySelector(`.podcast-card[podcast-id="${podcastId}"]`);
            if (likedCard) {
                likedCard.remove();
            }
        } else {
            // Add to liked section
            const clonedCard = podcastCard.cloneNode(true);
            setupLikeButton(clonedCard.querySelector('.like-button'));
            likedSection.insertBefore(clonedCard, likedSection.firstChild);
        }
        updateLikeCount(podcastId, !wasLiked);

    }
    
    function setupLikeButton(button) {
        button.addEventListener('click', async () => {
            const podcastId = button.dataset.podcastId;
            const isLiked = button.classList.contains('liked');
    
            // Toggle liked state
            button.classList.toggle('liked');
    
            // Add animation class
            button.classList.add(isLiked ? 'unliking' : 'liking');
    
            // Update like count
            updateLikeCount(podcastId, !isLiked);
    
            // Remove animation class after animation completes
            setTimeout(() => {
                button.classList.remove('liking', 'unliking');
            }, 500);
        });
    }
    
    function updateLikeCount(podcastId, isLiked) {
        const podcastCard = document.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        const likeCountElement = podcastCard.querySelector('.like-count');
        let likeCount = parseInt(likeCountElement.textContent, 10);
    
        if (isLiked) {
            likeCount++;
        } else {
            likeCount--;
        }
    
        likeCountElement.textContent = likeCount;
    }
    


    console.log('loaded');

    async function playPodcast(podcastId, podcastName, podcastImage, podcastAuthor) {
        try {
            // Extract userId from cookies
            const getCookie = (name) => {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
            };

            const userId = getCookie('user_id');
            if (!userId) {
                showErrorNotification('User ID not found in cookies');
                return;
            }

            const response = await fetch(`/audio/${podcastId}`);
            console.log(response);
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                audioElement.src = audioUrl;
                audioElement.play();
                currentPodcastImage.src = podcastImage;
                currentPodcastTitle.textContent = podcastName;
                currentPodcastAuthor.textContent = podcastAuthor;
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
        console.log('clicked');
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
                <img src="static/images/placeholder.png" alt="${podcastName} cover image" class="podcast-image">
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
        if (playButton) {
            playButton.addEventListener('click', (e) => {
                e.preventDefault();
                const podcastId = card.dataset.podcastId;
                const podcastName = card.querySelector('.podcast-title').textContent;
                const podcastImage = card.querySelector('.podcast-image').src;
                const podcastAuthor = card.querySelector('.podcast-author').textContent;
                playPodcast(podcastId, podcastName, podcastImage, podcastAuthor);
            });
        }
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