import { useLeague } from '../contexts/LeagueContext';
import { StandingsTable } from '../components/handball/StandingsTable';

export function StandingsPage() {
  const { selectedLeague } = useLeague();

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

  return (
    <div className="space-y-6 p-6 bg-gray-50 dark:bg-slate-950 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Tabelle</h1>
        <p className="text-gray-600 dark:text-gray-400">Liga-Standings und Rankings</p>
      </div>

      <StandingsTable league={selectedLeague} />
    </div>
  );
}
