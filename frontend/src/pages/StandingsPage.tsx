import { useLeague } from '../contexts/LeagueContext';
import { StandingsTable } from '../components/handball/StandingsTable';
import { CrossTable } from '../components/handball/CrossTable';
import { StandingsChart } from '../components/handball/StandingsChart';

export function StandingsPage() {
  const { selectedLeague } = useLeague();

  if (!selectedLeague) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">Keine Liga ausgewählt</div>
          <div className="text-gray-500 dark:text-gray-400">Bitte wähle eine Liga aus der Dropdown-Liste oben aus.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 dark:bg-slate-950 min-h-screen">
      <StandingsTable league={selectedLeague} />
      <CrossTable league={selectedLeague} />
      <StandingsChart league={selectedLeague} />
    </div>
  );
}
