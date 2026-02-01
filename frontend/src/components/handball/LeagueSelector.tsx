import { LeagueConfig } from '../../types/handball';

interface LeagueSelectorProps {
  leagues: LeagueConfig[];
  selectedLeague: LeagueConfig | null;
  onLeagueChange: (league: LeagueConfig) => void;
}

export function LeagueSelector({
  leagues,
  selectedLeague,
  onLeagueChange,
}: LeagueSelectorProps) {
  return (
    <select
      value={selectedLeague?.name || ''}
      onChange={(e) => {
        const league = leagues.find((l) => l.name === e.target.value);
        if (league) onLeagueChange(league);
      }}
      className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 hover:border-gray-400 dark:hover:border-slate-500 transition-colors appearance-none"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 10px center',
        paddingRight: '2.5rem',
      }}
    >
      <option value="">Select a league...</option>
      {leagues.map((league) => (
        <option key={league.name} value={league.name}>
          {league.display_name} ({league.age_group})
        </option>
      ))}
    </select>
  );
}
