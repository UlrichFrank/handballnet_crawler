
interface TeamSelectorProps {
  teams: string[];
  selectedTeam: string | null;
  onSelectTeam: (team: string) => void;
}

export function TeamSelector({ teams, selectedTeam, onSelectTeam }: TeamSelectorProps) {
  return (
    <div className="relative">
      <select
        value={selectedTeam || ''}
        onChange={(e) => onSelectTeam(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none cursor-pointer bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 hover:border-gray-400 dark:hover:border-slate-500 transition-colors"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 10px center',
          paddingRight: '2.5rem',
        }}
      >
        <option value="">-- Select a team --</option>
        {teams.map((team) => (
          <option key={team} value={team}>
            {team}
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-2.5 pointer-events-none text-gray-500">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </div>
  );
}
