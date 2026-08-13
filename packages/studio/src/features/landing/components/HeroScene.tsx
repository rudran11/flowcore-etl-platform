import React, { useRef, useState, useEffect } from 'react';
import { motion, useSpring, useTransform, useReducedMotion } from 'framer-motion';
import { TopologyGrid } from './TopologyGrid';

export const HeroScene: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isMobile, setIsMobile] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  // Use springs for smooth parallax interpolation
  const mouseX = useSpring(0, { stiffness: 50, damping: 20 });
  const mouseY = useSpring(0, { stiffness: 50, damping: 20 });

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (isMobile || prefersReducedMotion) return;

    const handleMouseMove = (e: MouseEvent) => {
      // Normalize mouse coordinates to -1 to 1 range
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = (e.clientY / window.innerHeight) * 2 - 1;
      
      mouseX.set(x);
      mouseY.set(y);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isMobile, prefersReducedMotion, mouseX, mouseY]);

  // Transform normalized mouse coordinates into subtle rotation and translation
  const rotateY = useTransform(mouseX, [-1, 1], [-10, 10]);
  const rotateX = useTransform(mouseY, [-1, 1], [45 + 5, 45 - 5]); // Base is 45deg
  const translateX = useTransform(mouseX, [-1, 1], [-20, 20]);
  const translateY = useTransform(mouseY, [-1, 1], [-20, 20]);

  return (
    <div 
      ref={containerRef} 
      className="absolute inset-0 w-full h-full overflow-hidden flex items-center justify-center pointer-events-none"
      style={{ perspective: '1200px' }}
    >
      {/* Fallback flat SVG for mobile or reduced motion */}
      {isMobile || prefersReducedMotion ? (
        <div className="w-full h-full opacity-30 flex items-center justify-center">
          <TopologyGrid is3D={false} />
        </div>
      ) : (
        <motion.div 
          className="relative w-full h-full flex items-center justify-center origin-center"
          style={{ 
            rotateX, 
            rotateY,
            rotateZ: -15, // Base isometric tilt
            x: translateX,
            y: translateY,
            transformStyle: 'preserve-3d'
          }}
        >
          {/* Depth background grid */}
          <div 
            className="absolute inset-[-50%] bg-dot-topology opacity-20"
            style={{ transform: 'translateZ(-300px)' }}
          />
          
          <TopologyGrid is3D={true} />
        </motion.div>
      )}
    </div>
  );
};
