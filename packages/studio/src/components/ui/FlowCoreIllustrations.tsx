import React from 'react';

export const IllustrationNoPipelines: React.FC<{ className?: string }> = ({ className }) => (
  <svg viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <g opacity="0.4">
      {/* Topology Grid */}
      <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1" fill="currentColor" opacity="0.3" />
      </pattern>
      <rect width="200" height="120" fill="url(#grid)" />
      
      {/* Node 1 */}
      <rect x="20" y="40" width="40" height="40" rx="8" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" fill="transparent" />
      {/* Node 2 */}
      <rect x="80" y="40" width="40" height="40" rx="8" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" fill="transparent" />
      {/* Node 3 */}
      <rect x="140" y="40" width="40" height="40" rx="8" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" fill="transparent" />
      
      {/* Edges */}
      <path d="M60 60 L80 60" stroke="currentColor" strokeWidth="2" strokeDasharray="2 2" />
      <path d="M120 60 L140 60" stroke="currentColor" strokeWidth="2" strokeDasharray="2 2" />
    </g>
  </svg>
);

export const IllustrationNoDatasets: React.FC<{ className?: string }> = ({ className }) => (
  <svg viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
    <g opacity="0.4">
      <rect x="40" y="20" width="120" height="80" rx="8" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" fill="transparent" />
      <line x1="40" y1="45" x2="160" y2="45" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
      <line x1="70" y1="20" x2="70" y2="100" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
      <circle cx="100" cy="70" r="10" stroke="currentColor" strokeWidth="2" fill="transparent" />
    </g>
  </svg>
);
