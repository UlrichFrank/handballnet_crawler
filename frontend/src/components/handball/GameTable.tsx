import React, { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';
import { StatCell } from './StatCell';

interface GameTableProps {
  league: LeagueConfig;
  teamName: string;
}

export function GameTable({ league, teamName }: GameTableProps) {
  const [players, setPlayers] = useState<string[]>([]);
  const [teamGames, setTeamGames] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await dataService.getGameData(league.out_name);

        const games = dataService.getTeamGames(data, teamName);
        setTeamGames(games);

        const teamPlayers = dataService.getTeamPlayers(games);
        setPlayers(teamPlayers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load game data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [league, teamName]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading game data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  if (teamGames.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-700">
        No games found for this team.
      </div>
    );
  }

  // Calculate stats labels (same as XLS)
  const statLabels = ['Tore', '7m Vers.', '7m Tore', '2-Min', 'Gelb', 'Rot', 'Blau'];
  const summaryLabels = ['Tore\nGesamt', '7m\nVers.', '7m\nTore', '2-Min\nGesamt', 'Gelb', 'Rot', 'Blau'];

  return (
    <div className="bg-white dark:bg-slate-950 rounded-lg shadow-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse table-auto">
          {/* Header Row with Game Info */}
          <thead>
            <tr>
              <th
                className="sticky left-0 z-20 bg-blue-900 dark:bg-blue-600 text-white px-4 py-3 text-left text-sm font-bold border border-blue-200 dark:border-blue-700 whitespace-nowrap"
                style={{ minWidth: '180px' }}
              >
                Player
              </th>
              {teamGames.map((game, idx) => (
                <th
                  key={`header_${idx}`}
                  colSpan={7}
                  className="bg-blue-900 dark:bg-blue-600 text-white px-3 py-3 text-center text-sm font-bold border border-blue-200 dark:border-blue-700"
                  style={{ minWidth: '260px' }}
                >
                  <div className="text-xs leading-tight">
                    <div className="font-semibold">{game.date}</div>
                    <div className="font-bold text-sm">{game.is_home ? '🏠' : '🏃'}</div>
                    <div className="text-xs font-bold">{game.score}</div>
                    <div className="text-xs font-normal truncate">vs {game.opponent}</div>
                  </div>
                </th>
              ))}
              <th
                colSpan={7}
                className="bg-blue-900 dark:bg-blue-600 text-white px-3 py-3 text-center text-xs font-bold border border-blue-200 dark:border-blue-700 whitespace-nowrap"
                style={{ minWidth: '260px' }}
              >
                <div className="leading-tight">Gesamt</div>
              </th>
            </tr>
            {/* Sub-header with stat labels */}
            <tr>
              <th className="sticky left-0 z-20 bg-blue-500 dark:bg-blue-700 text-white px-4 py-2 text-left text-xs font-semibold border border-blue-200 dark:border-blue-600" />
              {teamGames.map((_, gameIdx) =>
                statLabels.map((label) => (
                  <th
                    key={`sublabel_${gameIdx}_${label}`}
                    className="bg-blue-500 dark:bg-blue-700 text-white text-center text-xs font-semibold px-2 py-2 border border-blue-200 dark:border-blue-600 whitespace-nowrap"
                    style={{ minWidth: '36px' }}
                  >
                    {label.length > 6 ? label.split(' ')[0] : label}
                  </th>
                ))
              )}
              {summaryLabels.map((label) => (
                <th
                  key={`summary_${label}`}
                  className="bg-blue-500 dark:bg-blue-700 text-white text-center text-xs font-semibold px-2 py-2 border border-blue-200 dark:border-blue-600 whitespace-nowrap"
                  style={{ minWidth: '36px' }}
                >
                  {label.split('\n')[0]}
                </th>
              ))}
            </tr>
          </thead>

          {/* Player Rows */}
          <tbody>
            {players.map((playerName, playerIdx) => (
              <tr key={playerName} className={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900 hover:bg-blue-50 dark:hover:bg-slate-800' : 'bg-gray-50 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-slate-700'}>
                <td
                  className="sticky left-0 z-10 bg-inherit px-4 py-2 text-sm font-semibold border border-gray-200 dark:border-slate-700 text-gray-900 dark:text-gray-100 text-left whitespace-nowrap"
                  style={{ minWidth: '180px' }}
                >
                  {playerName}
                </td>

                {/* Game stats */}
                {teamGames.map((game, gameIdx) => {
                  const stats = dataService.getPlayerGameStats(game, playerName);
                  return (
                    <React.Fragment key={`game_${gameIdx}`}>
                      <StatCell
                        value={stats?.goals ?? null}
                        type="goals"
                        hasAttempts={stats?.seven_meters ?? 0}
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.seven_meters ?? null}
                        type="attempts"
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.seven_meters_goals ?? null}
                        type="seven_goals"
                        hasAttempts={stats?.seven_meters ?? 0}
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.two_min_penalties ?? null}
                        type="other"
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.yellow_cards ?? null}
                        type="other"
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.red_cards ?? null}
                        type="other"
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                      <StatCell
                        value={stats?.blue_cards ?? null}
                        type="other"
                        bgClass={playerIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                      />
                    </React.Fragment>
                  );
                })}

                {/* Summary stats */}
                {(() => {
                  const totalStats = dataService.getPlayerTotalStats(teamGames, playerName);
                  return (
                    <React.Fragment>
                      <StatCell
                        value={totalStats.goals}
                        type="goals"
                        hasAttempts={totalStats.seven_meters}
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.seven_meters}
                        type="attempts"
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.seven_meters_goals}
                        type="seven_goals"
                        hasAttempts={totalStats.seven_meters}
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.two_min_penalties}
                        type="other"
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.yellow_cards}
                        type="other"
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.red_cards}
                        type="other"
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                      <StatCell
                        value={totalStats.blue_cards}
                        type="other"
                        className={playerIdx % 2 === 0 ? 'bg-white' : 'bg-hb-playerGray2'}
                        bold
                      />
                    </React.Fragment>
                  );
                })()}
              </tr>
            ))}

            {/* GESAMT (Total) Row */}
            <tr className="bg-yellow-100 dark:bg-amber-900 font-bold">
              <td className="sticky left-0 z-10 bg-yellow-100 dark:bg-amber-900 px-4 py-3 text-sm font-bold border border-gray-200 dark:border-slate-700 text-gray-900 dark:text-amber-100">
                GESAMT
              </td>

              {teamGames.map((game, gameIdx) => {
                const totals = dataService.getGameTotals(game);
                return (
                  <React.Fragment key={`total_${gameIdx}`}>
                    <StatCell value={totals.goals} type="goals" hasAttempts={totals.seven_meters} total />
                    <StatCell value={totals.seven_meters} type="attempts" total />
                    <StatCell value={totals.seven_meters_goals} type="seven_goals" hasAttempts={totals.seven_meters} total />
                    <StatCell value={totals.two_min_penalties} type="other" total />
                    <StatCell value={totals.yellow_cards} type="other" total />
                    <StatCell value={totals.red_cards} type="other" total />
                    <StatCell value={totals.blue_cards} type="other" total />
                  </React.Fragment>
                );
              })}

              {/* Summary totals */}
              {(() => {
                const summaryTotals = {
                  goals: 0,
                  seven_meters: 0,
                  seven_meters_goals: 0,
                  two_min_penalties: 0,
                  yellow_cards: 0,
                  red_cards: 0,
                  blue_cards: 0,
                };

                teamGames.forEach((game) => {
                  const totals = dataService.getGameTotals(game);
                  summaryTotals.goals += totals.goals;
                  summaryTotals.seven_meters += totals.seven_meters;
                  summaryTotals.seven_meters_goals += totals.seven_meters_goals;
                  summaryTotals.two_min_penalties += totals.two_min_penalties;
                  summaryTotals.yellow_cards += totals.yellow_cards;
                  summaryTotals.red_cards += totals.red_cards;
                  summaryTotals.blue_cards += totals.blue_cards;
                });

                return (
                  <React.Fragment>
                    <StatCell value={summaryTotals.goals} type="goals" hasAttempts={summaryTotals.seven_meters} total />
                    <StatCell value={summaryTotals.seven_meters} type="attempts" total />
                    <StatCell value={summaryTotals.seven_meters_goals} type="seven_goals" hasAttempts={summaryTotals.seven_meters} total />
                    <StatCell value={summaryTotals.two_min_penalties} type="other" total />
                    <StatCell value={summaryTotals.yellow_cards} type="other" total />
                    <StatCell value={summaryTotals.red_cards} type="other" total />
                    <StatCell value={summaryTotals.blue_cards} type="other" total />
                  </React.Fragment>
                );
              })()}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
