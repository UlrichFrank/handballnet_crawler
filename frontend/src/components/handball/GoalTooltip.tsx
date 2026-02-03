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
}

export function GoalTooltip({ goals, x, y, canvasRect }: GoalTooltipProps) {
  if (!canvasRect || goals.length === 0) return null;

  const tooltipWidth = 240;
  const tooltipHeight = 50 + goals.length * 70;
  const tooltipMargin = 10;
  const padding = 10;

  // Use absolute positioning relative to canvas
  let tooltipX = x - tooltipWidth / 2;
  let tooltipY = y - tooltipHeight - tooltipMargin;
  let arrowPosition: 'top' | 'bottom' = 'bottom';

  // Constrain within canvas bounds
  const canvasWidth = canvasRect.width;
  const canvasHeight = canvasRect.height;

  // Constrain horizontally
  if (tooltipX < padding) {
    tooltipX = padding;
  } else if (tooltipX + tooltipWidth > canvasWidth - padding) {
    tooltipX = canvasWidth - tooltipWidth - padding;
  }

  // Constrain vertically - try above first
  if (tooltipY + tooltipHeight <= canvasHeight - padding) {
    // Fits above
    if (tooltipY >= padding) {
      // Perfect fit above
      arrowPosition = 'bottom';
    } else {
      // Too high, try below
      tooltipY = y + tooltipMargin;
      arrowPosition = 'top';
    }
  } else {
    // Doesn't fit above, try below
    tooltipY = y + tooltipMargin;
    arrowPosition = 'top';
    
    if (tooltipY + tooltipHeight > canvasHeight - padding) {
      // Doesn't fit below either, constrain to fit
      tooltipY = canvasHeight - tooltipHeight - padding;
      // Recalculate arrow position
      if (tooltipY + tooltipHeight > y) {
        arrowPosition = 'top';
      } else {
        arrowPosition = 'bottom';
      }
    }
  }

  // Final safety check
  if (tooltipY < padding) {
    tooltipY = padding;
  }
  if (tooltipY + tooltipHeight > canvasHeight - padding) {
    tooltipY = canvasHeight - tooltipHeight - padding;
  }

  return (
    <div
      className="absolute z-50 bg-slate-900 dark:bg-slate-800 text-white rounded-lg shadow-2xl border border-slate-700 dark:border-slate-600 pointer-events-none"
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
