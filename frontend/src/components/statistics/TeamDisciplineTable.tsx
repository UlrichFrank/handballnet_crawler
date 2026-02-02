import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface TeamDisciplineStats {
  teamName: string;
  blueCards: number;
  redCards: number;
  twoMinPenalties: number;
  yellowCards: number;
  totalDisciplinePoints: number;
}

interface TeamDisciplineTableProps {
  league: LeagueConfig;
}

export function TeamDisciplineTable({ league }: TeamDisciplineTableProps) {
  const [teams, setTeams] = useState<TeamDisciplineStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const stats = await dataService.getTeamDisciplineStats(league.name);
        setTeams(stats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load team discipline statistics');
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
              <th className="px-4 py-3 text-center font-bold">🔵 Blau (4)</th>
              <th className="px-4 py-3 text-center font-bold">🔴 Rot (3)</th>
              <th className="px-4 py-3 text-center font-bold">⏱️ 2-Min (2)</th>
              <th className="px-4 py-3 text-center font-bold">🟡 Gelb (1)</th>
              <th className="px-4 py-3 text-center font-bold">Gesamt Punkte</th>
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
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-bold">{team.blueCards}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-bold">{team.redCards}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">{team.twoMinPenalties}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">{team.yellowCards}</td>
                <td className={`px-4 py-3 text-center font-bold ${
                  team.totalDisciplinePoints === 0 
                    ? 'text-green-600 dark:text-green-400' 
                    : team.totalDisciplinePoints <= 5
                    ? 'text-yellow-600 dark:text-yellow-400'
                    : 'text-red-600 dark:text-red-400'
                }`}>
                  {team.totalDisciplinePoints}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-3 bg-gray-50 dark:bg-slate-800 text-xs text-gray-600 dark:text-gray-400">
        Bewertung: Blau=4 Pkte | Rot=3 Pkte | 2-Min=2 Pkte | Gelb=1 Pkt. Weniger Punkte = Besser (Fair-Play)
      </div>
    </div>
  );
}
