// ===== API Configuration =====
const API_BASE = '/api';

// ===== State =====
let allWorkers = [];
let currentFilter = 'all';
let currentUser = null;

// ===== DOM Elements =====
const workersGrid = document.getElementById('workers-grid');
const loading = document.getElementById('loading');
const noWorkers = document.getElementById('no-workers');
const authModal = document.getElementById('auth-modal');
const workerModal = document.getElementById('worker-modal');
const reviewModal = document.getElementById('review-modal');
const modalBody = document.getElementById('modal-body');
const toast = document.getElementById('toast');
const navAuth = document.getElementById('nav-auth');

// ===== Skill Icons =====
const skillIcons = {
    PLUMBER: '🔧',
    MAID: '🧹',
    BABYSITTER: '👶',
    ELECTRICIAN: '⚡',
    CARPENTER: '🪚',
    PAINTER: '🎨',
    GARDENER: '🌱',
    DAYCARE: '🏠',
    DRIVER: '🚗',
    COOK: '👨‍🍳',
    CLEANER: '🧽'
};

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', () => {
    // Check URL parameters for skill filter
    const urlParams = new URLSearchParams(window.location.search);
    const skillParam = urlParams.get('skill');
    if (skillParam) {
        currentFilter = skillParam;
        const filterEl = document.getElementById('skill-filter');
        if (filterEl) {
            filterEl.value = skillParam;
        }
    }

    loadWorkers();
    checkAuthState();
    setupEventListeners();
    setupScrollEffects();
});

// ===== Auth State =====
function checkAuthState() {
    const savedUser = localStorage.getItem('shobkaj_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateNavForLoggedInUser();
    }
}

function updateNavForLoggedInUser() {
    const roleIcon = currentUser.role === 'WORKER' ? '💼' : '🏠';
    navAuth.innerHTML = `
        <div class="user-menu" onclick="toggleUserMenu()">
            <div class="user-avatar">${roleIcon}</div>
            <span class="user-name">${currentUser.username}</span>
        </div>
        <button class="btn btn-outline" onclick="handleLogout()">Log Out</button>
    `;
}

function updateNavForLoggedOutUser() {
    navAuth.innerHTML = `
        <button class="btn btn-outline" onclick="openAuthModal('login')">Log In</button>
        <button class="btn btn-primary" onclick="openAuthModal('signup')">Sign Up</button>
    `;
}

// ===== Load Workers =====
async function loadWorkers() {
    // Only load workers if on a page with workers grid
    if (!workersGrid) return;

    try {
        if (loading) loading.style.display = 'block';
        if (noWorkers) noWorkers.style.display = 'none';
        workersGrid.innerHTML = '';

        const response = await fetch(`${API_BASE}/workers`);
        allWorkers = await response.json();

        // Update stats (only on homepage)
        const workerCountEl = document.getElementById('worker-count');
        if (workerCountEl) {
            workerCountEl.textContent = allWorkers.length;
        }

        // Count reviews (only on homepage)
        const reviewCountEl = document.getElementById('review-count');
        if (reviewCountEl) {
            let reviewCount = 0;
            for (const worker of allWorkers) {
                try {
                    const detail = await fetch(`${API_BASE}/workers/${worker.id}`);
                    const data = await detail.json();
                    if (data.reviews) {
                        reviewCount += data.reviews.length;
                    }
                } catch (e) {
                    // Skip if error
                }
            }
            reviewCountEl.textContent = reviewCount;
        }

        if (loading) loading.style.display = 'none';
        filterAndRenderWorkers();

    } catch (error) {
        console.error('Error loading workers:', error);
        if (loading) loading.style.display = 'none';
        showToast('Failed to load workers', 'error');
    }
}

// ===== Filter Workers =====
function filterWorkers() {
    const filterEl = document.getElementById('skill-filter');
    if (filterEl) {
        currentFilter = filterEl.value;
    }
    filterAndRenderWorkers();
}

function filterAndRenderWorkers() {
    if (!workersGrid) return;

    let filtered = allWorkers;

    if (currentFilter !== 'all') {
        filtered = allWorkers.filter(w => w.skill === currentFilter);
    }

    if (filtered.length === 0) {
        workersGrid.innerHTML = '';
        if (noWorkers) noWorkers.style.display = 'block';
        return;
    }

    if (noWorkers) noWorkers.style.display = 'none';
    workersGrid.innerHTML = filtered.map(worker => createWorkerCard(worker)).join('');

    // Add click listeners
    document.querySelectorAll('.worker-card').forEach(card => {
        card.addEventListener('click', () => {
            openWorkerModal(card.dataset.id);
        });
    });
}

// ===== Create Worker Card =====
function createWorkerCard(worker) {
    const icon = skillIcons[worker.skill] || '👷';
    const rating = worker.averageRating ? worker.averageRating.toFixed(1) : 'New';
    const ratingStars = worker.averageRating ? '★' : '✨';

    return `
        <div class="worker-card" data-id="${worker.id}">
            <div class="worker-header">
                <div class="worker-avatar">${icon}</div>
                <div class="worker-info">
                    <h3 class="worker-name">${worker.workerName}</h3>
                    <span class="worker-skill">${formatSkill(worker.skill)}</span>
                </div>
            </div>
            <p class="worker-description">${worker.description || 'Experienced professional ready to help you.'}</p>
            <div class="worker-footer">
                <div class="worker-rate">
                    ${worker.hourlyRate}tk <span>/hr</span>
                </div>
                <div class="worker-rating">
                    <span class="star">${ratingStars}</span>
                    ${rating}
                </div>
            </div>
        </div>
    `;
}

// ===== Worker Modal =====
async function openWorkerModal(workerId) {
    try {
        const response = await fetch(`${API_BASE}/workers/${workerId}`);
        const worker = await response.json();

        const icon = skillIcons[worker.skill] || '👷';
        const rating = worker.averageRating ? worker.averageRating.toFixed(1) : 'No ratings yet';

        let reviewsHtml = '';
        if (worker.reviews && worker.reviews.length > 0) {
            reviewsHtml = worker.reviews.map(review => `
                <div class="review-card">
                    <div class="review-header">
                        <span class="reviewer-name">${review.reviewerName}</span>
                        <span class="review-rating">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
                    </div>
                    <p class="review-comment">${review.comment || 'Great service!'}</p>
                </div>
            `).join('');
        } else {
            reviewsHtml = `
                <div class="no-reviews">
                    <p>No reviews yet. Be the first to leave a review!</p>
                </div>
            `;
        }

        modalBody.innerHTML = `
            <div class="worker-detail-header">
                <div class="worker-detail-avatar">${icon}</div>
                <div class="worker-detail-info">
                    <h2>${worker.workerName}</h2>
                    <span class="worker-skill">${formatSkill(worker.skill)}</span>
                    <div class="worker-detail-meta">
                        <span class="meta-item">
                            💰 <strong>${worker.hourlyRate}tk</strong>/hr
                        </span>
                        <span class="meta-item">
                            ⭐ ${rating}
                        </span>
                        <span class="meta-item">
                            📝 ${worker.reviews ? worker.reviews.length : 0} reviews
                        </span>
                    </div>
                </div>
            </div>
            <div class="worker-detail-description">
                ${worker.description || 'Experienced professional ready to help you with your needs.'}
            </div>
            <div class="reviews-section">
                <h3>
                    Customer Reviews
                    <button class="btn btn-primary add-review-btn" onclick="openReviewModal(${worker.id})">
                        ⭐ Add Review
                    </button>
                </h3>
                ${reviewsHtml}
            </div>
        `;

        workerModal.classList.add('active');
        document.body.style.overflow = 'hidden';

    } catch (error) {
        console.error('Error loading worker:', error);
        showToast('Failed to load worker details', 'error');
    }
}

function closeWorkerModal() {
    workerModal.classList.remove('active');
    document.body.style.overflow = '';
}

// ===== Auth Modal =====
function openAuthModal(type = 'login') {
    authModal.classList.add('active');
    document.body.style.overflow = 'hidden';

    if (type === 'signup' || type === 'signup-worker') {
        switchAuthForm('signup');
        if (type === 'signup-worker') {
            setTimeout(() => selectRole('WORKER'), 100);
        }
    } else {
        switchAuthForm('login');
    }
}

function closeAuthModal() {
    authModal.classList.remove('active');
    document.body.style.overflow = '';
}

function switchAuthForm(type) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (type === 'login') {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
    }
}

function selectRole(role) {
    document.getElementById('signup-role').value = role;

    // Update toggle buttons (supports both old and new class names)
    document.querySelectorAll('.role-btn, .role-toggle-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.role === role);
    });

    const workerFields = document.getElementById('worker-fields');
    if (workerFields) {
        workerFields.style.display = role === 'WORKER' ? 'block' : 'none';
    }
}

// ===== Auth Handlers =====
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data;
            localStorage.setItem('shobkaj_user', JSON.stringify(data));
            updateNavForLoggedInUser();
            closeAuthModal();
            showToast(`Welcome back, ${data.username}!`, 'success');
            loadWorkers(); // Refresh
        } else {
            showToast(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    }
}

async function handleSignup(e) {
    e.preventDefault();

    const username = document.getElementById('signup-username').value.trim();
    const email = document.getElementById('signup-email')?.value.trim() || '';
    const password = document.getElementById('signup-password').value;
    const role = document.getElementById('signup-role').value;

    const requestBody = { username, email, password, role };

    if (role === 'WORKER') {
        requestBody.skill = document.getElementById('signup-skill').value;
        requestBody.hourlyRate = parseFloat(document.getElementById('signup-rate').value) || 200;
        requestBody.description = document.getElementById('signup-description').value.trim();
    }

    try {
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data;
            localStorage.setItem('shobkaj_user', JSON.stringify(data));
            updateNavForLoggedInUser();
            closeAuthModal();
            showToast(`Welcome to ShobKaj, ${data.username}! 🎉`, 'success');
            loadWorkers(); // Refresh to show new worker
        } else {
            showToast(data.message || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showToast('Registration failed. Please try again.', 'error');
    }
}

function handleLogout() {
    currentUser = null;
    localStorage.removeItem('shobkaj_user');
    updateNavForLoggedOutUser();
    showToast('You have been logged out', 'success');
}

// ===== Review Modal =====
function openReviewModal(workerId) {
    document.getElementById('review-worker-id').value = workerId;
    document.getElementById('reviewer-name').value = currentUser ? currentUser.username : '';
    document.getElementById('review-comment').value = '';
    document.getElementById('review-rating').value = '5';
    updateStarRating(5);

    workerModal.classList.remove('active');
    reviewModal.classList.add('active');
}

function closeReviewModal() {
    reviewModal.classList.remove('active');
    document.body.style.overflow = '';
}

function updateStarRating(rating) {
    document.querySelectorAll('#star-rating .star').forEach((star, index) => {
        star.classList.toggle('active', index < rating);
    });
    document.getElementById('review-rating').value = rating;
}

async function submitReview(e) {
    e.preventDefault();

    const workerId = document.getElementById('review-worker-id').value;
    const reviewerName = document.getElementById('reviewer-name').value.trim();
    const rating = parseInt(document.getElementById('review-rating').value);
    const comment = document.getElementById('review-comment').value.trim();

    if (!reviewerName) {
        showToast('Please enter your name', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/reviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                workerProfileId: parseInt(workerId),
                rating,
                comment: comment || 'Great service!',
                reviewerName
            })
        });

        if (response.ok) {
            closeReviewModal();
            showToast('Review submitted successfully! ⭐', 'success');
            await loadWorkers();
            setTimeout(() => openWorkerModal(workerId), 300);
        } else {
            const error = await response.json();
            showToast(error.message || 'Failed to submit review', 'error');
        }
    } catch (error) {
        console.error('Review error:', error);
        showToast('Failed to submit review', 'error');
    }
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Category cards - redirect to workers page with filter
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', () => {
            const skill = card.dataset.skill;
            // Redirect to workers page with skill parameter
            window.location.href = `/workers.html?skill=${skill}`;
        });
    });

    // Modal overlays
    document.querySelector('#auth-modal .modal-overlay').addEventListener('click', closeAuthModal);
    document.querySelector('#worker-modal .modal-overlay').addEventListener('click', closeWorkerModal);
    document.querySelector('#review-modal .modal-overlay').addEventListener('click', closeReviewModal);

    // Star rating
    document.querySelectorAll('#star-rating .star').forEach(star => {
        star.addEventListener('click', () => {
            updateStarRating(parseInt(star.dataset.rating));
        });
    });

    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
            closeWorkerModal();
            closeReviewModal();
        }
    });
}

function setupScrollEffects() {
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ===== Utilities =====
function formatSkill(skill) {
    return skill.charAt(0) + skill.slice(1).toLowerCase();
}

function showToast(message, type = 'success') {
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    toastMessage.textContent = message;
    toastIcon.textContent = type === 'success' ? '✓' : '✕';
    toast.className = 'toast show ' + type;

    setTimeout(() => {
        toast.className = 'toast';
    }, 3500);
}

function toggleMobileMenu() {
    // TODO: Implement mobile menu
}

function toggleUserMenu() {
    // TODO: Implement user dropdown menu
}

// Make functions available globally
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthForm = switchAuthForm;
window.selectRole = selectRole;
window.handleLogin = handleLogin;
window.handleSignup = handleSignup;
window.handleLogout = handleLogout;
window.openReviewModal = openReviewModal;
window.closeReviewModal = closeReviewModal;
window.submitReview = submitReview;
window.filterWorkers = filterWorkers;
window.closeWorkerModal = closeWorkerModal;
window.toggleMobileMenu = toggleMobileMenu;
window.toggleUserMenu = toggleUserMenu;
