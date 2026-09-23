/**
 * UrbanValuate - Global Client Logic & Ultra-Max Theme Manager
 * Controls 5 luxury themes, mobile nav toggle, floating theme dock,
 * navbar dropdown, active link states, home contact form, and toast messaging.
 */

document.addEventListener('DOMContentLoaded', () => {
    initLuxuryThemes();
    initMobileNav();
    initHomeContactForm();
    highlightActiveNavLink();
});

// 5 Ultra-Max Themes Metadata
const LUXURY_THEMES = {
    'obsidian-gold': {
        name: 'Royal Obsidian & 24K Gold',
        shortName: 'Obsidian Gold',
        icon: '👑',
        badge: 'Penthouse Dark'
    },
    'champagne-light': {
        name: 'Champagne Pearl (Sotheby’s Ivory)',
        shortName: 'Champagne Pearl',
        icon: '🏛️',
        badge: 'Executive Light'
    },
    'sapphire-marina': {
        name: 'Sapphire Marina (Monaco Blue)',
        shortName: 'Sapphire Marina',
        icon: '💎',
        badge: 'Oceanic Navy'
    },
    'emerald-royale': {
        name: 'Emerald Royale (Bel Air Botanical)',
        shortName: 'Emerald Royale',
        icon: '🌿',
        badge: 'Estate Green'
    },
    'midnight-amethyst': {
        name: 'Midnight Amethyst (Dubai Cyber Luxe)',
        shortName: 'Midnight Amethyst',
        icon: '🔮',
        badge: 'Skyline Violet'
    }
};

function initLuxuryThemes() {
    const savedTheme = localStorage.getItem('hp_luxury_theme') || 'obsidian-gold';
    applyTheme(savedTheme, false);

    // Navbar Dropdown Toggle
    const themeMenuBtn = document.getElementById('themeMenuBtn');
    const themeDropdownMenu = document.getElementById('themeDropdownMenu');

    if (themeMenuBtn && themeDropdownMenu) {
        themeMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = themeDropdownMenu.classList.contains('show');
            themeDropdownMenu.classList.toggle('show', !isOpen);
            themeMenuBtn.setAttribute('aria-expanded', !isOpen);
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!themeDropdownMenu.contains(e.target) && !themeMenuBtn.contains(e.target)) {
                themeDropdownMenu.classList.remove('show');
                themeMenuBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Dropdown Option Buttons
    const themeOptions = document.querySelectorAll('.theme-opt');
    themeOptions.forEach(opt => {
        opt.addEventListener('click', (e) => {
            const chosen = opt.getAttribute('data-theme');
            if (chosen) {
                applyTheme(chosen, true);
                if (themeDropdownMenu) themeDropdownMenu.classList.remove('show');
                if (themeMenuBtn) themeMenuBtn.setAttribute('aria-expanded', 'false');
            }
        });
    });

    // Floating Theme Dock Swatch Buttons
    const dockButtons = document.querySelectorAll('.dock-swatch-btn');
    dockButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const chosen = btn.getAttribute('data-theme');
            if (chosen) {
                applyTheme(chosen, true);
            }
        });
    });
}

function applyTheme(themeKey, notify = false) {
    if (!LUXURY_THEMES[themeKey]) themeKey = 'obsidian-gold';

    // Apply to DOM & LocalStorage
    document.documentElement.setAttribute('data-theme', themeKey);
    localStorage.setItem('hp_luxury_theme', themeKey);

    const themeInfo = LUXURY_THEMES[themeKey];

    // Update Navbar Button Label & Icon
    const activeIcon = document.getElementById('activeThemeIcon');
    const activeLabel = document.getElementById('activeThemeLabel');
    if (activeIcon) activeIcon.textContent = themeInfo.icon;
    if (activeLabel) activeLabel.textContent = themeInfo.shortName || themeInfo.name.split(' (')[0];

    // Update active state in dropdown
    document.querySelectorAll('.theme-opt').forEach(opt => {
        const isMatch = opt.getAttribute('data-theme') === themeKey;
        opt.classList.toggle('active', isMatch);
    });

    // Update active state in floating dock
    document.querySelectorAll('.dock-swatch-btn').forEach(btn => {
        const isMatch = btn.getAttribute('data-theme') === themeKey;
        btn.classList.toggle('active', isMatch);
    });

    // Dispatch global event for Chart.js and components
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: themeKey, info: themeInfo } }));

    if (notify) {
        showToast(`Theme transformed to ${themeInfo.icon} ${themeInfo.name}`, 'gold');
    }
}

// Mobile Navbar Hamburger Toggle
function initMobileNav() {
    const toggleBtn = document.getElementById('navToggleBtn');
    const navMenu = document.getElementById('navMenu');

    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            navMenu.classList.toggle('show');
            const isOpen = navMenu.classList.contains('show');
            toggleBtn.innerHTML = isOpen ? '<i class="bi bi-x-lg"></i>' : '<i class="bi bi-list"></i>';
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
                navMenu.classList.remove('show');
                toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
            }
        });

        // Close when clicking any nav link
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('show');
                toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
            });
        });
    }
}

// Home Page Quick Customer Support Inquiry Form
function initHomeContactForm() {
    const homeForm = document.getElementById('homeContactForm');
    const submitBtn = document.getElementById('homeContactBtn');
    const successCard = document.getElementById('homeContactSuccess');
    const successMsg = document.getElementById('homeContactSuccessMsg');

    if (homeForm) {
        homeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const originalHtml = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Dispatching...';

            const payload = {
                name: document.getElementById('homeName').value.trim(),
                email: document.getElementById('homeEmail').value.trim(),
                phone: document.getElementById('homePhone')?.value.trim() || '',
                message: document.getElementById('homeMsg').value.trim(),
                category: 'General Support & Valuation Inquiry',
                corridor: 'Tech Park Cyber City'
            };

            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const res = await response.json();

                if (res.success) {
                    homeForm.reset();
                    if (successCard) {
                        successCard.style.display = 'block';
                        if (successMsg) {
                            successMsg.innerHTML = `Thank you <strong>${res.details.name}</strong>. Inquiry registered under docket <strong>${res.docket_id}</strong>. Our advisory desk will reach out within 15 minutes.`;
                        }
                    }
                    showToast(`Inquiry dispatched! Docket: ${res.docket_id}`, 'success');
                } else {
                    showToast(res.error || 'Failed to submit inquiry', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Unable to connect to advisory desk.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalHtml;
            }
        });
    }
}

// Active Nav Link highlighting
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Global Toast Notification Helper
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const borderStyles = {
        gold: '1px solid rgba(245, 158, 11, 0.5)',
        success: '1px solid rgba(16, 185, 129, 0.5)',
        error: '1px solid rgba(239, 68, 68, 0.5)',
        info: '1px solid rgba(99, 102, 241, 0.5)'
    };
    
    toast.style.cssText = `
        background: rgba(10, 16, 32, 0.95);
        color: #f8fafc;
        border: ${borderStyles[type] || borderStyles.info};
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(245, 158, 11, 0.2);
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: fadeIn 0.3s ease;
        min-width: 260px;
        backdrop-filter: blur(16px);
        pointer-events: auto;
    `;
    
    toast.innerHTML = `<span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
