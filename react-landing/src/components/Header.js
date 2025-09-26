import React, { useState } from 'react';
import './Header.css';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const redirectUrl = process.env.REACT_APP_REDIRECT_URL || ''
  console.log('redirect',redirectUrl)
    // const redirectUrl = process.env.NODE_ENV === 'production' 
  //   ? process.env.REACT_APP_REDIRECT_URL || 'https://your-production-domain.com/login'
  //   : 'http://localhost:8000/login'
  // console.log('redirect', redirectUrl, 'NODE_ENV:', process.env.NODE_ENV)

  return (
    <div className="pb-16">
      <header className="fixed top-0 w-full z-50 flex items-center justify-between px-6 py-3 bg-[#262626] shadow-lg" style={{backgroundColor: '#262626'}}>
        {/* Logo */}
        <div className="flex items-center gap-2">
          <a href="/">
            <img src="/images/fire_house_logo.svg" alt="Logo" className="w-10 h-10" />
          </a>
          <a href="/">
            <h1 className="text-xl font-bold text-gray-200 hover:text-white font-serif">FIREHOUSE</h1>
          </a>
        </div>

        {/* Navigation Links (Centered on Desktop) */}
        <div className="flex-grow flex justify-center">
          <nav className="hidden md:flex items-center gap-6 relative">
            {/* Truck Availability & Job Logistics */}
            <div className="group relative">
              <a href="/availability" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                AVAILABILITY & LOGISTICS
              </a>
            </div>

            {/* FireHouse Stations */}
            <div className="group relative">
              <a href="/station" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                STATIONS
              </a>
            </div>

            {/* Vehicle Inspection */}
            <div className="group relative">
              <a href="/inspection" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                VEHICLE INSPECTION
              </a>
            </div>

            {/* On-Site Inspection */}
            <div className="group relative">
              <a href="/onsite-inspection" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                ON-SITE INSPECTION
              </a>
            </div>

            {/* Inventory */}
            <div className="group relative">
              <a href="/inventory" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                INVENTORY
              </a>
            </div>

            {/* Gift Card */}
            <div className="group relative">
              <a href="/gift" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                GIFT
              </a>
            </div>

            {/* Packaging and Supplies */}
            <div className="group relative">
              <a href="/packaging" className="flex items-center gap-1 text-gray-200 hover:text-white text-sm hover:border-b hover:border-white">
                PACKAGING & SUPPLIES
              </a>
            </div>
          </nav>
        </div>

        {/* Login (visible if not authenticated) */}
        <a href={redirectUrl} className="ml-auto flex gap-1 justify-center text-black bg-white p-2 rounded-lg w-16">
          Login
        </a>

        {/* Hamburger Icon (visible on mobile) */}
        <div className="md:hidden flex items-center">
          <button 
            id="hamburger-menu" 
            className="text-gray-200 hover:text-white"
            onClick={toggleMobileMenu}
          >
            <i className="fa-solid fa-bars"></i>
          </button>
        </div>
      </header>

      {/* Mobile Menu */}
      <div className={`md:hidden fixed inset-0 bg-black bg-opacity-50 z-50 ${isMobileMenuOpen ? 'block' : 'hidden'}`}>
        <div className="flex justify-end p-6">
          <button 
            id="close-menu" 
            className="text-white text-2xl"
            onClick={toggleMobileMenu}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div className="flex justify-center items-center flex-col gap-4 text-white p-6">
          <a href="/availability" className="text-lg">AVAILABILITY & LOGISTICS</a>
          <a href="/station" className="text-lg">STATIONS</a>
          <a href="/inspection" className="text-lg">VEHICLE INSPECTION</a>
          <a href="/onsite-inspection" className="text-lg">ON-SITE INSPECTION</a>
          <a href="/inventory" className="text-lg">INVENTORY</a>
          <a href="/gift" className="text-lg">GIFT</a>
        </div>
      </div>
    </div>
  );
};

export default Header;
