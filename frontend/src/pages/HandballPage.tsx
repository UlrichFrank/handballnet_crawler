import { useState, useEffect } from 'react';
import { dataService } from '../services/dataService';
import { useLeague } from '../contexts/LeagueContext';
import { TeamSelector } from '../components/handball/TeamSelector';
import { GameTable } from '../components/handball/GameTable';

export function HandballPage() {
  const { selectedLeague } = useLeague();
  const [teams, setTeams] = useState<string[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Load teams when league changes
  useEffect(() => {
    const loadTeams = async () => {
      if (!selectedLeague) return;
      try {
        const fetchedTeams = await dataService.getTeamsForLeague(selectedLeague.out_name);
        setTeams(fetchedTeams);
        setSelectedTeam(fetchedTeams.length > 0 ? fetchedTeams[0] : null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load teams');
      }
    };

    loadTeams();
  }, [selectedLeague]);

  if (!selectedLeague) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">No League Selected</div>
          <div className="text-gray-500 dark:text-gray-400">Please select a league from the dropdown above.</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">Error</div>
          <div className="text-gray-700 dark:text-gray-300">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 dark:bg-slate-950 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Handball Statistics</h1>
        <p className="text-gray-600 dark:text-gray-400">View team games and player statistics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Team</label>
          <TeamSelector
            teams={teams}
            selectedTeam={selectedTeam}
            onSelectTeam={setSelectedTeam}
          />
        </div>
      </div>

      {selectedLeague && selectedTeam && (
        <GameTable league={selectedLeague} teamName={selectedTeam} />
      )}
    </div>
  );
}
