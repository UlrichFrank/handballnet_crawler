import { useState, useEffect } from 'react';
import { useLeague } from '../contexts/LeagueContext';
import { dataService } from '../services/dataService';
import { GameHighlightUtils, useNavigateWithHighlight } from '../hooks/useGameHighlight';

interface GameInfo {
  date: string;
  home: string;
  away: string;
  score: string;
}

interface OfficialData {
  name: string;
  count: number;
  games: GameInfo[];
}

export function OfficialsPage() {
  const { selectedLeague } = useLeague();
  const navigateWithHighlight = useNavigateWithHighlight();
  const [referees, setReferees] = useState<OfficialData[]>([]);
  const [timekeepers, setTimekeepers] = useState<OfficialData[]>([]);
  const [secretaries, setSecretaries] = useState<OfficialData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOfficials = async () => {
      if (!selectedLeague) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const officials = await dataService.getAllOfficials(selectedLeague.name);

        // Convert maps to sorted arrays
        setReferees(
          Array.from(officials.referees.entries())
            .map(([name, data]) => ({ name, count: data.count, games: data.games }))
            .sort((a, b) => b.count - a.count)
        );

        setTimekeepers(
          Array.from(officials.timekeepers.entries())
            .map(([name, data]) => ({ name, count: data.count, games: data.games }))
            .sort((a, b) => b.count - a.count)
        );

        setSecretaries(
          Array.from(officials.secretaries.entries())
            .map(([name, data]) => ({ name, count: data.count, games: data.games }))
            .sort((a, b) => b.count - a.count)
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load officials');
      } finally {
        setLoading(false);
      }
    };

    loadOfficials();
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500 dark:text-gray-400">Loading officials...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded-lg p-4 text-red-700 dark:text-red-200">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  const renderOfficialsTable = (officials: OfficialData[], emptyMessage: string) => {
    if (officials.length === 0) {
      return (
        <div className="text-gray-500 dark:text-gray-400 italic py-6 text-center">
          {emptyMessage}
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100 dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700">
              <th className="px-4 py-3 text-left font-bold text-gray-900 dark:text-gray-100">Name</th>
              <th className="px-4 py-3 text-center font-bold text-gray-900 dark:text-gray-100 w-24">Spiele</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900 dark:text-gray-100">Spiele</th>
            </tr>
          </thead>
          <tbody>
            {officials.map((official, idx) => (
              <tr
                key={official.name}
                className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
              >
                <td className="px-4 py-3 text-gray-900 dark:text-gray-100 font-semibold border-b border-gray-200 dark:border-slate-700">
                  {official.name}
                </td>
                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700 font-bold">
                  {official.count}
                </td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-slate-700">
                  <div className="flex flex-wrap gap-2">
                    {official.games.map((game, gidx) => (
                      <button
                        key={`${official.name}-${gidx}`}
                        onClick={() => {
                          const encodedGame = GameHighlightUtils.encodeGame({
                            date: game.date,
                            home: game.home,
                            away: game.away,
                          });
                          navigateWithHighlight('/handball', 'game', encodedGame);
                        }}
                        className="inline-block bg-blue-50 dark:bg-blue-900/30 text-blue-900 dark:text-blue-200 px-2 py-1 rounded text-xs border border-blue-200 dark:border-blue-700 hover:bg-blue-100 dark:hover:bg-blue-900/50 cursor-pointer transition-colors"
                      >
                        {game.date}: {game.home} vs {game.away} ({game.score})
                      </button>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="space-y-6 p-6 bg-gray-50 dark:bg-slate-950 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Spielleitung</h1>
        <p className="text-gray-600 dark:text-gray-400">Übersicht der Schiedsrichter, Zeitnehmer und Sekretäre</p>
      </div>

      <div className="space-y-6">
        {/* Referees */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">🏆 Schiedsrichter</h2>
          {renderOfficialsTable(referees, 'Keine Schiedsrichter gefunden')}
        </div>

        {/* Timekeepers */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">⏱️ Zeitnehmer</h2>
          {renderOfficialsTable(timekeepers, 'Keine Zeitnehmer gefunden')}
        </div>

        {/* Secretaries */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">📋 Sekretäre</h2>
          {renderOfficialsTable(secretaries, 'Keine Sekretäre gefunden')}
        </div>
      </div>
    </div>
  );
}
