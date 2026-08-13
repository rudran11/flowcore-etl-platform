import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import { EngineCore3D } from './EngineCore3D';
import { InfrastructureNode } from './InfrastructureNode';
import { DataStream3D } from './DataStream3D';
import { CameraRig } from './CameraRig';

export const FlowCoreScene: React.FC = () => {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none bg-background">
      <Canvas
        camera={{ position: [10, 8, 15], fov: 45 }}
        dpr={[1, Math.min(window.devicePixelRatio, 1.5)]} // Limit DPR for performance
        gl={{ antialias: false }} // Bloom handles some smoothing, disable native AA if performance needed, but let's leave it on for now
      >
        <color attach="background" args={['#050505']} />
        <fog attach="fog" args={['#050505', 10, 40]} />
        
        <ambientLight intensity={0.1} />
        <directionalLight 
          position={[-10, 10, -5]} 
          intensity={3.0} 
          color="#ffffff" 
          castShadow
        />
        <hemisphereLight intensity={0.2} color="#3b82f6" groundColor="#0f172a" />
        {/* Dramatic Rim Light */}
        <spotLight position={[0, 10, -10]} intensity={5.0} color="#10b981" />

        <Suspense fallback={null}>
          <CameraRig />

          <group>
            <EngineCore3D position={[0, 0, 0]} />

            {/* Source Nodes */}
            <InfrastructureNode position={[-8, 2, -4]} type="source" status="active" delay={0.4} />
            <InfrastructureNode position={[-8, -1, -2]} type="source" status="idle" delay={0.4} />

            {/* Transform Nodes */}
            <InfrastructureNode position={[-3, 0, 0]} type="transform" status="active" delay={0.8} />
            <InfrastructureNode position={[-3, 3, -1]} type="transform" status="queued" delay={0.8} />

            {/* Destination Nodes */}
            <InfrastructureNode position={[6, -2, 2]} type="destination" status="active" delay={1.6} />
            <InfrastructureNode position={[6, 2, 4]} type="destination" status="idle" delay={1.6} />

            {/* Data Streams (Simulated) */}
            <DataStream3D start={[-8, 2, -4]} end={[-3, 0, 0]} color="#10b981" speed={2} />
            <DataStream3D start={[-8, -1, -2]} end={[-3, 0, 0]} color="#10b981" speed={1.5} />
            
            <DataStream3D start={[-3, 0, 0]} end={[0, 0, 0]} color="#3b82f6" speed={3} />
            <DataStream3D start={[-3, 3, -1]} end={[0, 0, 0]} color="#f59e0b" speed={1} />

            <DataStream3D start={[0, 0, 0]} end={[6, -2, 2]} color="#10b981" speed={2.5} />
            <DataStream3D start={[0, 0, 0]} end={[6, 2, 4]} color="#3b82f6" speed={2} />
          </group>

          <EffectComposer>
            <Bloom 
              luminanceThreshold={0.4} 
              mipmapBlur 
              intensity={2.0} 
            />
          </EffectComposer>
        </Suspense>
      </Canvas>
    </div>
  );
};

export default FlowCoreScene;
