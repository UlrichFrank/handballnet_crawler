
interface StatCellProps {
  value: number | null;
  type: 'goals' | 'attempts' | 'seven_goals' | 'other';
  hasAttempts?: number;
  className?: string;
  bgClass?: string;
  bold?: boolean;
  total?: boolean;
}

export function StatCell({
  value,
  type,
  hasAttempts = 0,
  className = '',
  bgClass = '',
  bold = false,
  total = false,
}: StatCellProps) {
  // Determine display value
  let displayValue: string | number = '-';

  if (value !== null && value !== undefined) {
    // Goals: always show number (0 becomes 0)
    if (type === 'goals') {
      displayValue = value;
    }
    // 7m Tore: show "-" if no 7m attempts
    else if (type === 'seven_goals') {
      displayValue = hasAttempts > 0 ? value : '-';
    }
    // Other stats: show "-" if 0
    else if (type === 'attempts' || type === 'other') {
      displayValue = value > 0 ? value : '-';
    }
  }

  // Determine hover class based on base background
  let hoverClass = '';
  if (bgClass.includes('bg-white')) {
    hoverClass = 'hover:bg-blue-50';
  } else if (bgClass.includes('bg-gray-50')) {
    hoverClass = 'hover:bg-blue-100';
  } else if (bgClass.includes('dark:bg-slate-900')) {
    hoverClass = 'dark:hover:bg-slate-700';
  } else if (bgClass.includes('dark:bg-slate-800')) {
    hoverClass = 'dark:hover:bg-slate-600';
  }

  const bgColorClass = total ? 'bg-yellow-100 dark:bg-amber-900 text-gray-900 dark:text-amber-100' : (bgClass || className);
  const textClass = bold ? 'font-bold' : '';

  return (
    <td
      className={`px-2 py-2 text-center text-sm border border-gray-200 dark:border-slate-700 ${bgColorClass} ${hoverClass} ${textClass}`}
      style={{ minWidth: '40px' }}
    >
      {displayValue}
    </td>
  );
}
