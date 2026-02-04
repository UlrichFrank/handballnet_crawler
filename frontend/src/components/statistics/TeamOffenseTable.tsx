import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface TeamOffenseStats {
  teamName: string;
  totalGoals: number;
  games: number;
  avgGoalsPerGame: number;
}

interface TeamOffenseTableProps {
  league: LeagueConfig;
}

export function TeamOffenseTable({ league }: TeamOffenseTableProps) {
  const [teams, setTeams] = useState<TeamOffenseStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const stats = await dataService.getTeamOffenseStats(league.name);
        setTeams(stats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Offensivstatistiken konnten nicht geladen werden');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [league]);

  if (loading) {
    return <div className="text-center text-gray-500 dark:text-gray-400 py-12">Laden...</div>;
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
              <th className="px-4 py-3 text-center font-bold">Gesamt-Tore</th>
              <th className="px-4 py-3 text-center font-bold">Spiele</th>
              <th className="px-4 py-3 text-center font-bold">Ø pro Spiel</th>
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
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-bold">{team.totalGoals}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">{team.games}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-semibold">{team.avgGoalsPerGame}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
