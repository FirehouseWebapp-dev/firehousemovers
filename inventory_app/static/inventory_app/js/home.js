// Firehouse Movers Home Page JavaScript

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

const tl = gsap.timeline({ repeat: -1, repeatDelay: 1 });

// truck drive-in, pause, drive-out
tl.fromTo("#truck", { x: "-40%", y: 0, opacity: 0 }, { x: "20%", opacity: 1, duration: 4, ease: "power2.out" })
  .to("#truck", { x: "20%", duration: 2 })
  .to("#truck", { x: "140%", duration: 5, ease: "power2.in", opacity: 0 }, ">-0.5");

// wheels spin
gsap.to(["#wheel1", "#wheel2", "#wheel3"], { rotation: 360, transformOrigin: "50% 50%", repeat: -1, ease: "linear", duration: 1 });

// suspension bounce
gsap.to("#truck", { y: -4, yoyo: true, repeat: -1, duration: 0.8, ease: "sine.inOut" });

// text slides down from top immediately on page load
gsap.fromTo("#hero-title", 
  { opacity: 0, y: -50 }, 
  { opacity: 1, y: 0, duration: 1.2, ease: "power3.out" }
);
gsap.fromTo("#hero-tagline", 
  { opacity: 0, y: -30 }, 
  { opacity: 1, y: 0, duration: 1, delay: 0.3, ease: "power3.out" }
);

// Hero content fade on scroll
function handleHeroFade() {
  const scrollY = window.scrollY;
  const heroSection = document.querySelector('header');
  const heroHeight = heroSection.offsetHeight;
  
  // Calculate fade progress (0 to 1)
  const fadeProgress = Math.min(scrollY / (heroHeight * 0.8), 1);
  
  // Fade out hero content as user scrolls (minimum opacity 0.2)
  const newOpacity = Math.max(1 - (fadeProgress * 0.8), 0.2);
  
  gsap.to("#hero-title, #hero-tagline", {
    opacity: newOpacity,
    duration: 0.3,
    ease: "none"
  });
}

// Add scroll listener for hero fade
window.addEventListener('scroll', handleHeroFade);

// Platform statement animations
function animatePlatformStatement() {
  const platformTitle = document.getElementById('platform-title');
  const platformDescription = document.getElementById('platform-description');
  
  if (platformTitle && platformDescription) {
    // Reset elements to initial state
    gsap.set("#platform-title", { opacity: 0, x: -100, y: 30 });
    gsap.set("#platform-description", { opacity: 0, x: 100, y: 30 });
    
    // Title slides in from left with fade
    gsap.to("#platform-title", {
      opacity: 1, x: 0, y: 0, duration: 1.2, delay: 0.3, ease: "power3.out"
    });
    
    // Description slides in from right with fade
    gsap.to("#platform-description", {
      opacity: 1, x: 0, y: 0, duration: 1.2, delay: 0.6, ease: "power3.out"
    });
  }
}

// Trigger platform animation when section comes into view (every time)
const platformSection = document.querySelector('section.py-20.bg-gradient-to-b');
if (platformSection) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animatePlatformStatement();
      }
    });
  }, { threshold: 0.3 });
  
  observer.observe(platformSection);
}

// Initialize page load animations
window.addEventListener('load', () => {
  setTimeout(() => {
    animatePlatformStatement();
    addCardHoverEffects();
  }, 1000);
});

// Services overview animations
function animateServicesOverview() {
  const overviewTitle = document.getElementById('services-overview-title');
  const overviewDescription = document.getElementById('services-overview-description');
  const serviceHighlights = document.querySelectorAll('[id^="service-highlight-"]');
  
  if (overviewTitle && overviewDescription) {
    // Reset elements to initial state
    gsap.set("#services-overview-title", { opacity: 0, y: 30 });
    gsap.set("#services-overview-description", { opacity: 0, y: 30 });
    gsap.set(serviceHighlights, { opacity: 0, y: 40 });
    
    // Title fades in from below
    gsap.to("#services-overview-title", {
      opacity: 1, y: 0, duration: 1, delay: 0.2, ease: "power3.out"
    });
    
    // Description fades in from below
    gsap.to("#services-overview-description", {
      opacity: 1, y: 0, duration: 1, delay: 0.4, ease: "power3.out"
    });
    
    // Service highlights stagger in
    gsap.to(serviceHighlights, {
      opacity: 1, y: 0, duration: 0.8, delay: 0.6, ease: "power3.out", stagger: 0.2
    });
  }
}

// Trigger services overview animation when section comes into view
const servicesOverviewSection = document.querySelector('section.py-16.bg-gradient-to-b');
if (servicesOverviewSection) {
  const overviewObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateServicesOverview();
      }
    });
  }, { threshold: 0.3 });
  
  overviewObserver.observe(servicesOverviewSection);
}

// Animate service cards sequentially when scrolled into view
function animateCardsSequentially() {
  const allCards = gsap.utils.toArray("[data-animate]");
  
  // Group cards by their container sections
  const servicesSection = document.querySelector('#services');
  const additionalSection = document.querySelector('#services').nextElementSibling;
  const marketingSection = additionalSection.nextElementSibling;
  
  // Animate cards in each section sequentially
  [servicesSection, additionalSection, marketingSection].forEach((section, sectionIndex) => {
    if (section) {
      const sectionCards = section.querySelectorAll("[data-animate]");
      
      ScrollTrigger.create({
        trigger: section,
        start: "top 80%",
        end: "bottom 20%",
        onEnter: () => {
          // Smooth sequential animation with shorter intervals
          sectionCards.forEach((card, index) => {
            gsap.fromTo(card,
              { 
                opacity: 0, 
                y: 30, 
                scale: 0.95,
                rotationX: 10,
                filter: "blur(2px)"
              },
              {
                opacity: 1,
                y: 0,
                scale: 1,
                rotationX: 0,
                filter: "blur(0px)",
                duration: 1,
                ease: "power2.out",
                delay: index * 0.15 // Smoother 0.15 second intervals
              }
            );
          });
        },
        onLeaveBack: () => {
          // Smooth exit animation
          sectionCards.forEach((card, index) => {
            gsap.to(card, {
              opacity: 0,
              y: 20,
              scale: 0.98,
              rotationX: -5,
              filter: "blur(1px)",
              duration: 0.6,
              ease: "power2.inOut",
              delay: (sectionCards.length - index - 1) * 0.08 // Faster reverse
            });
          });
        }
      });
    }
  });
}

// Initialize sequential animations
animateCardsSequentially();

// Add smooth hover animations for cards
function addCardHoverEffects() {
  const serviceCards = document.querySelectorAll('.service-card');
  
  serviceCards.forEach(card => {
    // Mouse enter - smooth lift effect
    card.addEventListener('mouseenter', () => {
      gsap.to(card, {
        scale: 1.03,
        y: -8,
        rotationY: 2,
        rotationX: 2,
        duration: 0.6,
        ease: "power2.out",
        boxShadow: "0 15px 35px rgba(0,0,0,0.2)"
      });
    });
    
    // Mouse leave - smooth return
    card.addEventListener('mouseleave', () => {
      gsap.to(card, {
        scale: 1,
        y: 0,
        rotationY: 0,
        rotationX: 0,
        duration: 0.6,
        ease: "power2.out",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)"
      });
    });
  });
}


// Comprehensive Trust Section Animations
function animateTrustSection() {
  const trustSection = document.getElementById('trust-section');
  if (!trustSection) return;

  // Animate section header
  gsap.to("#trust-title", {
    opacity: 1,
    y: 0,
    duration: 1,
    ease: "power3.out",
    delay: 0.2
  });

  gsap.to("#trust-subtitle", {
    opacity: 1,
    y: 0,
    duration: 1,
    ease: "power3.out",
    delay: 0.4
  });

  // Animate stats cards with stagger
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach((card, index) => {
    const delay = parseInt(card.dataset.delay) / 1000;
    
    gsap.to(card, {
      opacity: 1,
      y: 0,
      duration: 0.8,
      ease: "back.out(1.2)",
      delay: 0.6 + delay,
      onComplete: () => {
        // Add floating animation after card appears
        gsap.to(card, {
          y: -5,
          duration: 2,
          ease: "sine.inOut",
          yoyo: true,
          repeat: -1,
          delay: Math.random() * 2
        });
      }
    });
  });

  // Start counter animation
  setTimeout(() => {
    animateCounters();
  }, 1000);
}

// Enhanced counter animation with easing
function animateCounters() {
  const counters = document.querySelectorAll('.counter');
  
  counters.forEach((counter, index) => {
    const target = parseInt(counter.getAttribute('data-target'));
    
    // Use GSAP for smooth counter animation
    gsap.fromTo(counter, 
      { textContent: 0 },
      {
        textContent: target,
        duration: 2,
        ease: "power2.out",
        delay: index * 0.2,
        snap: { textContent: 1 },
        onUpdate: function() {
          counter.textContent = Math.floor(this.targets()[0].textContent).toLocaleString();
        },
        onComplete: () => {
          // Add pulse effect when counter completes
          gsap.to(counter, {
            scale: 1.1,
            duration: 0.2,
            ease: "power2.out",
            yoyo: true,
            repeat: 1
          });
        }
      }
    );
  });
}

// Trigger trust section animations
const trustSection = document.getElementById('trust-section');
if (trustSection) {
  const trustObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateTrustSection();
      }
    });
  }, { threshold: 0.2 });
  
  trustObserver.observe(trustSection);
}

// Footer animation
function animateFooter() {
  const footer = document.getElementById('footer');
  if (footer) {
    gsap.to("#footer > div", {
      opacity: 1,
      duration: 1,
      ease: "power3.out"
    });
  }
}

// Trigger footer animation when it comes into view
const footerElement = document.getElementById('footer');
if (footerElement) {
  const footerObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateFooter();
      }
    });
  }, { threshold: 0.2 });
  
  footerObserver.observe(footerElement);
}

// headlight pulsing
gsap.to(".headlight", { fill: "#fef08a", repeat: -1, yoyo: true, duration: 0.6, ease: "sine.inOut" });
gsap.to(".beam", { opacity: 0.3, repeat: -1, yoyo: true, duration: 0.8 });

// exhaust smoke animation
function createSmoke() {
  const svg = document.getElementById("smoke-container");
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  const x = 10 + Math.random() * 10;
  circle.setAttribute("cx", x);
  circle.setAttribute("cy", 50);
  circle.setAttribute("r", 4);
  circle.setAttribute("fill", "rgba(200,200,200,0.5)");
  svg.appendChild(circle);

  gsap.to(circle, { cy: -10, r: 10, opacity: 0, duration: 2, ease: "power1.out", onComplete: () => circle.remove() });
}
setInterval(createSmoke, 1200);
