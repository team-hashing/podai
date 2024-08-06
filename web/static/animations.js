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

    const userSection = document.querySelector('#featured .podcast-grid');
    const likesSection = document.querySelector('#by-likes .podcast-grid');
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

                // Toggle liked stateº
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

                // find same-id 

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
        // update like count
        updateLikeCount(podcastId, !wasLiked);

        const userCard = userSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        const likesCard = likesSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        const likedCard = likedSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        if (!userCard && !likesCard && !likedCard) {
            return;
        }

        // if unlike
        if (wasLiked) {
            // Remove from liked section
            if (likedCard) {
                likedCard.remove();
            }

            // Replace from userSection and likesSection the card with same id if exists with clone card
            if (userCard) {
                // userCard.replaceWith(cloneCard);
                userCard.querySelector('.like-button').classList.remove('liked');
            }
            if (likesCard) {
                // likesCard.replaceWith(cloneCard);
                likesCard.querySelector('.like-button').classList.remove('liked');
            }


            // if like
        } else {
            // clone any of the cards
            let originalCard = userCard || likesCard || likedCard;
            let cloneCard = null;

            if (originalCard) {
                cloneCard = originalCard.cloneNode(true);
                cloneCard.querySelector('.like-button').classList.add('liked');
                addLikeButtonListener(cloneCard.querySelector('.like-button'));
                // setupLikeButton(cloneCard.querySelector('.like-button'));
            } else {
                console.error('Error: No se encontró ninguna tarjeta para clonar.');
            }
            if (!cloneCard) {
                return;
            }

            // Add 'liked' class to like button


            if (userCard) {
                // replace with clone card
                userCard.querySelector('.like-button').classList.add('liked');
            }
            if (likesCard) {
                likesCard.querySelector('.like-button').classList.add('liked');
            }
            // setupLikeButton(clonedCard.querySelector('.like-button'));

            if (cloneCard) {
                likedSection.insertBefore(cloneCard, likedSection.firstChild);
            } else {
                console.error(`Error: No element found with podcastId ${podcastId}`);
            }
        }
    }

    function addLikeButtonListener(button) {
        button.addEventListener('click', async () => {
            const podcastId = button.dataset.podcastId;
            const isLiked = button.classList.contains('liked');

            try {

                // Toggle liked stateº
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

                // find same-id 

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
        const userCard = userSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        if (userCard) {
            const likeCountElement = userCard.querySelector('.like-count');
            let likeCount = parseInt(likeCountElement.textContent, 10);

            if (isLiked) {
                likeCount++;
            } else {
                likeCount--;
            }

            likeCountElement.textContent = likeCount;
        }

        // Update the liked section
        const likedCard = likedSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        if (likedCard) {
            const likeCountElement = likedCard.querySelector('.like-count');
            let likeCount = parseInt(likeCountElement.textContent, 10);

            if (isLiked) {
                likeCount++;
            } else {
                likeCount--;
            }

            likeCountElement.textContent = likeCount;
        }

        // Update the likes section
        const likesCard = likesSection.querySelector(`.podcast-card[data-podcast-id="${podcastId}"]`);
        if (likesCard) {
            const likeCountElement = likesCard.querySelector('.like-count');
            let likeCount = parseInt(likeCountElement.textContent, 10);

            if (isLiked) {
                likeCount++;
            } else {
                likeCount--;
            }

            likeCountElement.textContent = likeCount;
        }
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

        generatePodcastMenu.classList.remove('active');

        try {
            const response = await fetch('/generate-podcast', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: podcastName, subject: podcastSubject }),
            });

            if (response.ok) {
                let newPodcast = await response.json();
                newPodcast.likes = 0;
                newPodcast.name = podcastName;
                newPodcast.author = userInfo.username;
                const loadingCard = createLoadingPodcastCard(newPodcast);
                const podcastGrid = document.querySelector('.podcast-grid');
                podcastGrid.insertBefore(loadingCard, podcastGrid.firstChild);

                // Start polling for status
                pollPodcastStatus(loadingCard, newPodcast.id);
            } else {
                const errorDetail = await response.json();
                if (errorDetail.detail === "Not enough tokens") {
                    showErrorNotification('Not enough tokens to generate podcast');
                } else {
                    showErrorNotification('Failed to generate podcast');
                }
            }
        } catch (error) {
            showErrorNotification('Error generating podcast');
        }
    });


    function createLoadingPodcastCard(podcast) {
        const card = document.createElement('div');
        card.className = 'podcast-card loading';
        card.setAttribute('data-podcast-id', podcast.id);
        card.innerHTML = `
            <div class="podcast-image-container">
                <img src="${podcast.image ? podcast.image : 'static/images/placeholder2.png'}"
                    alt="${podcast.name} cover image" class="podcast-image">
                <div class="loading-spinner"></div>
            </div>
            <h3 class="podcast-title">${podcast.name}</h3>
            <p class="podcast-author">${podcast.author}</p>
            <button class="like-button ${podcast.liked ? 'liked' : ''}"
                data-podcast-id="${podcast.id}">
                <span class="like-count">${podcast.likes}</span>
                <i class="fas fa-heart"></i>
                <div class="like-ripple"></div>
            </button>
        `;
        return card;
    }

    function updatePodcastCard(card, podcast) {
        if (!podcast) return;

        card.dataset.podcastId = podcast.id;
        card.querySelector('img').src = podcast.image;
        card.querySelector('.podcast-title').textContent = podcast.name;
        card.querySelector('.podcast-author').textContent = podcast.author;
        card.querySelector('.like-count').textContent = podcast.likes;

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

    /* auth transition */
    const contentWrapper = document.querySelector('.content-wrapper');
    const pageTransition = document.querySelector('.page-transition');

    function endPageTransition() {
        // Ensure the transition is visible
        document.body.classList.add('transition-active');
        pageTransition.style.opacity = '1';
        contentWrapper.style.transform = 'scale(0.9)';
        contentWrapper.style.opacity = '0';

        // Delay to allow the page content to load
        setTimeout(() => {
            // Fade out the transition
            pageTransition.style.opacity = '0';

            // Fade in and scale up the content
            contentWrapper.style.transform = 'scale(1)';
            contentWrapper.style.opacity = '1';

            // Remove the transition class after animation completes
            setTimeout(() => {
                document.body.classList.remove('transition-active');
                pageTransition.innerHTML = '';
            }, 500); // This should match the transition duration in CSS
        }, 500); // Adjust this delay as needed
    }

    // Check if we're coming from a login/signup page
    const pageTransitionCookie = document.cookie.split('; ').find(row => row.startsWith('page_transition='));
    if (pageTransitionCookie) {
        // Remove the cookie
        document.cookie = 'page_transition=; max-age=0; path=/;';
        endPageTransition();
    } else {
        // If not coming from login/signup, ensure no transition is visible
        document.body.classList.remove('transition-active');
        pageTransition.style.opacity = '0';
        contentWrapper.style.transform = 'scale(1)';
        contentWrapper.style.opacity = '1';
    }

    async function checkPodcastStatus(podcastId) {
        if (!podcastId || podcastId=="undefined") return null;
        try {
            const response = await fetch(`/check-podcast-status/${podcastId}`);
            if (response.ok) {
                const data = await response.json();
                return data.status;
            }
        } catch (error) {
            console.error('Error checking podcast status:', error);
        }
        return null;
    }

    function pollPodcastStatus(card, podcastId) {
        const interval = setInterval(async () => {
            const status = await checkPodcastStatus(podcastId);
            if (status === 'ready') {
                clearInterval(interval);
                updatePodcastCard(card, await fetchPodcastDetails(podcastId));
            }
        }, 5000); // Check every 5 seconds
    }

    async function fetchPodcastDetails(podcastId) {
        try {
            const response = await fetch(`/get-podcast-details/${podcastId}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching podcast details:', error);
        }
        return null;
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