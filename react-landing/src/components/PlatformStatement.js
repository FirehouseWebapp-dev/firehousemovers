import React, { useEffect } from 'react';
import './PlatformStatement.css';

const PlatformStatement = () => {

  useEffect(() => {
    const loadGSAP = async () => {
      const gsap = (await import('gsap')).default;
      const ScrollTrigger = (await import('gsap/ScrollTrigger')).default;
      
      gsap.registerPlugin(ScrollTrigger);

      // Platform statement animations
      const animatePlatformStatement = () => {
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
      };

      // Trigger platform animation when section comes into view
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
      setTimeout(() => {
        animatePlatformStatement();
      }, 1000);
    };

    loadGSAP();
  }, []);

  return (
    <section className="py-20 bg-gradient-to-b from-[#262626] via-[#1a1a1a] to-[#262626]">
      <div className="max-w-4xl mx-auto px-6 md:px-12 lg:px-24">
        <div className="text-left mt-16">
          <h2 
            id="platform-title" 
            className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight tracking-tight text-white mb-8 opacity-0"
          >
            The moving service we needed,<br />
            so we built it for you
          </h2>
          <p 
            id="platform-description" 
            className="text-lg md:text-xl text-gray-300 leading-relaxed max-w-3xl opacity-0"
          >
            Built by a dedicated team with years of experience, Firehouse Movers gives you access to trusted moving techniques, reliable crews, and modern tools that make relocating simple. Whether it's across town or across the state, we handle the heavy lifting so you can focus on what matters most.
          </p>
        </div>
      </div>
    </section>
  );
};

export default PlatformStatement;
