import React from 'react';
import { motion } from 'framer-motion';
import './ServicesGrid.css';

const ServicesGrid = () => {
  // Animation variants for staggered cards
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const cardVariants = {
    hidden: { 
      opacity: 0, 
      x: -50, 
      scale: 0.95 
    },
    visible: { 
      opacity: 1, 
      x: 0, 
      scale: 1,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const services = [
    {
      id: 1,
      title: "Truck Availability & Job Logistics",
      description: "See real-time availability and dispatch job logistics efficiently.",
      image: "/images/firehouse_movers.jpeg",
      link: "/availability",
      category: "AVAILABILITY",
      icon: (
        <svg className="w-6 h-6 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M8 16.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM15 16.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
          <path d="M3 4a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1V5a1 1 0 00-1-1H3zM3 10a1 1 0 00-1 1v1a1 1 0 001 1h1a1 1 0 001-1v-1a1 1 0 00-1-1H3z"/>
        </svg>
      )
    },
    {
      id: 2,
      title: "Truck & Trailer Inspection",
      description: "Quick checklists and photo logging for safety compliance.",
      image: "/images/truck_inspection.jpeg",
      link: "/inspection",
      category: "INSPECTION",
      icon: (
        <svg className="w-6 h-6 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 3,
      title: "Firehouse Station",
      description: "Station resources, schedules and hub operations at a glance.",
      image: "/images/firehouse_station.jpeg",
      link: "/station",
      category: "STATION",
      icon: (
        <svg className="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 114 0 2 2 0 01-4 0zm8 0a2 2 0 114 0 2 2 0 01-4 0z" clipRule="evenodd"/>
        </svg>
      )
    }
  ];

  const additionalServices = [
    {
      id: 4,
      title: "Uniform Inventory System",
      description: "Manage uniforms, sizes and allocations.",
      image: "/images/uniform.jpg",
      link: "/inventory",
      category: "INVENTORY",
      icon: (
        <svg className="w-6 h-6 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 5,
      title: "Gift Cards",
      description: "Rewards for employees and special promotions.",
      image: "/images/gift_cards.jpg",
      link: "/gift",
      category: "GIFT",
      icon: (
        <svg className="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      )
    },
    {
      id: 6,
      title: "On Site Inspection",
      description: "Record site conditions & get approvals quickly.",
      image: "/images/onsite_inspection.jpg",
      link: "/onsite-inspection",
      category: "ONSITE",
      icon: (
        <svg className="w-6 h-6 text-teal-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 7,
      title: "Packaging & Supplies",
      description: "High-quality packing for fragile goods.",
      image: "/images/packaging.jpeg",
      link: "/packaging",
      category: "PACKAGING",
      icon: (
        <svg className="w-6 h-6 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd"/>
        </svg>
      )
    }
  ];

  const marketingServices = [
    {
      id: 8,
      title: "Marketing Inventory",
      description: "Branded assets & photos.",
      image: "/images/marketing.jpeg",
      link: "/marketing",
      category: "MARKETING",
      icon: (
        <svg className="w-6 h-6 text-pink-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 9,
      title: "Prizes & Acknowledgements",
      description: "Recognize and reward top performers.",
      image: "/images/acknowledgments.jpg",
      link: "/awards",
      category: "AWARDS",
      icon: (
        <svg className="w-6 h-6 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      )
    },
    {
      id: 10,
      title: "Employees Evaluation",
      description: "Create and manage evaluation forms.",
      image: "/images/employees_evaluation.jpg",
      link: "/evaluation",
      category: "EVALUATION",
      icon: (
        <svg className="w-6 h-6 text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 11,
      title: "Fleet Fueling",
      description: "Fuel logs and scheduling for your fleet.",
      image: "/images/fleet_fueling_status.jpg",
      link: "/fleet",
      category: "FLEET",
      icon: (
        <svg className="w-6 h-6 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 114 0 2 2 0 01-4 0zm8 0a2 2 0 114 0 2 2 0 01-4 0z" clipRule="evenodd"/>
        </svg>
      )
    }
  ];

  const ServiceCard = ({ service, index }) => (
    <motion.div 
      className="service-card group relative overflow-hidden rounded-xl bg-[#262626] border border-gray-700 transition-all duration-300 cursor-default" 
      variants={cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.1 }}
    >
      <div className="relative h-64 p-6">
        {/* Background image that is always visible */}
        <img 
          src={service.image} 
          alt={service.title} 
          className="absolute inset-0 w-full h-full object-cover opacity-100 group-hover:opacity-30 z-10 hover-image transition-opacity duration-300"
        />
        
        <div className="relative z-20 h-full flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              {service.icon}
            </div>
            <div className="text-xs text-gray-400 font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              {service.category}
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2 text-white">{service.title}</h3>
            <p className="text-sm text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              {service.description}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <main id="main" className="-mt-8 relative" style={{ scrollSnapType: 'y mandatory' }}>
      {/* Service cards removed - keeping only the main structure */}
    </main>
  );
};

export default ServicesGrid;
