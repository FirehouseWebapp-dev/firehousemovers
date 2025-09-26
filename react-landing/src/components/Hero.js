import React, { useEffect } from 'react';
import './Hero.css';

const Hero = () => {

  useEffect(() => {
    // Load GSAP dynamically
    const loadGSAP = async () => {
      const gsap = (await import('gsap')).default;
      const ScrollTrigger = (await import('gsap/ScrollTrigger')).default;
      
      gsap.registerPlugin(ScrollTrigger);

      // Truck continuous loop movement
      gsap.fromTo("#truck",
        { x: "-150px" },
        { x: "110vw", duration: 10, ease: "linear", repeat: -1 }
      );

      // Wheels spin
      gsap.to(["#wheel1", "#wheel2", "#wheel3"], { 
        rotation: 360, 
        transformOrigin: "50% 50%", 
        repeat: -1, 
        ease: "linear", 
        duration: 1 
      });

      // Suspension bounce
      gsap.to("#truck", { 
        y: -4, 
        yoyo: true, 
        repeat: -1, 
        duration: 0.8, 
        ease: "sine.inOut" 
      });

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
        const heroSection = document.querySelector('header');
        const heroHeight = heroSection.offsetHeight;
        
        const fadeProgress = Math.min(scrollY / (heroHeight * 1.5), 1);
        const newOpacity = Math.max(1 - (fadeProgress * 0.5), 0.2);
        
        gsap.to("#hero-title, #hero-tagline", {
          opacity: newOpacity,
          duration: 0.3,
          ease: "none"
        });
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
          const x = 10 + Math.random() * 10;
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
        }
      };
      
      setInterval(createSmoke, 1200);
    };

    loadGSAP();
  }, []);

  return (
    <header className="relative overflow-hidden h-screen">
      {/* Background Image */}
      <div className="absolute inset-0">
        <img 
          src="/images/two_trucks.jpg" 
          alt="Firehouse Movers Trucks" 
          className="w-full h-full object-cover object-center background-image opacity-60"
        />
        {/* Strong dark overlay for text contrast */}
        <div className="absolute inset-0 bg-black/50"></div>
        {/* Additional gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/30"></div>
      </div>

      {/* SVG Truck Scene */}
      <div className="absolute inset-0 flex items-end justify-start overflow-hidden z-10 truck-animation" id="truck-scene">
        <svg id="truck" className="w-[20rem] h-auto drop-shadow-2xl" viewBox="0 0 320 120" xmlns="http://www.w3.org/2000/svg">
          {/* trailer */}
          <rect x="10" y="30" rx="8" ry="8" width="190" height="60" className="truck-body" />
          {/* Firehouse logo on trailer */}
          <image href="/images/fire_house_logo.svg" x="82" y="35" width="45" height="45" opacity="0.7" />
          {/* cab */}
          <rect x="200" y="40" rx="6" ry="6" width="90" height="50" className="truck-cab" />
          {/* windows */}
          <rect x="210" y="48" width="26" height="18" rx="2" className="truck-window" />
          <rect x="240" y="48" width="30" height="18" rx="2" className="truck-window" />
          {/* headlights */}
          <circle cx="290" cy="72" r="6" className="headlight" />
          <circle cx="290" cy="90" r="6" className="headlight" />
          {/* headlight beams */}
          <polygon points="296,66 320,58 320,86 296,78" className="beam" />
          <polygon points="296,84 320,76 320,104 296,96" className="beam" />
          {/* wheels */}
          <circle id="wheel1" cx="60" cy="95" r="14" className="wheel" />
          <circle id="wheel2" cx="170" cy="95" r="14" className="wheel" />
          <circle id="wheel3" cx="250" cy="95" r="14" className="wheel" />
        </svg>

        {/* exhaust smoke group */}
        <svg className="absolute left-[185px] bottom-[65px]" id="smoke-container" width="40" height="60"></svg>
      </div>

      {/* Hero content */}
      <div className="relative z-20 h-full flex items-center justify-center px-6">
        <div className="text-center max-w-4xl mx-auto">
          {/* Enhanced text with strong shadows and contrast */}
          <h1 
            id="hero-title" 
            className="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 tracking-wide drop-shadow-2xl" 
            style={{
              textShadow: '0 4px 8px rgba(0,0,0,0.9), 0 2px 4px rgba(0,0,0,0.8), 0 0 20px rgba(0,0,0,0.5)'
            }}
          >
            <span className="text-white drop-shadow-2xl">FIREHOUSE</span><br />
            <span 
              className="text-red-500 drop-shadow-2xl" 
              style={{
                textShadow: '0 4px 8px rgba(0,0,0,0.9), 0 2px 4px rgba(0,0,0,0.8), 0 0 20px rgba(239,68,68,0.3)'
              }}
            >
              MOVERS
            </span>
          </h1>
          
          <p 
            id="hero-tagline" 
            className="text-xl md:text-2xl text-white mb-8 max-w-2xl mx-auto leading-relaxed font-medium drop-shadow-xl" 
            style={{
              textShadow: '0 2px 4px rgba(0,0,0,0.8), 0 1px 2px rgba(0,0,0,0.6)'
            }}
          >
            Professional moving services across the state. Fast, secure, and dependable.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="#services" 
              className="px-8 py-4 bg-red-500 text-white font-semibold hover:bg-red-600 transition-all duration-300 rounded-lg shadow-2xl hover:shadow-red-500/25 hover:scale-105 transform"
            >
              Get Started
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Hero;
