import React from 'react';

// Coordinates must match the Node x,y positions + offset for centering
// src1: -300, -150
// src2: -250, 150
// tf1: 0, -50
// tf2: 50, 100
// dst1: 300, -100

export const DataFlowSVG: React.FC<{ is3D: boolean }> = ({ is3D }) => {
  // We use a relative SVG box 1000x600, centered at 0,0
  
  const Edge = ({ id, d, duration = "2s", color = "var(--primary)" }: { id: string, d: string, duration?: string, color?: string }) => (
    <>
      <path 
        id={id}
        d={d} 
        fill="none" 
        stroke={color} 
        strokeWidth={is3D ? "3" : "2"} 
        strokeOpacity="0.2" 
        strokeLinecap="round"
      />
      
      {/* Particle 1 */}
      <circle r="3" fill={color} filter="drop-shadow(0 0 6px currentColor)">
        <animateMotion dur={duration} repeatCount="indefinite" path={d} />
      </circle>
      
      {/* Particle 2 (Offset by half duration) */}
      <circle r="2" fill="#fff" opacity="0.8">
        <animateMotion dur={duration} begin={`${parseFloat(duration)/2}s`} repeatCount="indefinite" path={d} />
      </circle>
    </>
  );

  return (
    <svg 
      viewBox="-500 -300 1000 600" 
      className="w-full h-full overflow-visible"
    >
      <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>
      
      {/* src1 to tf1 */}
      <Edge 
        id="path1" 
        d="M -204 -150 C -100 -150, -100 -50, 0 -50" 
        duration="2s"
        color="hsl(217, 91%, 60%)" 
      />
      
      {/* src2 to tf1 */}
      <Edge 
        id="path2" 
        d="M -154 150 C -50 150, -50 -50, 0 -50" 
        duration="2.5s"
        color="hsl(217, 91%, 60%)" 
      />
      
      {/* tf1 to tf2 */}
      <Edge 
        id="path3" 
        d="M 96 -50 C 150 -50, 0 100, 50 100" 
        duration="1.5s"
        color="hsl(160, 84%, 39%)" 
      />
      
      {/* tf1 to dst1 */}
      <Edge 
        id="path4" 
        d="M 96 -50 C 200 -50, 200 -100, 300 -100" 
        duration="1.8s"
        color="hsl(160, 84%, 39%)" 
      />
      
      {/* tf2 to dst1 */}
      <Edge 
        id="path5" 
        d="M 146 100 C 200 100, 200 -100, 300 -100" 
        duration="2.2s"
        color="hsl(160, 84%, 39%)" 
      />
    </svg>
  );
};
