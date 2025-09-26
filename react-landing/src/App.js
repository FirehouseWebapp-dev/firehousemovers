import React from 'react';
import './App.css';
import Header from './components/Header';
import Hero from './components/Hero';
import PlatformStatement from './components/PlatformStatement';
import ServicesOverview from './components/ServicesOverview';
import ServicesGrid from './components/ServicesGrid';
import LoginPrompt from './components/LoginPrompt';
import Footer from './components/Footer';
import CardsStack from './components/CardsStack';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#262626] via-[#1a1a1a] to-[#262626] text-gray-100 antialiased relative overflow-x-hidden">
      <Header />
      <Hero />
      <PlatformStatement />
      <ServicesOverview />
      <ServicesGrid />
      <CardsStack />
      <LoginPrompt />
      <Footer />
    </div>
  );
}

export default App;
