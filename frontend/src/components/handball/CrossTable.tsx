import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface CrossTableProps {
    league: LeagueConfig;
}

// First (label) column fixed width
const FIRST_COL_W = 216; // px  (3× the ~48px data cols, then +50%)
// Header row height = first column width (gives rotated names enough room)
const HEADER_ROW_H = 216; // px  (+50% of previous 144px)
// Body rows: fixed equal height
const ROW_H = 40; // px

export function CrossTable({ league }: CrossTableProps) {
    const [teams, setTeams] = useState<string[]>([]);
    const [gameMap, setGameMap] = useState<Map<string, { score?: string; date: string }>>(new Map());
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                const gameData = await dataService.getAggregatedGameData(league.name);
                const allTeams = await dataService.getTeamsForLeague(league.name);
                setTeams(allTeams);

                const map = new Map<string, { score?: string; date: string }>();
                gameData.games.forEach((game: any) => {
                    const homeTeam = game.home.team_name;
                    const awayTeam = game.away.team_name;
                    const key = `${homeTeam}|${awayTeam}`;

                    let score: string | undefined = undefined;
                    if (
                        game.home.players &&
                        game.away.players &&
                        (game.home.players.length > 0 || game.away.players.length > 0)
                    ) {
                        const homeGoals = game.home.players.reduce((sum: number, p: any) => sum + p.goals, 0);
                        const awayGoals = game.away.players.reduce((sum: number, p: any) => sum + p.goals, 0);
                        score = `${homeGoals}:${awayGoals}`;
                    }

                    let formattedDate = '';
                    if (game.date) {
                        const parts = game.date.split('.');
                        formattedDate = parts.length >= 2 ? `${parts[0]}.${parts[1]}.` : game.date;
                    }

                    map.set(key, { score, date: formattedDate });
                });
                setGameMap(map);
            } catch (err) {
                console.error('Failed to load cross table data:', err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [league]);

    if (loading) {
        return <div className="text-center py-8 text-gray-500">Lade Kreuztabelle...</div>;
    }

    return (
        <div>
            {/* Title and description outside the table card */}
            <div>
                <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Kreuztabelle</h1>
                <p className="text-gray-600 dark:text-gray-400">Heimmannschaft (vertikal) vs. Gastmannschaft (horizontal)</p>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg overflow-hidden">
                <div className="overflow-x-auto">
                    {/*
                     * table-layout: fixed + width: 100%
                     *   → first column gets FIRST_COL_W, remaining space is split equally
                     *     among all other columns (no explicit width set on them).
                     */}
                    <table
                        className="border-collapse w-full"
                        style={{ tableLayout: 'fixed' }}
                    >
                        <colgroup>
                            {/* First column: fixed width */}
                            <col style={{ width: `${FIRST_COL_W}px` }} />
                            {/* Data columns: no explicit width → share remaining space equally */}
                            {teams.map((t) => (
                                <col key={t} />
                            ))}
                        </colgroup>

                        <thead>
                            <tr style={{ height: `${HEADER_ROW_H}px` }}>
                                {/* Empty top-left corner */}
                                <th className="bg-blue-900 dark:bg-blue-600 border border-blue-800 dark:border-blue-700 p-1" />

                                {teams.map((team) => (
                                    <th
                                        key={team}
                                        className="bg-blue-900 dark:bg-blue-600 border border-blue-800 dark:border-blue-700 font-bold overflow-hidden"
                                        style={{ padding: 0, position: 'relative' }}
                                    >
                                        {/*
                                         * position: absolute; bottom anchors the wrapper to the
                                         * physical BOTTOM of the cell. The writing-mode div grows
                                         * upward from there. After rotate(180°), text start is
                                         * always at the VISUAL bottom — for both single and wrapped.
                                         */}
                                        <div style={{
                                            position: 'absolute',
                                            bottom: 4,
                                            left: 0,
                                            right: 0,
                                            display: 'flex',
                                            justifyContent: 'center',
                                        }}>
                                            <div
                                                className="text-xs font-bold text-white"
                                                style={{
                                                    writingMode: 'vertical-rl',
                                                    transform: 'rotate(180deg)',
                                                    overflowWrap: 'break-word',
                                                    wordBreak: 'break-word',
                                                    hyphens: 'auto',
                                                    lineHeight: '1.2',
                                                    maxHeight: `${HEADER_ROW_H - 12}px`,
                                                    overflow: 'hidden',
                                                }}
                                            >
                                                {team}
                                            </div>
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>

                        <tbody>
                            {teams.map((homeTeam, rowIdx) => (
                                <tr
                                    key={homeTeam}
                                    style={{ height: `${ROW_H}px` }}
                                    className={rowIdx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                                >
                                    {/* First column: home team label, styled like header */}
                                    <th
                                        className="bg-blue-900 dark:bg-blue-600 text-white border border-blue-800 dark:border-blue-700 p-2 text-xs font-bold text-left align-middle overflow-hidden"
                                        style={{
                                            overflowWrap: 'break-word',
                                            wordBreak: 'break-word',
                                            hyphens: 'auto',
                                            lineHeight: '1.3',
                                        }}
                                    >
                                        {homeTeam}
                                    </th>

                                    {teams.map((awayTeam) => {
                                        if (homeTeam === awayTeam) {
                                            return (
                                                <td
                                                    key={`${homeTeam}-${awayTeam}`}
                                                    className="border border-gray-200 dark:border-slate-700 bg-gray-200 dark:bg-slate-950 text-center font-bold text-gray-400 text-xs"
                                                >
                                                    -
                                                </td>
                                            );
                                        }

                                        const game = gameMap.get(`${homeTeam}|${awayTeam}`);
                                        if (!game) {
                                            return (
                                                <td
                                                    key={`${homeTeam}-${awayTeam}`}
                                                    className="border border-gray-200 dark:border-slate-700"
                                                />
                                            );
                                        }

                                        if (game.score) {
                                            return (
                                                <td
                                                    key={`${homeTeam}-${awayTeam}`}
                                                    className="border border-gray-200 dark:border-slate-700 text-center text-xs font-semibold text-gray-900 dark:text-gray-100"
                                                >
                                                    {game.score}
                                                </td>
                                            );
                                        }

                                        return (
                                            <td
                                                key={`${homeTeam}-${awayTeam}`}
                                                className="border border-gray-200 dark:border-slate-700 text-center text-xs bg-gray-100 dark:bg-slate-800/50 text-gray-400 italic"
                                            >
                                                {game.date}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
