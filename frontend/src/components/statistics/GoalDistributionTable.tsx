import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface GoalDistributionStats {
  teamName: string;
  avgGoalsPerPlayer: number;
  medianGoalsPerPlayer: number;
  giniCoefficient: number;
}

interface GoalDistributionTableProps {
  league: LeagueConfig;
}

export function GoalDistributionTable({ league }: GoalDistributionTableProps) {
  const [teams, setTeams] = useState<GoalDistributionStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const stats = await dataService.getGoalDistributionStats(league.name);
        // Sort by Gini coefficient (ascending - lower is better/more balanced)
        const sorted = stats.sort((a, b) => a.giniCoefficient - b.giniCoefficient);
        setTeams(sorted);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load goal distribution statistics');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [league]);

  if (loading) {
    return <div className="text-center text-gray-500 dark:text-gray-400 py-12">Loading...</div>;
  }

  if (error) {
    return <div className="text-red-600 dark:text-red-400 py-6">{error}</div>;
  }

  if (teams.length === 0) {
    return <div className="text-gray-500 dark:text-gray-400 py-6">Keine Teams gefunden</div>;
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-blue-900 dark:bg-blue-600 text-white">
              <th className="px-4 py-3 text-left font-bold">Rang</th>
              <th className="px-4 py-3 text-left font-bold">Team</th>
              <th className="px-4 py-3 text-center font-bold">Gini-Koeffizient</th>
              <th className="px-4 py-3 text-center font-bold">Ø Tore pro Spieler</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team, idx) => (
              <tr
                key={team.teamName}
                className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
              >
                <td className="px-4 py-3 font-bold text-blue-900 dark:text-blue-400">{idx + 1}</td>
                <td className="px-4 py-3 font-semibold text-gray-900 dark:text-gray-100">{team.teamName}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-semibold">{team.giniCoefficient.toFixed(3)}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-semibold">{team.avgGoalsPerPlayer.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-4 bg-gray-50 dark:bg-slate-800 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-slate-700">
        <p className="font-semibold mb-2">📊 Gini-Koeffizient:</p>
        <p>Der Gini-Koeffizient misst die Ungleichverteilung der Tore innerhalb einer Mannschaft. Ein Wert nahe 0 bedeutet, dass die Tore gleichmäßig auf die Spieler verteilt sind, während ein höherer Wert anzeigt, dass einige wenige Spieler die meisten Tore werfen. Teams mit niedrigen Werten haben eine ausgewogenere Offensivleistung.</p>
      </div>
    </div>
  );
}
