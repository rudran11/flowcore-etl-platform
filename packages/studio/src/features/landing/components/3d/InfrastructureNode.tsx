import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface InfrastructureNodeProps {
  position: [number, number, number];
  type: 'source' | 'transform' | 'destination';
  status?: 'active' | 'idle' | 'queued';
  delay?: number; // for wake-up sequence
}

export const InfrastructureNode: React.FC<InfrastructureNodeProps> = ({ 
  position, 
  type, 
  status = 'idle',
  delay = 0 
}) => {
  const meshRef = useRef<THREE.Group>(null);
  
  // Base colors mapped to FlowCore design tokens
  const statusColors = {
    active: '#10b981', // Emerald
    idle: '#334155',   // Slate
    queued: '#f59e0b', // Amber
  };

  const glowColor = statusColors[status];

  useFrame((state) => {
    if (!meshRef.current) return;
    
    const time = state.clock.elapsedTime;
    
    // Wake up sequence based on delay
    if (time < delay) {
      meshRef.current.visible = false;
      return;
    } else {
      meshRef.current.visible = true;
    }

    // Very subtle hovering effect based on type
    const hoverAmplitude = type === 'transform' ? 0.15 : 0.05;
    meshRef.current.position.y = position[1] + Math.sin(time * 2 + position[0]) * hoverAmplitude;
  });

  return (
    <group ref={meshRef} position={position}>
      {/* Main Chassis */}
      <mesh position={[0, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[1.5, 0.4, 1.5]} />
        <meshStandardMaterial 
          color="#0f172a" 
          metalness={0.6} 
          roughness={0.7} 
        />
      </mesh>
      
      {/* Beveled Top Plate / LED Indicator */}
      <mesh position={[0, 0.21, 0]}>
        <boxGeometry args={[1.3, 0.02, 1.3]} />
        <meshStandardMaterial 
          color={glowColor}
          emissive={glowColor}
          emissiveIntensity={status === 'idle' ? 0.2 : 2.0}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>
    </group>
  );
};
