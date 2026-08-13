import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface DataStream3DProps {
  start: [number, number, number];
  end: [number, number, number];
  color?: string;
  speed?: number;
}

export const DataStream3D: React.FC<DataStream3DProps> = ({ 
  start, 
  end, 
  color = '#10b981', // Emerald data flow
  speed = 1.0 
}) => {
  const lineMaterialRef = useRef<THREE.LineDashedMaterial>(null);

  // Create a smooth curve between start and end with an arc
  const curve = useMemo(() => {
    // Add a mid-point that arches slightly up and away
    const midX = (start[0] + end[0]) / 2;
    const midY = Math.max(start[1], end[1]) + 1.5;
    const midZ = (start[2] + end[2]) / 2;
    
    return new THREE.CatmullRomCurve3([
      new THREE.Vector3(...start),
      new THREE.Vector3(midX, midY, midZ),
      new THREE.Vector3(...end)
    ]);
  }, [start, end]);

  const geometry = useMemo(() => {
    // Extract points from the curve for the Line
    const points = curve.getPoints(50);
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [curve]);

  useFrame((_, delta) => {
    if (lineMaterialRef.current) {
      // Animate the dash offset backwards so particles flow from start to end
      (lineMaterialRef.current as any).dashOffset -= delta * speed * 2;
    }
  });

  return (
    <group>
      {/* Background faint path */}
      {/* @ts-expect-error: React 18 types enforce SVG line attributes, overriding R3F */}
      <line geometry={geometry as any}>
        <lineBasicMaterial color={color} transparent opacity={0.1} />
      </line>
      
      {/* Animated glowing particles on path */}
      {/* @ts-expect-error: React 18 types enforce SVG line attributes, overriding R3F */}
      <line geometry={geometry as any}>
        <lineDashedMaterial 
          ref={lineMaterialRef}
          color={color} 
          dashSize={0.5} 
          gapSize={1.5}
          transparent
          opacity={0.8}
        />
      </line>
    </group>
  );
};
