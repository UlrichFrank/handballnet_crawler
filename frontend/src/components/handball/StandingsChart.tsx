import { useState, useEffect } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface StandingsChartProps {
    league: LeagueConfig;
}

/** Generate N visually distinct colors using evenly spaced HSL hues — no duplicates. */
function generateUniqueColors(n: number): string[] {
    return Array.from({ length: n }, (_, i) => {
        const hue = Math.round((i * 360) / n);
        // Alternate lightness slightly to improve distinguishability for adjacent hues
        const lightness = i % 2 === 0 ? 42 : 52;
        return `hsl(${hue}, 72%, ${lightness}%)`;
    });
}

type ProgressionEntry = { spieltag: number; date: string;[team: string]: number | string };

export function StandingsChart({ league }: StandingsChartProps) {
    const [progression, setProgression] = useState<ProgressionEntry[]>([]);
    const [teams, setTeams] = useState<string[]>([]);
    const [teamColors, setTeamColors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [hoveredTeam, setHoveredTeam] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await dataService.getStandingsProgression(league.name);
                setProgression(data);

                const teamSet = new Set<string>();
                data.forEach(entry => {
                    Object.keys(entry).forEach(k => {
                        if (k !== 'spieltag' && k !== 'date') teamSet.add(k);
                    });
                });
                const sorted = Array.from(teamSet).sort();
                setTeams(sorted);

                // Assign unique, non-repeating colors
                const colors = generateUniqueColors(sorted.length);
                const colorMap: Record<string, string> = {};
                sorted.forEach((team, i) => { colorMap[team] = colors[i]; });
                setTeamColors(colorMap);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Fehler beim Laden');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [league]);

    if (loading) return <div className="text-center text-gray-500 dark:text-gray-400 py-12">Lade Tabellenverlauf...</div>;
    if (error) return <div className="text-center text-red-500 py-6">{error}</div>;
    if (progression.length === 0 || teams.length === 0) return (
        <div className="text-center text-gray-500 dark:text-gray-400 py-6">Keine Verlaufsdaten verfügbar.</div>
    );

    const nTeams = teams.length;

    // Build a lookup: spieltag index → date string
    const dateByIndex: Record<number, string> = {};
    progression.forEach(e => { dateByIndex[e.spieltag] = e.date as string; });

    // Custom X-axis tick: shows spieltag number + date below
    const CustomXTick = ({ x, y, payload }: any) => {
        const date = dateByIndex[payload.value] ?? '';
        return (
            <g transform={`translate(${x},${y})`}>
                <text x={0} y={0} dy={12} textAnchor="middle" fontSize={10} fill="currentColor" className="text-gray-600 dark:text-gray-400">
                    {payload.value}
                </text>
                {date && (
                    <text x={0} y={0} dy={24} textAnchor="middle" fontSize={9} fill="currentColor" className="text-gray-400 dark:text-gray-500">
                        {date}
                    </text>
                )}
            </g>
        );
    };

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (!active || !payload || payload.length === 0) return null;
        const date = dateByIndex[label] ?? '';
        const sorted = [...payload].filter(p => typeof p.value === 'number').sort((a, b) => a.value - b.value);
        return (
            <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg shadow-lg p-3 text-xs max-w-[240px]">
                <p className="font-bold text-gray-900 dark:text-gray-100 mb-1">
                    Spieltag {label}{date ? ` · ${date}` : ''}
                </p>
                <div className="border-t border-gray-200 dark:border-slate-700 pt-1 mt-1">
                    {sorted.map((entry: any) => (
                        <div key={entry.dataKey} className={`flex items-center gap-2 py-0.5 ${hoveredTeam === entry.dataKey ? 'font-bold' : ''}`}>
                            <span className="inline-block w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: entry.stroke }} />
                            <span className="text-gray-700 dark:text-gray-300 truncate flex-1">{entry.dataKey}</span>
                            <span className="font-bold text-gray-900 dark:text-gray-100 ml-auto">{entry.value}.</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    const renderLegend = ({ payload }: any) => (
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 mt-2 px-4">
            {payload?.map((entry: any) => {
                const isHovered = hoveredTeam === entry.dataKey;
                const isDimmed = hoveredTeam !== null && !isHovered;
                return (
                    <span
                        key={entry.dataKey}
                        className="flex items-center gap-1 cursor-pointer select-none text-xs transition-opacity"
                        style={{ opacity: isDimmed ? 0.3 : 1, fontWeight: isHovered ? 700 : 400 }}
                        onMouseEnter={() => setHoveredTeam(entry.dataKey)}
                        onMouseLeave={() => setHoveredTeam(null)}
                    >
                        <span className="inline-block rounded-sm flex-shrink-0" style={{ width: 16, height: 3, backgroundColor: entry.color }} />
                        <span className="text-gray-700 dark:text-gray-300">{entry.dataKey}</span>
                    </span>
                );
            })}
        </div>
    );

    return (
        <div>
            <div>
                <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Tabellenverlauf</h1>
                <p className="text-gray-600 dark:text-gray-400">Platzierung jeder Mannschaft nach jedem Spieltag</p>
            </div>

            <div className="p-4" onMouseLeave={() => setHoveredTeam(null)}>
                <ResponsiveContainer width="100%" height={460}>
                    <LineChart data={progression} margin={{ top: 8, right: 24, left: 0, bottom: 32 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(156,163,175,0.3)" />
                        <XAxis
                            dataKey="spieltag"
                            height={48}
                            tick={<CustomXTick />}
                            tickLine={false}
                            label={{ value: 'Spieltag', position: 'insideBottom', offset: -4, fontSize: 12 }}
                        />
                        <YAxis
                            reversed
                            domain={[1, nTeams]}
                            ticks={Array.from({ length: nTeams }, (_, i) => i + 1)}
                            label={{ value: 'Platz', angle: -90, position: 'insideLeft', offset: 10, fontSize: 12 }}
                            tick={{ fontSize: 11 }}
                            tickLine={false}
                            width={32}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend content={renderLegend} />
                        {teams.map((team) => {
                            const color = teamColors[team] ?? '#888';
                            const isHovered = hoveredTeam === team;
                            const isDimmed = hoveredTeam !== null && !isHovered;
                            return (
                                <Line
                                    key={team}
                                    type="linear"
                                    dataKey={team}
                                    stroke={color}
                                    strokeWidth={isHovered ? 3.5 : 2}
                                    strokeOpacity={isDimmed ? 0.12 : 1}
                                    dot={false}
                                    activeDot={{ r: isHovered ? 6 : 4, strokeWidth: 0 }}
                                    connectNulls
                                    onMouseEnter={() => setHoveredTeam(team)}
                                    onMouseLeave={() => setHoveredTeam(null)}
                                />
                            );
                        })}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
