import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

// CardsStack component for animated testimonial cards
function CardsStack() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  // Animation transforms
  const card2Y = useTransform(scrollYProgress, [0.2, 0.35], [-100, 0]);
  const card2Opacity = useTransform(scrollYProgress, [0.2, 0.35], [0, 1]);
  const card3Y = useTransform(scrollYProgress, [0.4, 0.55], [-100, 0]);
  const card3Opacity = useTransform(scrollYProgress, [0.4, 0.55], [0, 1]);
  const card4Y = useTransform(scrollYProgress, [0.6, 0.75], [-100, 0]);
  const card4Opacity = useTransform(scrollYProgress, [0.6, 0.75], [0, 1]);

  // Testimonials data
  const testimonials = [
    {
      id: 1,
      text: "We have used Firehouse for our last 5 moves within DFW over the last 15 years. They are always professional, always on time, and they do a great job of keeping our stuff safe during transport. Today we paid for packing and they got it down so quickly and everything is very organized. These guys are the best!",
      author: "Candie Blunt",
      initials: "CB",
      color: "pink",
      isStatic: true
    },
    {
      id: 2,
      text: "I am forever grateful for Firehouse movers. The team they sent out were top notch! They were respectful of me and my stuff. They made sure everything was handled with care. I felt like the red carpet was rolled out for me. Julio, David, and Jorge are the team to ask for! They work hard and see to it that all the details are covered! Great work guys! Thank you!!!",
      author: "Jennie Lieber",
      initials: "JL",
      color: "blue",
      y: card2Y,
      opacity: card2Opacity,
      zIndex: 30
    },
    {
      id: 3,
      text: "Wow! I am simply blown away! Thank you for taking such great care of our family! From the first phone call, to the day of, and getting the move done, everything was done with such care and excellence! Getting a quote and date on the calendar was fast and easy. The team showed up on moving day right on time and went above and beyond to make sure everything was packaged safely and thoroughly wrapped. They worked quickly and efficiently with such joy and great attitudes. THANK YOU! God bless you all and bless your business! 🙌🏼",
      author: "Eugene Chua",
      initials: "EC",
      color: "green",
      y: card3Y,
      opacity: card3Opacity,
      zIndex: 20
    },
    {
      id: 4,
      text: "They were incredible, quick and efficient. No issues at all, fair price for 3 hours. The guys were friendly and checked multiple times that we were satisfied with final placement and arrangement of everything. They also went out of their way to move an oversized sofa upstairs that we were ready to abort- but they were determined. They took great care not to damage anything. Would definitely recommend.",
      author: "Shayna Bauman",
      initials: "SB",
      color: "purple",
      y: card4Y,
      opacity: card4Opacity,
      zIndex: 10
    }
  ];

  const avatarColors = {
    pink: "bg-pink-200 text-pink-700",
    blue: "bg-blue-200 text-blue-700",
    green: "bg-green-200 text-green-700",
    purple: "bg-purple-200 text-purple-700"
  };

  const baseCardClass = "w-full bg-gray-800 bg-opacity-50 backdrop-blur-sm rounded-2xl p-8 max-w-[39rem]";
  const contentClass = "text-left";
  const textClass = "text-lg text-white mb-4 italic";
  const authorClass = "flex items-center";
  const avatarClass = "w-12 h-12 rounded-full mr-4 flex items-center justify-center";
  const nameClass = "text-white font-semibold";

  return (
    <div
      ref={containerRef}
      className="relative flex flex-col items-center max-w-4xl mx-auto min-h-[120vh] space-y-8"
    >
      {testimonials.map((testimonial) => {
        const CardComponent = testimonial.isStatic ? 'div' : motion.div;
        const cardProps = testimonial.isStatic 
          ? { 
              className: `sticky top-80 ${baseCardClass} z-40`,
              style: { paddingTop: '2rem', paddingBottom: '2rem', paddingLeft: '2rem', paddingRight: '2rem' }
            }
          : {
              style: { y: testimonial.y, opacity: testimonial.opacity, maxWidth: '39rem' },
              className: `relative ${baseCardClass} z-${testimonial.zIndex}`
            };

        return (
          <CardComponent key={testimonial.id} {...cardProps}>
            <div className={contentClass}>
              <p className={textClass}>"{testimonial.text}"</p>
              <div className={authorClass}>
                <div className={`${avatarClass} ${avatarColors[testimonial.color]}`}>
                  <span className="font-semibold text-lg">{testimonial.initials}</span>
                </div>
                <div>
                  <h4 className={nameClass}>{testimonial.author}</h4>
                </div>
              </div>
            </div>
          </CardComponent>
        );
      })}
    </div>
  );
}

export default CardsStack;
