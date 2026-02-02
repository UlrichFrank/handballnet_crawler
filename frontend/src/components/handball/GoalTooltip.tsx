interface GoalTooltipProps {
  goal: {
    scorer: string;
    seven_meter: boolean;
    minute: number;
    second: number;
    score_home: number;
    score_away: number;
  };
  x: number; // Canvas pixel position
  y: number;
  canvasRect: DOMRect | null;
}

export function GoalTooltip({ goal, x, y, canvasRect }: GoalTooltipProps) {
  if (!canvasRect) return null;

  // Convert canvas coordinates to screen coordinates
  const screenX = canvasRect.left + x;
  const screenY = canvasRect.top + y;

  // Calculate tooltip position (try above, fallback below)
  const tooltipWidth = 200;
  const tooltipHeight = 100;
  const tooltipMargin = 10;

  let tooltipX = screenX - tooltipWidth / 2; // Center horizontally
  let tooltipY = screenY - tooltipHeight - tooltipMargin; // Above the point

  // Fallback: if too close to top, show below
  if (tooltipY < 10) {
    tooltipY = screenY + tooltipMargin;
  }

  // Fallback: if too close to left/right edges
  if (tooltipX < 10) {
    tooltipX = 10;
  } else if (tooltipX + tooltipWidth > window.innerWidth - 10) {
    tooltipX = window.innerWidth - tooltipWidth - 10;
  }

  const timeString = `${String(goal.minute).padStart(2, '0')}:${String(goal.second).padStart(2, '0')}`;
  const goalType = goal.seven_meter ? '7-Meter' : 'aus dem Spiel';

  return (
    <div
      className="fixed z-50 bg-slate-900 dark:bg-slate-700 text-white rounded-lg shadow-xl border border-slate-700 dark:border-slate-600 pointer-events-none"
      style={{
        left: `${tooltipX}px`,
        top: `${tooltipY}px`,
        width: `${tooltipWidth}px`,
      }}
    >
      <div className="p-3 space-y-1 text-sm">
        <div className="font-bold text-blue-300">{goal.scorer}</div>
        <div className="text-xs text-gray-300">
          <div>Zeit: {timeString}</div>
          <div>Art: {goalType}</div>
          <div className="mt-1 pt-1 border-t border-slate-600">
            Stand: {goal.score_home}:{goal.score_away}
          </div>
        </div>
      </div>
      {/* Arrow pointing to goal */}
      <div
        className="absolute w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-slate-900 dark:border-t-slate-700"
        style={{
          left: `${tooltipWidth / 2 - 4}px`,
          bottom: tooltipY > screenY ? 'auto' : '-4px',
          top: tooltipY > screenY ? '-4px' : 'auto',
        }}
      />
    </div>
  );
}
