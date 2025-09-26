import { motion, useScroll, useTransform, useSpring } from "framer-motion";
import { useRef } from "react";
import CardsStack from "./CardsStack";

// ColorChangingSection component with dual-layer setup
function ColorChangingSection() {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  return (
    <div
      ref={sectionRef}
      className="relative min-h-screen flex flex-col items-center justify-start pt-32 overflow-hidden"
    >
      {/* FIRST LAYER — red background + dark gray text */}
      <div className="absolute inset-0 bg-red-500 flex items-center justify-center">
        <div className="text-center text-6xl md:text-8xl lg:text-[10rem] font-bold text-[#2A2A2A]">
          1 million users,
          <br />
          plus you.
        </div>
      </div>

      {/* SECOND LAYER — dark background + red text (reveals with clipPath) */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        style={{
          clipPath: useTransform(
            scrollYProgress,
            [0, 0.25, 0.5],
            [
              // 1️⃣ Start: diagonal line at corner (hidden)
              "polygon(0% 100%, 100% 0%, 100% 100%, 0% 100%)",
              // 2️⃣ Diagonal reveals
              "polygon(0% 100%, 50% 50%, 100% 0%, 100% 100%, 0% 100%)",
              // 3️⃣ Fully revealed
              "polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)",
            ]
          ),
          backgroundColor: "#2A2A2A",
        }}
      >
        <div className="text-center text-6xl md:text-8xl lg:text-[10rem] font-bold text-red-500">
          1 million users,
          <br />
          plus you.
        </div>
      </motion.div>
    </div>
  );
}

export default function ServicesOverview() {
  const sectionRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  // Service cards data
  const serviceCards = [
    {
      id: 1,
      title: "Truck Availability & Job Logistics",
      description: "See real-time availability and dispatch job logistics efficiently.",
      image: "/images/firehouse_movers.jpeg",
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
      category: "STATION",
      icon: (
        <svg className="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm2 6a2 2 0 114 0 2 2 0 01-4 0zm8 0a2 2 0 114 0 2 2 0 01-4 0z" clipRule="evenodd"/>
        </svg>
      )
    },
    {
      id: 4,
      title: "Uniform Inventory System",
      description: "Manage uniforms, sizes and allocations.",
      image: "/images/uniform.jpg",
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
      category: "PACKAGING",
      icon: (
        <svg className="w-6 h-6 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd"/>
        </svg>
      )
    }
  ];

  // Cards opacity - fade in after 0.05 scroll
  const cardsOpacity = useTransform(scrollYProgress, [0.05, 0.15], [0, 1]);

  const combinedFontScale = useTransform(
    scrollYProgress,
    [0, 0.1, 0.2, 0.3, 1],
    ['12rem', '10rem', '8rem', '6rem', '4rem'] // 🔹 MORE BIG
  );

  // Spring animation for smoother scaling
  const smoothCombinedFont = useSpring(combinedFontScale, { 
    stiffness: 35, 
    damping: 20,
    mass: 0.8,
    precision: 0.01
  });

  // Background color animation - faster transition to match shrinking
  const backgroundColor = useTransform(scrollYProgress, [0, 0.1, 0.2, 1], ['#1a1a1a', '#1a1a1a', '#2a2a2a', '#2a2a2a']);
  
  // Text color animation - faster transition to match shrinking
  const textColor = useTransform(scrollYProgress, [0, 0.2, 0.3, 1], ['#ffffff', '#ffffff', '#ef4444', '#ef4444']);

  // Generate staggered slide-in animations (right -> left)
  const card0Slide = useTransform(scrollYProgress, [0.05, 0.15], [200, 0]);
  const card1Slide = useTransform(scrollYProgress, [0.08, 0.18], [200, 0]);
  const card2Slide = useTransform(scrollYProgress, [0.11, 0.21], [200, 0]);
  const card3Slide = useTransform(scrollYProgress, [0.14, 0.24], [200, 0]);
  const card4Slide = useTransform(scrollYProgress, [0.17, 0.27], [200, 0]);
  const card5Slide = useTransform(scrollYProgress, [0.20, 0.30], [200, 0]);
  const card6Slide = useTransform(scrollYProgress, [0.23, 0.33], [200, 0]);
  
  const cardSlides = [card0Slide, card1Slide, card2Slide, card3Slide, card4Slide, card5Slide, card6Slide];

  return (
    <div className="relative">
      {/* Sticky container */}
      <motion.div
        ref={sectionRef}
        className="sticky top-0 h-[130vh] flex flex-col items-center justify-center relative pt-12"
        style={{
          zIndex: 10,
          backgroundColor: backgroundColor,
        }}
      >
        {/* Heading */}
        <motion.h2
          className="text-2xl md:text-3xl lg:text-4xl font-bold text-center w-full py-4"
          style={{
            fontSize: smoothCombinedFont,
            color: textColor,
          }}
        >
          MOVE AS ONE
        </motion.h2>

        {/* Cards fly in when sticky div is active */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
          {/* Card 1 - from left */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [-1000, -120], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [0, -80], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [-15, -12], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 1, // layer order
            }}
          >
            <img src="/images/truckk.jpg" alt="Marketing Inventory" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 2 - from right */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [1000, 80], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [0, -60], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [15, 18], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 2, // layer order
            }}
          >
            <img src="/images/onsite_inspection.jpg" alt="Onsite Inspection" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 3 - from top-left */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [-1000, -40], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [-1000, 20], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [-8, 5], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 3, // layer order
            }}
          >
            <img src="/images/servies.jpg" alt="Services" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 4 - from bottom-right */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [1000, 60], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [1000, 30], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [8, -8], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 4, // layer order
            }}
          >
            <img src="/images/gift_cards.jpg" alt="Gift Cards" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 5 - from top-left diagonal */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [-1000, 90], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [-1000, -40], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [-20, 15], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 5, // layer order
            }}
          >
            <img src="/images/supplies.jpg" alt="Supplies" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 6 - from top-right diagonal */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [1000, -90], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [-1000, 50], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [20, -10], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 6, // layer order
            }}
          >
            <img src="/images/uniform.jpg" alt="Uniform" className="w-full h-full object-cover" />
          </motion.div>

          {/* Card 7 - from bottom-left diagonal */}
          <motion.div
            className="absolute w-60 h-44 md:w-80 md:h-60 rounded-lg shadow-lg overflow-hidden"
            style={{
              x: useTransform(scrollYProgress, [0, 1], [-1000, 40], { clamp: false }),
              y: useTransform(scrollYProgress, [0, 1], [1000, -20], { clamp: false }),
              rotate: useTransform(scrollYProgress, [0, 1], [-20, 8], { clamp: false }),
              opacity: 1, // no fade
              zIndex: 7, // layer order
            }}
          >
            <img src="/images/truck_inspection.jpeg" alt="Truck Inspection" className="w-full h-full object-cover" />
          </motion.div>
        </div>

      </motion.div>
      
      {/* Pack, Move, Settle section */}
      <div className="relative min-h-screen flex flex-col items-center justify-center bg-[#1a1a1a]">
        <div className="flex flex-col items-center space-y-16">
          {/* Pack text with logo */}
          <motion.div
            className="flex flex-row items-center space-x-6"
            initial={{ opacity: 0, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            viewport={{ once: false, amount: 0.3 }}
          >
            <div className="w-20 h-20 flex items-center justify-center bg-white rounded-full">
              <svg className="w-12 h-12 text-gray-800" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div className="text-6xl md:text-7xl lg:text-8xl font-bold text-white">
              Pack
            </div>
          </motion.div>
          
          {/* Move text with logo */}
          <motion.div
            className="flex flex-row items-center space-x-6"
            initial={{ opacity: 0, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.3 }}
            viewport={{ once: false, amount: 0.3 }}
          >
            <div className="w-20 h-20 flex items-center justify-center bg-red-500 rounded-full">
              <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div className="text-6xl md:text-7xl lg:text-8xl font-bold text-red-500">
              Move
            </div>
          </motion.div>
          
          {/* Settle text with logo */}
          <motion.div
            className="flex flex-row items-center space-x-6"
            initial={{ opacity: 0, y: 100 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut", delay: 0.6 }}
            viewport={{ once: false, amount: 0.3 }}
          >
            <div className="w-20 h-20 flex items-center justify-center bg-green-500 rounded-full">
              <svg className="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div className="text-6xl md:text-7xl lg:text-8xl font-bold text-green-500">
              Settle
            </div>
          </motion.div>
        </div>
      </div>

      {/* Dark grey background section */}
      <div className="relative min-h-screen bg-white flex flex-col items-center justify-start pt-20">
        <div className="text-center px-6 md:px-12 lg:px-24">
          <div className="space-y-6">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-800">
              Fast moves? <span className="text-red-500">Sure.</span>
            </h2>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-800">
              Safe handling? <span className="text-red-500">Check.</span>
            </h2>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-800">
              On-time delivery? <span className="text-red-500">Also check.</span>
            </h2>
          </div>
          
          {/* Lottie Animation */}
          <div className="mt-16 flex justify-center">
            <dotlottie-wc 
              src="https://lottie.host/323e0b6b-9f38-4aeb-bbbe-c2ad20e1b0be/Q5PeNUlqIO.lottie" 
              style={{
                width: "500px", 
                height: "500px",
                backgroundColor: "transparent",
                background: "transparent"
              }} 
              autoplay 
              loop
            ></dotlottie-wc>
          </div>
          
        </div>
      </div>

      {/* Team Photo Background Section */}
      <div 
        className="relative min-h-screen bg-cover bg-center bg-no-repeat flex flex-col items-center justify-start pt-20 pb-32"
        style={{
          backgroundImage: "url('/images/background.jpg')"
        }}
      >
        {/* Overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-50"></div>
        
        {/* Content over the background image */}
        <div className="relative z-10 text-center text-white px-6 md:px-12 lg:px-24 w-full">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-[120px]">
            Hear it from our clients
          </h2>
          
          {/* Client testimonial cards */}
          <CardsStack />
        </div>
      </div>

      {/* Color changing background section */}
      <ColorChangingSection />
    </div>
  );
}