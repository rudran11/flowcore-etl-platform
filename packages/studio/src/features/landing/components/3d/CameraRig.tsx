import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useScroll, useTransform, useSpring } from 'framer-motion';
import * as THREE from 'three';

export const CameraRig: React.FC = () => {
  const { scrollYProgress } = useScroll();
  
  // Smooth out the scroll progress
  const smoothProgress = useSpring(scrollYProgress, { damping: 20, stiffness: 50 });

  // Map scroll progress to camera positions
  // 0% -> Hero (wide isometric)
  // 25% -> Build (push in to source/transform)
  // 50% -> Execute (low angle engine core)
  // 75% -> Observe (top down orthographic-ish)
  // 100% -> Ecosystem (structured grid)
  
  const camX = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [10, -4, 2, 0, 8]);
  const camY = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [8, 2, -1, 20, 6]);
  const camZ = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [15, 5, 6, 0, 12]);
  
  const targetX = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [0, -2, 0, 0, 0]);
  const targetY = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [0, 0, 0, 0, 0]);
  const targetZ = useTransform(smoothProgress, [0, 0.25, 0.5, 0.75, 1], [0, 0, 0, 0, 0]);

  const mousePosition = useRef({ x: 0, y: 0 });

  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Normalize to -1 to 1
      mousePosition.current = {
        x: (e.clientX / window.innerWidth) * 2 - 1,
        y: -(e.clientY / window.innerHeight) * 2 + 1
      };
    };
    
    // Only apply parallax if user hasn't reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (!mediaQuery.matches) {
      window.addEventListener('mousemove', handleMouseMove);
    }
    
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useFrame((state, delta) => {
    // Interpolate camera to the scroll-defined positions
    const targetCamPos = new THREE.Vector3(camX.get(), camY.get(), camZ.get());
    
    // Apply mouse parallax (subtle offset)
    targetCamPos.x += mousePosition.current.x * 2;
    targetCamPos.y += mousePosition.current.y * 2;

    // Smoothly move camera
    state.camera.position.lerp(targetCamPos, delta * 2);
    
    // Smoothly look at target
    const targetLookAt = new THREE.Vector3(targetX.get(), targetY.get(), targetZ.get());
    
    // We need to lerp the quaternion for smooth rotation changes
    const currentLookAt = new THREE.Vector3(0, 0, -1).applyQuaternion(state.camera.quaternion).add(state.camera.position);
    currentLookAt.lerp(targetLookAt, delta * 3);
    state.camera.lookAt(currentLookAt);
  });

  return null; // This component just drives the camera
};
