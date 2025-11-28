// ===== Mobile Menu Toggle =====
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });
}

// ===== Smooth Scrolling for Navigation Links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href !== '') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                const headerOffset = 70;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    mobileMenuBtn.classList.remove('active');
                }
            }
        }
    });
});

// ===== Navbar Scroll Effect =====
let lastScroll = 0;
const nav = document.querySelector('.nav');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    // Add shadow on scroll
    if (currentScroll > 0) {
        nav.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    } else {
        nav.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
});

// ===== Intersection Observer for Fade-in Animations =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe all sections and cards
document.querySelectorAll('.section, .feature-card, .stat-item').forEach(el => {
    observer.observe(el);
});

// ===== Counter Animation for Stats =====
const animateCounter = (element, target, duration = 2000) => {
    let current = 0;
    const increment = target / (duration / 16);
    const isDecimal = target % 1 !== 0;
    
    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = isDecimal ? current.toFixed(1) : Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };
    
    updateCounter();
};

// Animate counters when they come into view
const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
            entry.target.classList.add('counted');
            const numberElement = entry.target.querySelector('.stat-number');
            const text = numberElement.textContent;
            const number = parseFloat(text.replace(/[^0-9.]/g, ''));
            
            if (!isNaN(number)) {
                numberElement.textContent = '0';
                setTimeout(() => {
                    animateCounter(numberElement, number);
                }, 200);
            }
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-item').forEach(stat => {
    statObserver.observe(stat);
});

// ===== Form Handling (if you add forms later) =====
const handleFormSubmit = (formId, callback) => {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            callback(data);
        });
    }
};

// ===== Utility: Debounce Function =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== Performance: Lazy Loading Images =====
if ('loading' in HTMLImageElement.prototype) {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
        img.src = img.dataset.src;
    });
} else {
    // Fallback for browsers that don't support lazy loading
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
    document.body.appendChild(script);
}

// ===== Add Mobile Menu Styles Dynamically =====
const style = document.createElement('style');
style.textContent = `
    @media (max-width: 768px) {
        .nav-links.active {
            display: flex;
            flex-direction: column;
            position: absolute;
            top: 70px;
            left: 0;
            right: 0;
            background-color: white;
            padding: 2rem;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            gap: 1.5rem;
        }
        
        .mobile-menu-btn.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .mobile-menu-btn.active span:nth-child(2) {
            opacity: 0;
        }
        
        .mobile-menu-btn.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    }
`;
document.head.appendChild(style);

// ===== Dynamic Date for Blog =====
const updateCurrentDate = () => {
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        const today = new Date().toLocaleDateString('en-US', options);
        dateElement.textContent = today;
    }
};

updateCurrentDate();

// ===== Newsletter Form Handling =====
const newsletterForm = document.getElementById('newsletterForm');
if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const emailInput = newsletterForm.querySelector('input[type="email"]');
        const email = emailInput.value;
        
        // Simulate submission (replace with actual API call)
        const button = newsletterForm.querySelector('button');
        const originalText = button.textContent;
        button.textContent = 'Subscribing...';
        button.disabled = true;
        
        setTimeout(() => {
            button.textContent = '✓ Subscribed!';
            button.style.backgroundColor = '#38ef7d';
            emailInput.value = '';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
                button.style.backgroundColor = '';
            }, 3000);
        }, 1500);
        
        console.log('Newsletter subscription for:', email);
    });
}

// ===== Smooth Scroll with Offset for Blog Headers =====
const scrollToElement = (target) => {
    const headerOffset = 70;
    const elementPosition = target.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
};

// ===== Theme Toggle =====
const themeToggle = {
    init() {
        this.buttons = document.querySelectorAll('[data-theme-option]');
        this.currentTheme = localStorage.getItem('theme') || 'auto';
        
        // Set initial theme
        this.applyTheme(this.currentTheme);
        this.updateActiveButton(this.currentTheme);
        
        // Add click handlers
        this.buttons.forEach(button => {
            button.addEventListener('click', () => {
                const theme = button.dataset.themeOption;
                this.setTheme(theme);
            });
        });
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
                if (this.currentTheme === 'auto') {
                    this.applyTheme('auto');
                }
            });
        }
    },
    
    setTheme(theme) {
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        this.applyTheme(theme);
        this.updateActiveButton(theme);
    },
    
    applyTheme(theme) {
        let actualTheme = theme;
        
        if (theme === 'auto') {
            // Use system preference
            actualTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches 
                ? 'dark' 
                : 'light';
        }
        
        document.documentElement.setAttribute('data-theme', actualTheme);
    },
    
    updateActiveButton(theme) {
        this.buttons.forEach(button => {
            button.classList.toggle('active', button.dataset.themeOption === theme);
        });
    }
};

// Initialize theme toggle on page load
themeToggle.init();

// ===== Dynamic Content Loading from JSON =====
const ContentLoader = {
    async init() {
        // Only run on homepage (index.html)
        if (!document.querySelector('.hero-blog')) return;
        
        try {
            const data = await this.loadLatestContent();
            
            if (!data) {
                console.log('No dynamic content available, using static content');
                // Still set today's date even if JSON doesn't load
                this.updateDate(null);
                return;
            }
            
            console.log('%c📡 Loading dynamic content...', 'color: #0066ff; font-weight: bold;');
            
            // Always update date first
            this.updateDate(data.date);
            
            if (data.hero) {
                this.updateHero(data.hero);
            }
            
            if (data.headlines && data.headlines.length > 0) {
                this.updateHeadlines(data.headlines);
            }
            
            // Show "Show Me More" button if there are runners-up articles
            if (data.runners_up && data.runners_up.length > 0) {
                this.showMoreButton(data.runners_up.length);
            }
            
            console.log('%c✓ Dynamic content loaded successfully!', 'color: #38ef7d; font-weight: bold;');
            
        } catch (error) {
            console.error('Failed to load content:', error);
            // Still set today's date on error
            this.updateDate(null);
        }
    },
    
    showMoreButton(count) {
        const btn = document.getElementById('show-more-btn');
        const countBadge = document.getElementById('more-count');
        
        if (btn && countBadge) {
            countBadge.textContent = `${count} more`;
            btn.style.display = 'inline-flex';
        }
    },
    
    async loadLatestContent() {
        try {
            const response = await fetch('content/latest.json');
            if (!response.ok) {
                console.log('No dynamic content found, using static content');
                return null;
            }
            
            const data = await response.json();
            console.log('✓ Loaded dynamic content:', data);
            
            return data;
        } catch (error) {
            console.log('Using static content (dynamic loading disabled)');
            return null;
        }
    },
    
    updateHeroSection(hero) {
        if (!hero) return;
        
        const heroTitle = document.querySelector('.hero-title');
        const heroSubtitle = document.querySelector('.hero-subtitle');
        const categoryTag = document.querySelector('.category-tag');
        const readTime = document.querySelector('.read-time');
        const heroLink = document.querySelector('.hero-actions .btn-primary');
        
        if (heroTitle) {
            // Check if there's a gradient-text span
            const gradientText = heroTitle.querySelector('.gradient-text');
            if (gradientText) {
                // Split title into two parts (simple split on ":")
                const titleParts = hero.title.split(':');
                if (titleParts.length > 1) {
                    heroTitle.innerHTML = `${titleParts[0]}:<span class="gradient-text">${titleParts[1]}</span>`;
                } else {
                    heroTitle.innerHTML = `<span class="gradient-text">${hero.title}</span>`;
                }
            } else {
                heroTitle.textContent = hero.title;
            }
        }
        
        if (heroSubtitle) heroSubtitle.textContent = hero.subtitle;
        if (categoryTag) categoryTag.textContent = hero.category;
        if (readTime) readTime.textContent = hero.read_time;
        if (heroLink) heroLink.href = hero.url;
    },
    
    updateHeadlines(headlines) {
        if (!headlines || headlines.length === 0) return;
        
        const articlesGrid = document.querySelector('.articles-grid');
        if (!articlesGrid) return;
        
        // Clear existing static content
        articlesGrid.innerHTML = '';
        
        // Create article cards dynamically
        headlines.forEach((article, index) => {
            const articleCard = document.createElement('article');
            articleCard.className = index === 0 ? 'article-card featured' : 'article-card';
            
            articleCard.innerHTML = `
                <div class="article-image">
                    ${article.image_url 
                        ? `<img src="${article.image_url}" alt="${article.title}" onerror="this.parentElement.innerHTML='<div class=\\'image-placeholder\\' style=\\'background: linear-gradient(135deg, ${this.getGradientColors(index)});\\' ><span>${article.category}</span></div>';">` 
                        : `<div class="image-placeholder" style="background: linear-gradient(135deg, ${this.getGradientColors(index)});">
                            <span>${article.category}</span>
                        </div>`
                    }
                </div>
                <div class="article-content">
                    <div class="article-meta">
                        <span class="category">${article.category}</span>
                        <span class="time">${this.getTimeAgo(article.published)}</span>
                    </div>
                    <h3 class="article-title">
                        <a href="${article.url}" target="_blank">${article.title}</a>
                    </h3>
                    <p class="article-excerpt">
                        ${article.excerpt}
                    </p>
                    <div class="article-footer">
                        <span class="author-small">${article.source}</span>
                        <span class="read-time-small">${article.read_time}</span>
                    </div>
                    <div class="article-rating" data-url="${article.url}" data-category="${article.category}" data-score="${article.score}">
                        <button class="rating-btn rating-up" data-rating="up" title="I want more like this">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                            </svg>
                        </button>
                        <button class="rating-btn rating-down" data-rating="down" title="I want less like this">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
            
            articlesGrid.appendChild(articleCard);
        });
        
        // Initialize rating handlers
        this.initializeRatingHandlers();
        
        console.log(`✓ ${headlines.length} headline articles loaded and rendered`);
    },
    
    initializeRatingHandlers() {
        document.querySelectorAll('.rating-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const ratingContainer = btn.closest('.article-rating');
                const url = ratingContainer.dataset.url;
                const category = ratingContainer.dataset.category;
                const score = parseFloat(ratingContainer.dataset.score);
                const rating = btn.dataset.rating;
                
                // Check current state
                const currentRating = this.getCurrentRating(url);
                
                if (currentRating) {
                    // Already rated
                    if (currentRating.rating === rating) {
                        // Clicking same button - undo/unrate
                        this.removeRating(url);
                        ratingContainer.classList.remove(`rated-${rating}`);
                        btn.classList.remove('active');
                        this.showRatingFeedback('undo');
                        return;
                    } else {
                        // Clicking opposite button - switch rating
                        this.removeRating(url);
                        ratingContainer.classList.remove(`rated-${currentRating.rating}`);
                        ratingContainer.querySelector(`[data-rating="${currentRating.rating}"]`).classList.remove('active');
                    }
                }
                
                // Show reason picker modal
                this.showReasonPicker(url, category, score, rating, ratingContainer, btn);
            });
        });
        
        // Restore previous ratings
        this.restoreRatings();
    },
    
    getCurrentRating(url) {
        const ratings = this.getRatings();
        return ratings.find(r => r.url === url);
    },
    
    removeRating(url) {
        const ratings = this.getRatings();
        const filtered = ratings.filter(r => r.url !== url);
        localStorage.setItem('techpulse_ratings', JSON.stringify(filtered));
    },
    
    showReasonPicker(url, category, score, rating, container, btn) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'reason-modal';
        modal.innerHTML = `
            <div class="reason-modal-content">
                <h3>Why did you ${rating === 'up' ? 'like' : 'dislike'} this article?</h3>
                <p class="reason-subtitle">Select all that apply:</p>
                <div class="reason-options">
                    ${this.getReasonOptions(rating).map(reason => `
                        <label class="reason-option">
                            <input type="checkbox" value="${reason.value}">
                            <span>${reason.icon} ${reason.label}</span>
                        </label>
                    `).join('')}
                </div>
                <div class="reason-actions">
                    <button class="reason-skip" onclick="ContentLoader.skipReasons('${url}', '${category}', ${score}, '${rating}', this)">Skip</button>
                    <button class="reason-submit" onclick="ContentLoader.submitReasons('${url}', '${category}', ${score}, '${rating}', this)">Submit</button>
                </div>
            </div>
        `;
        
        // Store references for later
        modal.dataset.container = container;
        modal.dataset.btn = btn;
        
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeReasonModal(modal);
            }
        });
    },
    
    getReasonOptions(rating) {
        if (rating === 'up') {
            return [
                { value: 'content_quality', label: 'High-quality content', icon: '⭐' },
                { value: 'relevant_topic', label: 'Highly relevant topic', icon: '🎯' },
                { value: 'trusted_source', label: 'Trusted source', icon: '✓' },
                { value: 'actionable', label: 'Actionable insights', icon: '💡' },
                { value: 'timely', label: 'Timely/breaking news', icon: '⚡' },
                { value: 'technical_depth', label: 'Good technical depth', icon: '🔬' },
                { value: 'business_impact', label: 'Clear business impact', icon: '💼' },
                { value: 'unique_perspective', label: 'Unique perspective', icon: '🌟' }
            ];
        } else {
            return [
                { value: 'not_relevant', label: 'Not relevant to me', icon: '❌' },
                { value: 'low_quality', label: 'Low quality/clickbait', icon: '👎' },
                { value: 'too_basic', label: 'Too basic/obvious', icon: '😴' },
                { value: 'too_technical', label: 'Too technical/complex', icon: '🤯' },
                { value: 'outdated', label: 'Outdated information', icon: '📅' },
                { value: 'untrusted_source', label: 'Don\'t trust source', icon: '⚠️' },
                { value: 'too_long', label: 'Too long/verbose', icon: '📚' },
                { value: 'duplicate', label: 'Already seen this', icon: '🔄' }
            ];
        }
    },
    
    submitReasons(url, category, score, rating, btnElement) {
        const modal = btnElement.closest('.reason-modal');
        const checkboxes = modal.querySelectorAll('input[type="checkbox"]:checked');
        const reasons = Array.from(checkboxes).map(cb => cb.value);
        
        this.finalizeRating(url, category, score, rating, reasons, modal);
    },
    
    skipReasons(url, category, score, rating, btnElement) {
        const modal = btnElement.closest('.reason-modal');
        this.finalizeRating(url, category, score, rating, [], modal);
    },
    
    finalizeRating(url, category, score, rating, reasons, modal) {
        // Save rating with reasons
        this.saveRating(url, category, score, rating, reasons);
        
        // Get container and button from modal dataset (stored earlier)
        const containers = document.querySelectorAll(`[data-url="${url}"]`);
        containers.forEach(container => {
            container.classList.add(`rated-${rating}`);
            const btn = container.querySelector(`[data-rating="${rating}"]`);
            if (btn) btn.classList.add('active');
        });
        
        // Close modal
        this.closeReasonModal(modal);
        
        // Show feedback
        this.showRatingFeedback(rating);
    },
    
    closeReasonModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    },
    
    saveRating(url, category, score, rating, reasons = []) {
        const ratings = this.getRatings();
        
        ratings.push({
            url: url,
            category: category,
            score: score,
            rating: rating,
            reasons: reasons,
            timestamp: new Date().toISOString()
        });
        
        localStorage.setItem('techpulse_ratings', JSON.stringify(ratings));
        
        const reasonText = reasons.length > 0 ? ` (${reasons.length} reasons)` : '';
        console.log(`✓ Saved ${rating} rating for article in category: ${category}${reasonText}`);
    },
    
    getRatings() {
        const stored = localStorage.getItem('techpulse_ratings');
        return stored ? JSON.parse(stored) : [];
    },
    
    restoreRatings() {
        const ratings = this.getRatings();
        
        ratings.forEach(rating => {
            const container = document.querySelector(`[data-url="${rating.url}"]`);
            if (container) {
                container.classList.add(`rated-${rating.rating}`);
                const btn = container.querySelector(`[data-rating="${rating.rating}"]`);
                if (btn) btn.classList.add('active');
                // Don't disable - allow toggling/switching
            }
        });
    },
    
    showRatingFeedback(rating) {
        const messages = {
            'up': '👍 Got it! We\'ll show more like this',
            'down': '👎 Noted! We\'ll show less like this',
            'undo': '↩️ Rating removed'
        };
        
        const message = messages[rating] || messages['up'];
        
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'rating-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    },
    
    getGradientColors(index) {
        const gradients = [
            '#4F46E5 0%, #06B6D4 100%',
            '#EC4899 0%, #8B5CF6 100%',
            '#10B981 0%, #3B82F6 100%',
            '#F59E0B 0%, #EF4444 100%',
            '#8B5CF6 0%, #EC4899 100%',
            '#06B6D4 0%, #10B981 100%'
        ];
        return gradients[index % gradients.length];
    },
    
    getTimeAgo(publishedDate) {
        if (!publishedDate) return 'Recently';
        
        const now = new Date();
        const published = new Date(publishedDate);
        const diffMs = now - published;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return published.toLocaleDateString();
    },
    
    updateDate(dateStr) {
        const dateElement = document.getElementById('currentDate');
        if (dateElement) {
            if (dateStr) {
                dateElement.textContent = dateStr;
            } else {
                // Fallback to today's date if no date provided
                const today = new Date();
                const options = { year: 'numeric', month: 'long', day: 'numeric' };
                dateElement.textContent = today.toLocaleDateString('en-US', options);
            }
        }
    }
};

// Initialize dynamic content loading
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ContentLoader.init());
} else {
    ContentLoader.init();
}

// ===== Console Message =====
console.log('%c📰 TechPulse Blog Loaded Successfully!', 'color: #0066ff; font-size: 16px; font-weight: bold;');
console.log('%cBuilt with modern web standards', 'color: #666; font-size: 12px;');
