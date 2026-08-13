
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
  const isFailed = data?.status === 'failed';
  const hasError = data?.error;

  let strokeColor = 'hsl(var(--border))';
  if (selected) strokeColor = 'hsl(var(--primary))';
  else if (hasError || isFailed) strokeColor = 'hsl(var(--destructive))';
  else if (isRunning) strokeColor = 'hsl(var(--primary))';

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
          ...(hasError ? {
            strokeDasharray: '4 4',
            animation: 'dashdraw 1s linear infinite reverse',
            stroke: 'hsl(var(--status-error))',
          } : {}),
        }}
        id={id}
      />
      
      {/* Premium Data flowing particles effect when running */}
      {isRunning && (
        <>
          <circle r="3" fill="hsl(var(--status-running))" filter="drop-shadow(0 0 4px hsl(var(--status-running)))">
            <animateMotion dur="1.5s" repeatCount="indefinite" path={edgePath} />
          </circle>
          <circle r="2" fill="#fff">
            <animateMotion dur="1.5s" repeatCount="indefinite" path={edgePath} />
          </circle>
        </>
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
            {String(data.label)}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
};
