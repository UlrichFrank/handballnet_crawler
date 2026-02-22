import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface RefereeStats {
    name: string;
    games: number;
    yellowCards: number;
    twoMinPenalties: number;
    redCards: number;
    blueCards: number;
}

interface Props {
    league: LeagueConfig;
}

export function RefereeStatisticsTable({ league }: Props) {
    const [stats, setStats] = useState<RefereeStats[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadStats = async () => {
            try {
                setLoading(true);
                const data = await dataService.getRefereeStatistics(league.name);
                setStats(data);
            } catch (err) {
                console.error('Failed to load referee statistics:', err);
            } finally {
                setLoading(false);
            }
        };

        if (league) {
            loadStats();
        }
    }, [league]);

    if (loading) {
        return <div className="text-center text-gray-500 dark:text-gray-400 py-12">Laden...</div>;
    }

    if (stats.length === 0) {
        return <div className="text-gray-500 dark:text-gray-400 py-6 text-center">Keine Schiedsrichter-Daten gefunden</div>;
    }

    return (
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto" style={{ maxHeight: '600px', overflowY: 'auto' }}>
                <table className="w-full">
                    <thead className="sticky top-0">
                        <tr className="bg-blue-900 dark:bg-blue-600 text-white">
                            <th className="px-4 py-3 text-left font-bold">Rang</th>
                            <th className="px-4 py-3 text-left font-bold">Name</th>
                            <th className="px-4 py-3 text-center font-bold w-24">Spiele</th>
                            <th className="px-4 py-3 text-center font-bold text-blue-300">🔵 Blau</th>
                            <th className="px-4 py-3 text-center font-bold text-red-300">🔴 Rot</th>
                            <th className="px-4 py-3 text-center font-bold">⏱️ 2-Min</th>
                            <th className="px-4 py-3 text-center font-bold text-yellow-300">🟡 Gelb</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stats.map((stat, idx) => (
                            <tr
                                key={stat.name}
                                className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-gray-50 dark:bg-slate-800'}
                            >
                                <td className="px-4 py-3 font-bold text-blue-900 dark:text-blue-400">
                                    {idx + 1}
                                </td>
                                <td className="px-4 py-3 font-semibold text-gray-900 dark:text-gray-100">
                                    {stat.name}
                                </td>
                                <td className="px-4 py-3 text-center font-bold text-gray-900 dark:text-gray-100">
                                    {stat.games}
                                </td>
                                <td className="px-4 py-3 text-center font-semibold text-blue-600 dark:text-blue-400">
                                    {stat.blueCards}
                                </td>
                                <td className="px-4 py-3 text-center font-semibold text-red-600 dark:text-red-400">
                                    {stat.redCards}
                                </td>
                                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">
                                    {stat.twoMinPenalties}
                                </td>
                                <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100">
                                    {stat.yellowCards}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="px-4 py-3 bg-gray-50 dark:bg-slate-800 text-sm text-gray-600 dark:text-gray-400">
                Summierte Strafen aus allen durch den Schiedsrichter geleiteten Spielen.
            </div>
        </div>
    );
}
