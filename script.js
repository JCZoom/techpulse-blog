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

// ===== Console Message =====
console.log('%c📰 TechPulse Blog Loaded Successfully!', 'color: #0066ff; font-size: 16px; font-weight: bold;');
console.log('%cBuilt with modern web standards', 'color: #666; font-size: 12px;');
