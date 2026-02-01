
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
        className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-hb-header focus:border-transparent appearance-none cursor-pointer bg-white"
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
