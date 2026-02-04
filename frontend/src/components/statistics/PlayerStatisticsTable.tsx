import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface PlayerStatistics {
  name: string;
  team: string;
  goals: number;
  sevenMetersGoals: number;
  sevenMetersAttempts: number;
  sevenMeterPercent: number;
  games: number;
}

interface PlayerStatisticsTableProps {
  league: LeagueConfig;
}

export function PlayerStatisticsTable({ league }: PlayerStatisticsTableProps) {
  const [players, setPlayers] = useState<PlayerStatistics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const stats = await dataService.getPlayerStatistics(league.name);
        setPlayers(stats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load player statistics');
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

  if (players.length === 0) {
    return <div className="text-gray-500 dark:text-gray-400 py-6">Keine Spieler gefunden</div>;
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg overflow-hidden">
      <div className="overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
        <table className="w-full">
          <thead className="sticky top-0">
            <tr className="bg-blue-900 dark:bg-blue-600 text-white">
              <th className="px-4 py-3 text-left font-bold">Rang</th>
              <th className="px-4 py-3 text-left font-bold">Name</th>
              <th className="px-4 py-3 text-left font-bold">Verein</th>
              <th className="px-4 py-3 text-center font-bold">Tore</th>
              <th className="px-4 py-3 text-center font-bold">7m Tore</th>
              <th className="px-4 py-3 text-center font-bold">7m Versuche</th>
              <th className="px-4 py-3 text-center font-bold">7m %</th>
              <th className="px-4 py-3 text-center font-bold">Spiele</th>
            </tr>
          </thead>
          <tbody>
            {players.map((player, idx) => (
              <tr
                key={`${player.name}-${player.team}`}
                className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
              >
                <td className="px-4 py-3 font-bold text-blue-900 dark:text-blue-400">{idx + 1}</td>
                <td className="px-4 py-3 font-semibold text-gray-900 dark:text-gray-100">{player.name}</td>
                <td className="px-4 py-3 text-gray-900 dark:text-gray-100 text-sm">{player.team}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-bold">{player.goals}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">{player.sevenMetersGoals}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">{player.sevenMetersAttempts}</td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-semibold">
                  {player.sevenMeterPercent}%
                </td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 font-semibold">{player.games}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-3 bg-gray-50 dark:bg-slate-800 text-sm text-gray-600 dark:text-gray-400">
        {players.length} Spieler insgesamt (10 pro Sichtfenster)
      </div>
    </div>
  );
}
