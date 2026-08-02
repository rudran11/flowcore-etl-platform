import React from 'react';
import { BaseEdge, EdgeProps, getBezierPath, EdgeLabelRenderer } from '@xyflow/react';

export const AnimatedEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
  selected,
}: EdgeProps) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isRunning = data?.status === 'running';
  const hasError = data?.status === 'error';
  const isSuccess = data?.status === 'success';

  let strokeColor = 'hsl(var(--border))';
  if (selected) strokeColor = 'hsl(var(--primary))';
  else if (hasError) strokeColor = 'hsl(var(--destructive))';
  else if (isSuccess) strokeColor = '#10b981';

  return (
    <>
      {/* Invisible thicker path for easier selection */}
      <BaseEdge
        path={edgePath}
        style={{ ...style, strokeWidth: 20, stroke: 'transparent', cursor: 'pointer' }}
      />
      
      {/* Main visible path */}
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: selected ? 2.5 : 1.5,
          stroke: strokeColor,
          transition: 'stroke 0.3s ease, stroke-width 0.3s ease',
          ...(isRunning && {
            strokeDasharray: '5, 5',
            animation: 'dashdraw 1s linear infinite',
            stroke: 'hsl(var(--primary))',
          }),
        }}
        id={id}
      />
      
      {/* Data flowing particles effect when running */}
      {isRunning && (
        <circle r="4" fill="hsl(var(--primary))">
          <animateMotion dur="2s" repeatCount="indefinite" path={edgePath} />
        </circle>
      )}

      {/* Optional: Add a label or status badge on the edge itself via EdgeLabelRenderer */}
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="bg-card border border-border/50 text-[10px] text-muted-foreground px-2 py-0.5 rounded shadow-sm font-medium"
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
};
