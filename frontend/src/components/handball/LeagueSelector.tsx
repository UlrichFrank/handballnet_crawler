import { LeagueConfig } from '../../types/handball';

interface LeagueSelectorProps {
  leagues: LeagueConfig[];
  selectedLeague: LeagueConfig | null;
  onLeagueChange: (league: LeagueConfig) => void;
}

export function LeagueSelector({ leagues, selectedLeague, onLeagueChange }: LeagueSelectorProps) {
  return (
    <div className="relative">
      <select
        value={selectedLeague?.name || ''}
        onChange={(e) => {
          const league = leagues.find((l) => l.name === e.target.value);
          if (league) onLeagueChange(league);
        }}
        className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100"
      >
        {leagues.map((league) => (
          <option key={league.name} value={league.name}>
            {league.display_name} ({league.age_group})
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-2.5 pointer-events-none text-gray-500 dark:text-gray-400">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </div>
  );
}
