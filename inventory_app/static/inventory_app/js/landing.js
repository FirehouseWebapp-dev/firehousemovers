// Firehouse Movers Landing Page JavaScript

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize GSAP
    gsap.registerPlugin(ScrollTrigger);
    
    // Set current year in footer
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
    
    // Initialize all components
    initMobileMenu();
    
    // Add small delay to ensure DOM is fully loaded
    setTimeout(() => {
        initHeroAnimations();
        initPlatformStatement();
        initServicesOverview();
        initScrollAnimations();
        initFooterAnimations();
        initColorChangingSection();
        initIntersectionObservers();
    }, 100);
});

// Mobile Menu Functionality - Enhanced for navbar compatibility
function initMobileMenu() {
    // Skip mobile menu initialization since navbar.html handles it
    // This prevents conflicts with the standard navbar mobile menu
    console.log('Mobile menu handled by navbar.html');
}

// Hero Section Animations
function initHeroAnimations() {
    // truck continuous loop movement
    gsap.fromTo("#truck",
        { x: "-150px" }, // start off screen left
        { x: "110vw", duration: 10, ease: "linear", repeat: -1 } // drive fully across
    );

    // smoke container moves with truck
    gsap.fromTo("#smoke-container",
        { x: "-150px" }, // start off screen left with truck
        { x: "110vw", duration: 10, ease: "linear", repeat: -1 } // move with truck
    );

    // wheels spin
    gsap.to(["#wheel1", "#wheel2", "#wheel3"], { rotation: 360, transformOrigin: "50% 50%", repeat: -1, ease: "linear", duration: 1 });

    // suspension bounce
    gsap.to("#truck", { y: -4, yoyo: true, repeat: -1, duration: 0.8, ease: "sine.inOut" });

    // Text slides down from top immediately on page load
    gsap.fromTo("#hero-title", 
        { opacity: 0, y: -50 }, 
        { opacity: 1, y: 0, duration: 1.2, ease: "power3.out" }
    );
    
    gsap.fromTo("#hero-tagline", 
        { opacity: 0, y: -30 }, 
        { opacity: 1, y: 0, duration: 1, delay: 0.3, ease: "power3.out" }
    );

    // Hero content fade on scroll
    const handleHeroFade = () => {
        const scrollY = window.scrollY;
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            const heroHeight = heroSection.offsetHeight;
            
            const fadeProgress = Math.min(scrollY / (heroHeight * 1.5), 1);
            const newOpacity = Math.max(1 - (fadeProgress * 0.5), 0.2);
            
            gsap.to("#hero-title, #hero-tagline", {
                opacity: newOpacity,
                duration: 0.3,
                ease: "none"
            });
        }
    };

    window.addEventListener('scroll', handleHeroFade);

    // Headlight pulsing
    gsap.to(".headlight", { 
        fill: "#fef08a", 
        repeat: -1, 
        yoyo: true, 
        duration: 0.6, 
        ease: "sine.inOut" 
    });
    
    gsap.to(".beam", { 
        opacity: 0.3, 
        repeat: -1, 
        yoyo: true, 
        duration: 0.8 
    });

    // Exhaust smoke animation
    const createSmoke = () => {
        const svg = document.getElementById("smoke-container");
        if (svg) {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            const x = 10 + Math.random() * 10; // Small random offset from truck exhaust
            circle.setAttribute("cx", x);
            circle.setAttribute("cy", 50);
            circle.setAttribute("r", 4);
            circle.setAttribute("fill", "rgba(200,200,200,0.5)");
            svg.appendChild(circle);

            gsap.to(circle, { 
                cy: -10, 
                r: 10, 
                opacity: 0, 
                duration: 2, 
                ease: "power1.out", 
                onComplete: () => circle.remove() 
            });
        } else {
            console.log("Smoke container not found");
        }
    };
    
    // Start smoke animation after a short delay
    setTimeout(() => {
        setInterval(createSmoke, 1200);
    }, 1000);
}

// Enhanced Platform Statement Animations
function initPlatformStatement() {
    const platformTitle = document.getElementById('platform-title');
    const platformDescription = document.getElementById('platform-description');
    
    if (platformTitle && platformDescription) {
        // Create scroll trigger for platform statement
        ScrollTrigger.create({
            trigger: ".py-24.md\\:py-32.lg\\:py-40",
            start: "top 80%",
            onEnter: () => {
                // Animate title sliding in from left
                gsap.fromTo("#platform-title", 
                    { 
                        opacity: 0, 
                        x: -100
                    },
                    { 
                        opacity: 1, 
                        x: 0,
                        duration: 1, 
                        delay: 0.2,
                        ease: "power2.out"
                    }
                );
                
                // Animate description sliding in from right
                gsap.fromTo("#platform-description", 
                    { 
                        opacity: 0, 
                        x: 100
                    },
                    { 
                        opacity: 1, 
                        x: 0,
                        duration: 1, 
                        delay: 0.6,
                        ease: "power2.out"
                    }
                );
                
                // Add enhanced text effects
                gsap.to("#platform-title", {
                    textShadow: "0 4px 8px rgba(0,0,0,0.3), 0 0 20px rgba(239,68,68,0.2)",
                    duration: 1,
                    delay: 1.2,
                    ease: "power2.out"
                });
                
                gsap.to("#platform-description", {
                    textShadow: "0 2px 4px rgba(0,0,0,0.5)",
                    duration: 1,
                    delay: 1.6,
                    ease: "power2.out"
                });
            }
        });
    }
}

// Services Overview Animations with extended scroll
function initServicesOverview() {
    const servicesOverview = document.getElementById('services-overview');
    const servicesTitle = document.getElementById('services-title');
    
    if (servicesOverview && servicesTitle) {
        // Create scroll-triggered animations for the services overview with extended scroll and slower timing
        ScrollTrigger.create({
            trigger: servicesOverview,
            start: "top center",
            end: "bottom center",
            scrub: 1, // Increased from 1 to 2 for slower animation
            onUpdate: (self) => {
                const progress = self.progress;
                
                // Font size animation - direct property assignment
                const fontSize = gsap.utils.interpolate(192, 64, progress); // 12rem to 4rem
                servicesTitle.style.fontSize = fontSize + "px";
                
                // Background color animation - direct property assignment
                const backgroundColor = gsap.utils.interpolate("#1a1a1a", "#2a2a2a", progress);
                servicesOverview.style.backgroundColor = backgroundColor;
                
                // Text color animation - change to red-500 when text starts shrinking
                if (progress > 0.1) { // Start color change when text starts shrinking
                    servicesTitle.style.color = "#dc2626"; // red-500
                } else {
                    servicesTitle.style.color = "#ffffff"; // white
                }
                
                // Card animations with slower timing
                animateCards(progress);
            }
        });
    }
}

// Animate the flying cards
function animateCards(progress) {
    const cards = [
        { id: 'card1', startX: -1000, endX: -120, startY: 0, endY: -80, startRotate: -15, endRotate: -12 },
        { id: 'card2', startX: 1000, endX: 80, startY: 0, endY: -60, startRotate: 15, endRotate: 18 },
        { id: 'card3', startX: -1000, endX: -40, startY: -1000, endY: 20, startRotate: -8, endRotate: 5 },
        { id: 'card4', startX: 1000, endX: 60, startY: 1000, endY: 30, startRotate: 8, endRotate: -8 },
        { id: 'card5', startX: -1000, endX: 90, startY: -1000, endY: -40, startRotate: -20, endRotate: 15 },
        { id: 'card6', startX: 1000, endX: -90, startY: -1000, endY: 50, startRotate: 20, endRotate: -10 },
        { id: 'card7', startX: -1000, endX: 40, startY: 1000, endY: -20, startRotate: -20, endRotate: 8 }
    ];
    
    cards.forEach(card => {
        const element = document.getElementById(card.id);
        if (element) {
            const x = gsap.utils.interpolate(card.startX, card.endX, progress);
            const y = gsap.utils.interpolate(card.startY, card.endY, progress);
            const rotate = gsap.utils.interpolate(card.startRotate, card.endRotate, progress);
            
            element.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg)`;
            element.style.opacity = 1;
        }
    });
}

// Pack, Move, Settle Section Animations - Hidden Until Scroll
function initPackMoveSettleAnimations() {
    const sections = ['pack-section', 'move-section', 'settle-section'];
    
    sections.forEach((sectionId, index) => {
        const element = document.getElementById(sectionId);
        if (element) {
            // Set initial state - completely hidden
            gsap.set(element, { y: 100, opacity: 0 });
            
            ScrollTrigger.create({
                trigger: element,
                start: "top 90%",
                end: "top 10%",
                scrub: true, // Direct scroll response
                onUpdate: (self) => {
                    const progress = self.progress;
                    // Each section appears at different scroll points - faster
                    const sectionStartProgress = index * 0.15; // Pack at 0%, Move at 15%, Settle at 30%
                    const sectionProgress = Math.max(0, (progress - sectionStartProgress) / (1 - sectionStartProgress));
                    
                    if (sectionProgress > 0) {
                        // Slide up and fade in together
                        const currentY = gsap.utils.interpolate(100, 0, sectionProgress);
                        const currentOpacity = gsap.utils.interpolate(0, 1, sectionProgress);
                        gsap.set(element, { y: currentY, opacity: currentOpacity });
                    } else {
                        // Keep completely hidden
                        gsap.set(element, { y: 100, opacity: 0 });
                    }
                }
            });
        }
    });
}

// Color Changing Section Animation - Modern & Simple
function initColorChangingSection() {
    const colorChangingSection = document.getElementById("color-changing-section");
    const overlay = document.getElementById("color-changing-overlay");

    if (colorChangingSection && overlay) {
        // Start as V-shape with subtle scale
        gsap.set(overlay, {
            clipPath: "polygon(50% 100%, 100% 100%, 100% 100%, 0% 100%, 0% 100%)",
            scale: 1.05,
        });

        // Fast reveal animation
        gsap.to(overlay, {
            clipPath: "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)",
            scale: 1,
            ease: "power3.out",
            scrollTrigger: {
                trigger: colorChangingSection,
                start: "top 85%",
                end: "bottom 20%",
                scrub: 0.3,
            },
        });
    }
}

// Testimonial Cards Animation - Simple scroll-triggered appearance
function initTestimonialCards() {
  const testimonialCards = document.querySelectorAll(".testimonial-card");

  if (testimonialCards.length > 0) {
    // Clear any existing ScrollTriggers for testimonial section
    ScrollTrigger.getAll().forEach(trigger => {
      if (trigger.trigger && trigger.trigger.id === 'testimonial-section') {
        trigger.kill();
      }
    });

    // Set initial positions - all cards start stacked and hidden
    testimonialCards.forEach((card, index) => {
      gsap.set(card, {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        zIndex: testimonialCards.length - index,
        y: 0,
        opacity: 0 // Start hidden to prevent flash
      });
    });

    // Scroll trigger - cards move directly with scroll position
    ScrollTrigger.create({
      trigger: "#testimonial-section",
      start: "top center",
      end: "bottom center",
      scrub: true, // Direct scroll response - no delay
      onUpdate: (self) => {
        const progress = self.progress;
        
        testimonialCards.forEach((card, index) => {
          if (index === 0) {
            // First card stays in place
            gsap.set(card, { y: 0, opacity: 1 });
          } else {
            // Each card slides out based on scroll progress
            const cardStartProgress = (index - 1) * 0.2; // Card 2 at 20%, Card 3 at 40%, Card 4 at 60%
            
            if (progress >= cardStartProgress) {
              // Direct scroll alignment - card moves exactly with scroll
              const cardProgress = Math.min(1, (progress - cardStartProgress) / 0.2);
              const finalY = index * 250; // Reduced spacing between cards
              const currentY = gsap.utils.interpolate(0, finalY, cardProgress);
              gsap.set(card, { y: currentY, opacity: 1 });
            } else {
              // Keep card completely hidden under the previous one
              gsap.set(card, { y: 0, opacity: 0 });
            }
          }
        });
      }
    });
  }
}

// Scroll Animations
function initScrollAnimations() {
    // Initialize pack, move, settle animations
    initPackMoveSettleAnimations();
    
    // Initialize testimonial cards
    initTestimonialCards();
}

// Footer Animations
function initFooterAnimations() {
    const footer = document.getElementById('footer');
    
    if (footer) {
        ScrollTrigger.create({
            trigger: footer,
            start: "top 80%",
            onEnter: () => {
                gsap.to("#footer > div", {
                    opacity: 1,
                    duration: 1,
                    ease: "power3.out"
                });
            }
        });
    }
}

// Intersection Observer for general animations
function initIntersectionObservers() {
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
    

}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                gsap.to(window, {
                    duration: 1,
                    scrollTo: {
                        y: targetElement,
                        offsetY: 80
                    },
                    ease: "power2.inOut"
                });
            }
        });
    });
}

// Initialize smooth scrolling
initSmoothScrolling();

// Performance optimizations
function optimizePerformance() {
    // Throttle scroll events
    let ticking = false;
    
    function updateScrollAnimations() {
        // Update any scroll-based animations here
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollAnimations);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
}

// Initialize performance optimizations
optimizePerformance();

// Handle window resize
window.addEventListener('resize', function() {
    // Refresh ScrollTrigger on resize
    ScrollTrigger.refresh();
});

// Handle page visibility change
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause animations when page is hidden
        gsap.globalTimeline.pause();
    } else {
        // Resume animations when page is visible
        gsap.globalTimeline.resume();
    }
});

// Preload critical images
function preloadImages() {
    const criticalImages = [
        '/static/images/two_trucks.jpg',
        '/static/images/fire_house_logo.svg',
        '/static/images/truckk.jpg',
        '/static/images/onsite_inspection.jpg',
        '/static/images/servies.jpg',
        '/static/images/gift_cards.jpg',
        '/static/images/supplies.jpg',
        '/static/images/uniform.jpg',
        '/static/images/truck_inspection.jpeg'
    ];
    
    criticalImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// Initialize image preloading
preloadImages();

// Error handling for GSAP
window.addEventListener('error', function(e) {
    console.warn('Animation error:', e.message);
    // Fallback animations or error handling can be added here
});

// Accessibility improvements
function initAccessibility() {
    // Add keyboard navigation for mobile menu
    const hamburgerMenu = document.getElementById('hamburger-menu');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (hamburgerMenu && mobileMenu) {
        hamburgerMenu.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                hamburgerMenu.click();
            }
        });
        
        // Trap focus in mobile menu when open
        const focusableElements = mobileMenu.querySelectorAll('a, button');
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        mobileMenu.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
            
            if (e.key === 'Escape') {
                const closeMenu = document.getElementById('close-menu');
                if (closeMenu) {
                    closeMenu.click();
                }
            }
        });
    }
}

// Initialize accessibility features
initAccessibility();

// Export functions for potential external use
window.FirehouseMovers = {
    initMobileMenu,
    initHeroAnimations,
    initPlatformStatement,
    initServicesOverview,
    initScrollAnimations,
    initFooterAnimations,
    initColorChangingSection,
    initIntersectionObservers
};