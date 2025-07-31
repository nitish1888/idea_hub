// Red Hat Idea Hub - Main JavaScript File
// =====================================

// Global configuration
const APP_CONFIG = {
    API_BASE_URL: window.location.origin,
    DEBOUNCE_DELAY: 300,
    ANIMATION_DURATION: 300
};

// Utility Functions
// =================

// Debounce function for input handling
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

// Format date consistently across the app
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format file size in human readable format
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Copy text to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

// Notification System
// ===================

function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        z-index: 10000;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: 500;
        box-shadow: var(--shadow-lg);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    `;
    
    // Set background color based on type
    const colors = {
        success: 'var(--green-500)',
        error: 'var(--red-500)',
        warning: 'var(--yellow-500)',
        info: 'var(--blue-500)'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add icon and message
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-times-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="${icons[type] || icons.info}"></i>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, duration);
}

// API Helper Functions
// ====================

async function apiCall(endpoint, options = {}) {
    const url = `${APP_CONFIG.API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

// Form Validation
// ===============

function validateForm(formElement) {
    const errors = [];
    const requiredFields = formElement.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        const value = field.value.trim();
        const fieldName = field.getAttribute('data-label') || field.name || field.id;
        
        if (!value) {
            errors.push(`${fieldName} is required`);
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
        
        // Email validation
        if (field.type === 'email' && value && !isValidEmail(value)) {
            errors.push(`${fieldName} must be a valid email address`);
            field.classList.add('error');
        }
        
        // URL validation
        if (field.type === 'url' && value && !isValidUrl(value)) {
            errors.push(`${fieldName} must be a valid URL`);
            field.classList.add('error');
        }
    });
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Loading States
// ==============

function showLoadingState(element, message = 'Loading...') {
    const originalContent = element.innerHTML;
    element.setAttribute('data-original-content', originalContent);
    
    element.innerHTML = `
        <div class="loading-state" style="display: flex; align-items: center; justify-content: center; gap: 0.75rem;">
            <div class="spinner"></div>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    
    element.disabled = true;
    element.style.pointerEvents = 'none';
}

function hideLoadingState(element) {
    const originalContent = element.getAttribute('data-original-content');
    if (originalContent) {
        element.innerHTML = originalContent;
        element.removeAttribute('data-original-content');
    }
    
    element.disabled = false;
    element.style.pointerEvents = 'auto';
}

// Navigation Helpers
// ==================

function setActiveNavigation(currentPath) {
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach(button => {
        button.classList.remove('active');
        if (button.getAttribute('href') === currentPath) {
            button.classList.add('active');
        }
    });
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Search Functionality
// ====================

function initializeSearch() {
    const searchInputs = document.querySelectorAll('[data-search]');
    
    searchInputs.forEach(input => {
        const targetSelector = input.getAttribute('data-search');
        const debouncedSearch = debounce((query) => {
            performSearch(query, targetSelector);
        }, APP_CONFIG.DEBOUNCE_DELAY);
        
        input.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });
    });
}

function performSearch(query, targetSelector) {
    const items = document.querySelectorAll(targetSelector);
    const searchTerm = query.toLowerCase().trim();
    
    if (!searchTerm) {
        // Show all items when search is empty
        items.forEach(item => {
            item.style.display = '';
            item.classList.remove('search-highlight');
        });
        return;
    }
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matches = text.includes(searchTerm);
        
        item.style.display = matches ? '' : 'none';
        
        if (matches) {
            item.classList.add('search-highlight');
        } else {
            item.classList.remove('search-highlight');
        }
    });
}

// Keyboard Shortcuts
// ==================

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal:not([style*="display: none"])');
            openModals.forEach(modal => {
                const closeButton = modal.querySelector('.modal-close, [data-modal-close]');
                if (closeButton) {
                    closeButton.click();
                }
            });
        }
        
        // Enter to submit forms (when focused on submit button)
        if (e.key === 'Enter' && e.target.type === 'submit') {
            e.target.click();
        }
    });
}

// Accessibility Enhancements
// ===========================

function initializeAccessibility() {
    // Add focus indicators for keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
    
    // Add ARIA labels to buttons without text
    document.querySelectorAll('button:not([aria-label])').forEach(button => {
        if (!button.textContent.trim()) {
            const icon = button.querySelector('i[class*="fa-"]');
            if (icon) {
                const iconClass = icon.className.split(' ').find(cls => cls.startsWith('fa-'));
                const label = iconClass ? iconClass.replace('fa-', '').replace('-', ' ') : 'Button';
                button.setAttribute('aria-label', label);
            }
        }
    });
}

// Dark Mode Support (future enhancement)
// ======================================

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    showNotification(`Switched to ${newTheme} mode`, 'info');
}

// Performance Monitoring
// ======================

function initializePerformanceMonitoring() {
    // Monitor page load performance
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                
                if (loadTime > 3000) { // More than 3 seconds
                    console.warn(`Slow page load detected: ${loadTime}ms`);
                }
            }, 0);
        });
    }
    
    // Monitor API call performance
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const start = performance.now();
        const response = await originalFetch.apply(this, args);
        const duration = performance.now() - start;
        
        if (duration > 5000) { // More than 5 seconds
            console.warn(`Slow API call detected: ${args[0]} took ${duration}ms`);
        }
        
        return response;
    };
}

// Global Error Handling
// =====================

function initializeErrorHandling() {
    window.addEventListener('error', (e) => {
        console.error('Global error:', e.error);
        showNotification('An unexpected error occurred', 'error');
    });
    
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('An unexpected error occurred', 'error');
    });
}

// Main Initialization
// ===================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Red Hat Idea Hub - Initializing...');
    
    // Initialize all features
    initializeTheme();
    initializeSmoothScrolling();
    initializeSearch();
    initializeKeyboardShortcuts();
    initializeAccessibility();
    initializePerformanceMonitoring();
    initializeErrorHandling();
    
    // Set active navigation
    setActiveNavigation(window.location.pathname);
    
    console.log('✅ Red Hat Idea Hub - Ready!');
});

// Export functions for use in other scripts
window.IdeaHub = {
    showNotification,
    apiCall,
    validateForm,
    showLoadingState,
    hideLoadingState,
    formatDate,
    formatFileSize,
    copyToClipboard,
    toggleTheme
};