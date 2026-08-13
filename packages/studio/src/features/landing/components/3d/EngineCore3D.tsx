import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export const EngineCore3D: React.FC<{ position?: [number, number, number] }> = ({ position = [0, 0, 0] }) => {
  const outerRingRef = useRef<THREE.Group>(null);
  const midRingRef = useRef<THREE.Group>(null);
  const innerRingRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (outerRingRef.current) outerRingRef.current.rotation.y += delta * 0.05;
    if (midRingRef.current) midRingRef.current.rotation.y -= delta * 0.08;
    if (innerRingRef.current) innerRingRef.current.rotation.y += delta * 0.15;
    
    // Subtle core pulse
    if (coreRef.current) {
      const material = coreRef.current.material as THREE.MeshPhysicalMaterial;
      material.emissiveIntensity = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.5;
    }
  });

  return (
    <group position={position}>
      {/* Central Glass Core */}
      <mesh ref={coreRef} position={[0, 0, 0]}>
        <cylinderGeometry args={[1, 1, 4, 32]} />
        <meshPhysicalMaterial 
          color="#1e293b" 
          emissive="#3b82f6"
          emissiveIntensity={1}
          metalness={0.9} 
          roughness={0.1}
          transmission={0.9}
          thickness={2.0}
        />
      </mesh>

      {/* Inner Structural Struts */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[1.2, 1.2, 4.2, 6, 1, true]} />
        <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.7} wireframe />
      </mesh>

      {/* Outer Ring */}
      <group ref={outerRingRef} position={[0, 0, 0]}>
        <mesh>
          <torusGeometry args={[2.5, 0.1, 16, 64]} />
          <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.4} />
        </mesh>
        {/* Ring Accent Nodes */}
        {[0, 1, 2].map((i) => (
          <mesh key={i} position={[Math.cos(i * (Math.PI * 2) / 3) * 2.5, 0, Math.sin(i * (Math.PI * 2) / 3) * 2.5]}>
            <boxGeometry args={[0.3, 0.3, 0.3]} />
            <meshStandardMaterial color="#1e293b" emissive="#3b82f6" emissiveIntensity={2} />
          </mesh>
        ))}
      </group>

      {/* Mid Ring */}
      <group ref={midRingRef} position={[0, -1, 0]}>
        <mesh>
          <torusGeometry args={[1.8, 0.08, 16, 64]} />
          <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.4} />
        </mesh>
      </group>

      {/* Inner Ring */}
      <group ref={innerRingRef} position={[0, 1.5, 0]}>
        <mesh>
          <torusGeometry args={[1.4, 0.05, 16, 64]} />
          <meshStandardMaterial color="#3b82f6" emissive="#3b82f6" emissiveIntensity={2} />
        </mesh>
      </group>
    </group>
  );
};
