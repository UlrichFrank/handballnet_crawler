import { useRef, useEffect, useState, useMemo } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Game } from '../../types/handball';
import { GoalTooltip } from './GoalTooltip';

interface GameTimelineDialogProps {
  game: Game;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  halfDuration: number;
}

interface EnrichedGoal {
  time_in_minutes: number;
  scorer: string;
  momentum: number;
  situation: 'lead' | 'tie' | 'deficit';
  seven_meter: boolean;
  score_home: number;
  score_away: number;
}

interface HalfData {
  half: number;
  duration_minutes: number;
  home_goals: EnrichedGoal[];
  away_goals: EnrichedGoal[];
}

export function GameTimelineDialog({
  game,
  isOpen,
  onOpenChange,
  halfDuration,
}: GameTimelineDialogProps) {
  const graphicData = useMemo(() => {
    if (!game.goals_timeline || game.goals_timeline.length === 0) {
      return null;
    }

    // Calculate game flow
    const enrichedGoals: EnrichedGoal[] = [];
    let homeScore = 0;
    let awayScore = 0;
    let lastScorerTeam: string | null = null;
    let momentum = 1;

    for (const goal of game.goals_timeline) {
      if (goal.team === 'home') {
        homeScore += 1;
      } else {
        awayScore += 1;
      }

      let situation: 'lead' | 'tie' | 'deficit' = 'tie';
      if (goal.team === 'home') {
        situation = homeScore > awayScore ? 'lead' : homeScore === awayScore ? 'tie' : 'deficit';
      } else {
        situation = awayScore > homeScore ? 'lead' : awayScore === homeScore ? 'tie' : 'deficit';
      }

      if (lastScorerTeam === goal.team) {
        momentum += 1;
      } else {
        momentum = 1;
        lastScorerTeam = goal.team;
      }

      enrichedGoals.push({
        time_in_minutes: goal.minute + goal.second / 60,
        scorer: goal.scorer,
        momentum,
        situation,
        seven_meter: goal.seven_meter || false,
        score_home: homeScore,
        score_away: awayScore,
      });
    }

    // Organize into halves
    const halves: HalfData[] = [
      {
        half: 1,
        duration_minutes: halfDuration,
        home_goals: [],
        away_goals: [],
      },
      {
        half: 2,
        duration_minutes: halfDuration,
        home_goals: [],
        away_goals: [],
      },
    ];

    for (const goal of enrichedGoals) {
      const halfIdx = goal.time_in_minutes < halfDuration ? 0 : 1;
      const timeInMinutes = halfIdx === 0 ? goal.time_in_minutes : goal.time_in_minutes - halfDuration;

      const goalData: EnrichedGoal = {
        ...goal,
        time_in_minutes: timeInMinutes,
      };

      // Find original goal to determine team
      const originalGoalIndex = enrichedGoals.indexOf(goal);
      const originalGoal = game.goals_timeline![originalGoalIndex];

      if (originalGoal?.team === 'home') {
        halves[halfIdx].home_goals.push(goalData);
      } else {
        halves[halfIdx].away_goals.push(goalData);
      }
    }

    return halves;
  }, [game, halfDuration]);

  if (!graphicData) {
    return (
      <Dialog open={isOpen} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Spiel-Ablauf</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center text-gray-500">Keine Tordaten verfügbar</div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg">
            {game.home.team_name} vs {game.away.team_name}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-6 py-4">
          {graphicData.map((half) => (
            <TimelineHalf
              key={half.half}
              half={half}
              homeTeam={game.home.team_name}
              awayTeam={game.away.team_name}
            />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface TimelineHalfProps {
  half: HalfData;
  homeTeam: string;
  awayTeam: string;
}

interface CircleData {
  x: number;
  y: number;
  radius: number;
  goal: EnrichedGoal;
  team: 'home' | 'away';
}

function TimelineHalf({ half, homeTeam, awayTeam }: TimelineHalfProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredGoal, setHoveredGoal] = useState<CircleData | null>(null);
  const [canvasRect, setCanvasRect] = useState<DOMRect | null>(null);
  const circlesRef = useRef<CircleData[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    // Set canvas size based on container
    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    const width = rect.width;
    const height = width / 4; // 4:1 aspect ratio

    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    canvas.width = width * dpr;
    canvas.height = height * dpr;

    setCanvasRect(canvas.getBoundingClientRect());

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Scale context for HiDPI
    ctx.scale(dpr, dpr);

    const canvasWidth = width;
    const canvasHeight = height;

    // Clear canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Setup dimensions
    const marginLeft = 20;
    const marginRight = 20;
    const marginTop = 30;
    const marginBottom = 40;
    const graphWidth = canvasWidth - marginLeft - marginRight;
    const graphHeight = canvasHeight - marginTop - marginBottom;

    // Helper to get color for situation
    const getColor = (situation: string) => {
      switch (situation) {
        case 'lead':
          return '#3498db'; // Blue
        case 'tie':
          return '#95a5a6'; // Gray
        case 'deficit':
          return '#e67e22'; // Orange
        default:
          return '#95a5a6';
      }
    };

    // Helper to get circle radius from momentum
    const getRadius = (momentum: number) => {
      return 5 + momentum * 1.5;
    };

    // Draw time axis lines
    ctx.strokeStyle = '#cccccc';
    ctx.lineWidth = 1;

    // Top line
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop);
    ctx.lineTo(marginLeft + graphWidth, marginTop);
    ctx.stroke();

    // Middle separator line (dashed)
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop + graphHeight / 2);
    ctx.lineTo(marginLeft + graphWidth, marginTop + graphHeight / 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Bottom line
    ctx.beginPath();
    ctx.moveTo(marginLeft, marginTop + graphHeight);
    ctx.lineTo(marginLeft + graphWidth, marginTop + graphHeight);
    ctx.stroke();

    // Draw minute labels
    ctx.fillStyle = '#666666';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    for (let minute = 0; minute <= half.duration_minutes; minute += 5) {
      const x = marginLeft + (minute / half.duration_minutes) * graphWidth;
      ctx.fillText(`${(half.half - 1) * half.duration_minutes + minute}'`, x, marginTop - 10);
    }

    // Draw team labels
    ctx.font = 'bold 12px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillStyle = '#333333';
    ctx.fillText(homeTeam, marginLeft - 10, marginTop + graphHeight / 4 + 5);
    ctx.fillText(awayTeam, marginLeft - 10, marginTop + (3 * graphHeight) / 4 + 5);

    // Reset circles array
    circlesRef.current = [];

    // Draw home team goals (top half)
    for (const goal of half.home_goals) {
      const x = marginLeft + (goal.time_in_minutes / half.duration_minutes) * graphWidth;
      const y = marginTop + graphHeight / 4;
      const color = getColor(goal.situation);
      const radius = getRadius(goal.momentum);

      // Draw circle
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw edge
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Draw momentum number if > 3
      if (goal.momentum > 3) {
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(goal.momentum.toString(), x, y);
      }

      // Draw score label
      ctx.fillStyle = '#333333';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${goal.score_home}:${goal.score_away}`, x, y + radius + 15);

      // Store circle data for hit detection
      circlesRef.current.push({
        x,
        y,
        radius: radius + 5, // Increase hit area slightly for better UX
        goal,
        team: 'home',
      });
    }

    // Draw away team goals (bottom half)
    for (const goal of half.away_goals) {
      const x = marginLeft + (goal.time_in_minutes / half.duration_minutes) * graphWidth;
      const y = marginTop + (3 * graphHeight) / 4;
      const color = getColor(goal.situation);
      const radius = getRadius(goal.momentum);

      // Draw circle
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Draw edge
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Draw momentum number if > 3
      if (goal.momentum > 3) {
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(goal.momentum.toString(), x, y);
      }

      // Draw score label
      ctx.fillStyle = '#333333';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${goal.score_home}:${goal.score_away}`, x, y + radius + 15);

      // Store circle data for hit detection
      circlesRef.current.push({
        x,
        y,
        radius: radius + 5, // Increase hit area slightly for better UX
        goal,
        team: 'away',
      });
    }
  }, [half, homeTeam, awayTeam]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Scale to canvas coordinate system
    const dpr = window.devicePixelRatio || 1;
    const canvasX = x * dpr;
    const canvasY = y * dpr;

    // Check if any circle is hovered
    let foundGoal: CircleData | null = null;
    for (const circle of circlesRef.current) {
      const distance = Math.sqrt(Math.pow(canvasX - circle.x * dpr, 2) + Math.pow(canvasY - circle.y * dpr, 2));
      if (distance <= circle.radius * dpr) {
        foundGoal = {
          ...circle,
          x: circle.x,
          y: circle.y,
        };
        break;
      }
    }

    setHoveredGoal(foundGoal);
    canvas.style.cursor = foundGoal ? 'pointer' : 'default';
  };

  const handleMouseLeave = () => {
    setHoveredGoal(null);
    if (canvasRef.current) {
      canvasRef.current.style.cursor = 'default';
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-gray-50 dark:bg-slate-900">
      <h3 className="font-semibold text-sm mb-3 text-gray-900 dark:text-gray-100">
        Halbzeit {half.half} ({half.duration_minutes} Min)
      </h3>
      <div
        ref={containerRef}
        className="w-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded overflow-hidden"
        style={{
          aspectRatio: '4 / 1',
        }}
      >
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="w-full h-full block"
        />
      </div>
      {hoveredGoal && canvasRect && (
        <GoalTooltip
          goal={{
            scorer: hoveredGoal.goal.scorer,
            seven_meter: hoveredGoal.goal.seven_meter,
            minute: Math.floor(hoveredGoal.goal.time_in_minutes),
            second: Math.round((hoveredGoal.goal.time_in_minutes % 1) * 60),
            score_home: hoveredGoal.goal.score_home,
            score_away: hoveredGoal.goal.score_away,
          }}
          x={hoveredGoal.x}
          y={hoveredGoal.y}
          canvasRect={canvasRect}
        />
      )}
    </div>
  );
}
