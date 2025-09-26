import React from 'react';
import './LoginPrompt.css';

const LoginPrompt = () => {
  return (
    <section className="pt-24 pb-24 bg-gradient-to-b from-[#262626] via-[#1a1a1a] to-[#262626]">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to <span className="text-red-500">Take Control</span>?
        </h2>
        
        <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
          Join our platform to streamline your moving operations with professional tools and real-time insights.
        </p>

        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
          <a 
            href="/login/" 
            className="group inline-flex items-center gap-3 px-10 py-4 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
          >
            <span>LogIn</span>
            <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </a>
          
          <a 
            href="/signup/" 
            className="px-10 py-4 bg-transparent border-2 border-white/20 hover:border-white/40 text-white hover:bg-white/5 font-semibold rounded-lg transition-all duration-300"
          >
            Create Account
          </a>
        </div>
      </div>
    </section>
  );
};

export default LoginPrompt;
