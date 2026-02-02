interface Goal {
  scorer: string;
  seven_meter: boolean;
  minute: number;
  second: number;
  score_home: number;
  score_away: number;
}

interface GoalTooltipProps {
  goals: Goal[];
  x: number;
  y: number;
  canvasRect: DOMRect | null;
  dialogRect?: DOMRect | null;
}

export function GoalTooltip({ goals, x, y, canvasRect, dialogRect }: GoalTooltipProps) {
  if (!canvasRect || goals.length === 0) return null;

  // Convert canvas coordinates to screen coordinates
  const screenX = canvasRect.left + x;
  const screenY = canvasRect.top + y;

  const tooltipWidth = 240;
  const tooltipHeight = 50 + goals.length * 70;
  const tooltipMargin = 10;
  const padding = 10; // Minimum distance from edge

  let tooltipX = screenX - tooltipWidth / 2;
  let tooltipY = screenY - tooltipHeight - tooltipMargin;
  let arrowPosition: 'top' | 'bottom' = 'bottom';

  // Use dialog bounds if available, otherwise use viewport bounds
  const bounds = dialogRect ? {
    left: dialogRect.left + padding,
    right: dialogRect.right - padding,
    top: dialogRect.top + padding,
    bottom: dialogRect.bottom - padding,
  } : {
    left: padding,
    right: window.innerWidth - padding,
    top: padding,
    bottom: window.innerHeight - padding,
  };

  // Constrain horizontally first (simpler)
  if (tooltipX < bounds.left) {
    tooltipX = bounds.left;
  } else if (tooltipX + tooltipWidth > bounds.right) {
    tooltipX = bounds.right - tooltipWidth;
  }

  // Constrain vertically - try above first
  if (tooltipY + tooltipHeight <= bounds.bottom) {
    // Fits above
    if (tooltipY >= bounds.top) {
      // Perfect fit above
      arrowPosition = 'bottom';
    } else {
      // Too high, try below
      tooltipY = screenY + tooltipMargin;
      arrowPosition = 'top';
    }
  } else {
    // Doesn't fit above, try below
    tooltipY = screenY + tooltipMargin;
    arrowPosition = 'top';
    
    if (tooltipY + tooltipHeight > bounds.bottom) {
      // Doesn't fit below either, constrain to fit
      tooltipY = bounds.bottom - tooltipHeight;
      // Recalculate arrow position based on actual placement
      if (tooltipY + tooltipHeight > screenY) {
        arrowPosition = 'top';
      } else {
        arrowPosition = 'bottom';
      }
    }
  }

  // Final safety check: ensure we don't go above bounds
  if (tooltipY < bounds.top) {
    tooltipY = bounds.top;
  }
  if (tooltipY + tooltipHeight > bounds.bottom) {
    tooltipY = bounds.bottom - tooltipHeight;
  }

  return (
    <div
      className="fixed z-50 bg-slate-900 dark:bg-slate-800 text-white rounded-lg shadow-2xl border border-slate-700 dark:border-slate-600 pointer-events-none"
      style={{
        left: `${tooltipX}px`,
        top: `${tooltipY}px`,
        width: `${tooltipWidth}px`,
      }}
    >
      <div className="p-3 space-y-3 text-sm">
        {goals.length > 1 && (
          <div className="text-xs text-yellow-300 font-semibold border-b border-slate-600 pb-2">
            {goals.length} Tore gleichzeitig
          </div>
        )}
        {goals.map((goal, idx) => {
          const timeString = `${String(goal.minute).padStart(2, '0')}:${String(goal.second).padStart(2, '0')}`;
          const goalType = goal.seven_meter ? '7-Meter' : 'aus dem Spiel';

          return (
            <div key={idx} className="pb-2 last:pb-0 border-b border-slate-600 last:border-b-0">
              <div className="font-bold text-blue-300">{goal.scorer}</div>
              <div className="text-xs text-gray-300 space-y-0.5">
                <div>⏱ {timeString}</div>
                <div>📍 {goalType}</div>
                <div className="text-yellow-200 font-semibold">Spielstand: {goal.score_home}:{goal.score_away}</div>
              </div>
            </div>
          );
        })}
      </div>
      {/* Arrow pointing to goal */}
      {arrowPosition === 'bottom' && (
        <div
          className="absolute w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-slate-900 dark:border-t-slate-800"
          style={{
            left: `${tooltipWidth / 2 - 4}px`,
            bottom: '-4px',
          }}
        />
      )}
      {arrowPosition === 'top' && (
        <div
          className="absolute w-0 h-0 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-slate-900 dark:border-b-slate-800"
          style={{
            left: `${tooltipWidth / 2 - 4}px`,
            top: '-4px',
          }}
        />
      )}
    </div>
  );
}
