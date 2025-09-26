import React, { useEffect } from 'react';
import './Footer.css';

const Footer = () => {
  useEffect(() => {
    const loadGSAP = async () => {
      const gsap = (await import('gsap')).default;
      const ScrollTrigger = (await import('gsap/ScrollTrigger')).default;
      
      gsap.registerPlugin(ScrollTrigger);

      // Footer animation
      const animateFooter = () => {
        const footer = document.getElementById('footer');
        if (footer) {
          gsap.to("#footer > div", {
            opacity: 1,
            duration: 1,
            ease: "power3.out"
          });
        }
      };

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
    };

    loadGSAP();
  }, []);

  return (
    <footer id="footer" className="bg-gradient-to-b from-[#1a1a1a] to-[#0f0f0f] border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-6 md:px-12 lg:px-24 py-4 opacity-0">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-16 lg:gap-24 mb-12 justify-items-start md:justify-items-center">
          
          {/* Company Info */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 16.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM15 16.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
                  <path d="M3 4a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1V5a1 1 0 00-1-1H3z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold text-white">Firehouse Movers</h3>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Firehouse Movers Inc. is a fast-growing franchise moving company offering a full range of moving services to residents and businesses. We are here to relieve the stress associated with relocating.
            </p>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <span className="text-gray-400 text-xs">Licensed & Insured</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span className="text-gray-400 text-xs">5-Star Rated Service</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <span className="text-gray-400 text-xs">Trained Moving Experts</span>
              </div>
            </div>
          </div>

          {/* Services */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white">Services</h4>
            <ul className="space-y-3">
              <li><a href="#services" className="text-gray-400 hover:text-white transition-colors duration-300 text-sm">Services</a></li>
              <li><a href="/availability" className="text-gray-400 hover:text-white transition-colors duration-300 text-sm">Logistics</a></li>
              <li><a href="/inspection" className="text-gray-400 hover:text-white transition-colors duration-300 text-sm">Inspections</a></li>
              <li><a href="/inventory" className="text-gray-400 hover:text-white transition-colors duration-300 text-sm">Inventory</a></li>
              <li><a href="/station" className="text-gray-400 hover:text-white transition-colors duration-300 text-sm">Station Management</a></li>
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4 md:justify-self-end">
            <h4 className="text-lg font-semibold text-white">Contact Info</h4>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
                </svg>
                <div>
                  <p className="text-gray-400 text-sm">2535-B TEXAS 121 E, STATE #140</p>
                  <p className="text-gray-400 text-sm">LEWISVILLE, TX 75056</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                </svg>
                <p className="text-gray-400 text-sm">(972) 412-6033</p>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                </svg>
                <p className="text-gray-400 text-sm">support@firehousemovers.com</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Footer */}
        <div className="border-t border-gray-800 pt-3">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-sm text-gray-400">
              © {new Date().getFullYear()} Firehouse Movers Inc. All rights reserved.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
