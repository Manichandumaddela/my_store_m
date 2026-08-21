document.addEventListener('DOMContentLoaded', function () {
    // ===== HAMBURGER MENU =====
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');

    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function () {
            this.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // ===== DYNAMIC CLICK SOUNDS =====
    document.addEventListener('click', function(e) {
        try {
            // Check if click was on an actionable element
            const actionable = e.target.closest('button, a, .btn, .qty-btn, .hamburger');
            if (!actionable) return; // Don't play sound on random text/background clicks
            
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            // Use a shared context to avoid creating too many and hitting limits
            if (!window.globalAudioCtx) {
                window.globalAudioCtx = new AudioContext();
            }
            const audioCtx = window.globalAudioCtx;
            
            // Resume context if suspended (browser autoplay policy)
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            // Determine sound profile based on element
            let startFreq = 600;
            let endFreq = 100;
            let oscType = 'sine';
            let duration = 0.05;
            let maxVol = 0.2;

            if (actionable.classList.contains('btn-danger') || actionable.classList.contains('delete')) {
                // Warning/Delete sound (lower, harsher)
                startFreq = 300;
                endFreq = 50;
                oscType = 'sawtooth';
                duration = 0.1;
                maxVol = 0.15;
            } else if (actionable.classList.contains('btn-success') || actionable.classList.contains('btn-primary')) {
                // Success/Primary sound (higher, rising)
                startFreq = 600;
                endFreq = 1200;
                oscType = 'sine';
                duration = 0.08;
                maxVol = 0.15;
            } else {
                // Default click sound
                startFreq = 600;
                endFreq = 100;
                oscType = 'sine';
                duration = 0.05;
                maxVol = 0.1;
            }

            oscillator.type = oscType;
            oscillator.frequency.setValueAtTime(startFreq, audioCtx.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(endFreq, audioCtx.currentTime + duration);
            
            gainNode.gain.setValueAtTime(maxVol, audioCtx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
            
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + duration);
        } catch (err) {
            console.error('Audio playback failed', err);
        }
    });

    // ===== AUTO-HIDE MESSAGES =====
    const messages = document.querySelectorAll('.message');
    messages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            message.style.transform = 'translateX(50px)';
            setTimeout(function () {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // ===== SCROLL ANIMATIONS =====
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animateElements.forEach(function (element) {
        observer.observe(element);
    });

    // ===== QUANTITY BUTTONS =====
    const qtyBtns = document.querySelectorAll('.qty-btn');
    qtyBtns.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            this.style.transform = 'scale(0.85)';
            setTimeout(function () {
                btn.style.transform = 'scale(1)';
            }, 200);
        });
    });

    // ===== SOUND EFFECT UTILITY =====
    function playAddToCartSound() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            
            // Create oscillators for a nice "ding" sound
            const osc = ctx.createOscillator();
            const osc2 = ctx.createOscillator();
            const gainNode = ctx.createGain();
            
            osc.type = 'sine';
            osc2.type = 'triangle';
            
            // Frequencies for a pleasant chime
            osc.frequency.setValueAtTime(880, ctx.currentTime); // A5
            osc.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.1); // A6
            
            osc2.frequency.setValueAtTime(880, ctx.currentTime);
            osc2.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.1);
            
            // Envelope
            gainNode.gain.setValueAtTime(0, ctx.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.02);
            gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
            
            osc.connect(gainNode);
            osc2.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            osc.start();
            osc2.start();
            osc.stop(ctx.currentTime + 0.5);
            osc2.stop(ctx.currentTime + 0.5);
        } catch (e) {
            console.error("Audio playback failed", e);
        }
    }

    // ===== ADD TO CART ANIMATION & SOUND =====
    const addToCartBtns = document.querySelectorAll('.btn-primary .fa-cart-plus, .btn-add-cart');
    addToCartBtns.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            playAddToCartSound();
            const parentBtn = this.closest('.btn');
            if (parentBtn && !parentBtn.classList.contains('btn-disabled')) {
                parentBtn.classList.add('btn-loading');
                setTimeout(function () {
                    parentBtn.classList.remove('btn-loading');
                }, 600);
            }
        });
    });

    // ===== PRICE FORMATTING (Rupee) =====
    function formatPrice(price) {
        return '₹' + parseFloat(price).toFixed(2);
    }

    // ===== UPDATE CART COUNT =====
    function updateCartCount(count) {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = count;
            if (count == 0) {
                badge.style.display = 'none';
            } else {
                badge.style.display = 'inline-block';
            }
        }
    }

    // ===== IMAGE LAZY LOADING =====
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(function (img) {
        imageObserver.observe(img);
    });

    // ===== CONFIRM DELETE =====
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});

// ===== GLOBAL HELPER FUNCTIONS =====
function formatRupee(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}