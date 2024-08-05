document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('passwordStrength');
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const errorPopup = document.getElementById('errorPopup');

    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', updatePasswordStrength);
    }

    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    function updatePasswordStrength() {
        const password = passwordInput.value;
        const strength = calculatePasswordStrength(password);
        passwordStrength.style.width = `${strength}%`;
        passwordStrength.style.backgroundColor = getStrengthColor(strength);
    }

    function calculatePasswordStrength(password) {
        let strength = 0;
        if (password.length > 6) strength += 20;
        if (password.match(/[a-z]+/)) strength += 20;
        if (password.match(/[A-Z]+/)) strength += 20;
        if (password.match(/[0-9]+/)) strength += 20;
        if (password.match(/[$@#&!]+/)) strength += 20;
        return strength;
    }

    function getStrengthColor(strength) {
        if (strength < 40) return '#bbbbbb';
        if (strength < 70) return '#AA3090';
        return '#800080';
    }

    async function handleSignup(e) {
        e.preventDefault();
        const formData = new FormData(signupForm);
        try {
            const response = await fetch('/signup', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail);
            }
            window.location.href = '/';
        } catch (error) {
            showError(error.message);
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(loginForm);
        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail);
            }
            window.location.href = '/';
        } catch (error) {
            showError(error.message);
        }
    }

    function showError(message) {
        errorPopup.textContent = message;
        errorPopup.style.display = 'block';
        errorPopup.classList.add('shake');
        setTimeout(() => {
            errorPopup.classList.remove('shake');
        }, 820);
    }

    /* Transition */
    function startPageTransition() {
        document.body.classList.add('transition-active');
        const transitionDiv = document.querySelector('.page-transition');
        const icon = document.createElement('i');
        icon.className = 'fas fa-spin fa-cog transition-icon';
        transitionDiv.appendChild(icon);
    }

    function navigateWithTransition(url) {
        startPageTransition();
        setTimeout(() => {
            window.location.href = url;
        }, 1000);
    }

    // Modify the handleSignup and handleLogin functions
    async function handleSignup(e) {
        e.preventDefault();
        const formData = new FormData(signupForm);
        try {
            const response = await fetch('/signup', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail);
            }
            navigateWithTransition('/');
        } catch (error) {
            showError(error.message);
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(loginForm);
        try {
            const response = await fetch('/login', {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail);
            }
            navigateWithTransition('/');
        } catch (error) {
            showError(error.message);
        }
    }
});