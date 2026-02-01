import { useState, useEffect } from 'react';
import { dataService } from '../../services/dataService';
import { LeagueConfig } from '../../types/handball';

interface TeamStanding {
  team: string;
  games: number;
  wins: number;
  draws: number;
  losses: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDiff: number;
  points: number;
  pointsFor: number;
  pointsAgainst: number;
}

interface StandingsTableProps {
  league: LeagueConfig;
}

export function StandingsTable({ league }: StandingsTableProps) {
  const [standings, setStandings] = useState<TeamStanding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStandings = async () => {
      try {
        setLoading(true);
        const gameData = await dataService.getGameData(league.out_name);
        const teams = await dataService.getTeamsForLeague(league.out_name);

        const standingsData: TeamStanding[] = teams.map((teamName) => {
          const teamGames = dataService.getTeamGames(gameData, teamName);
          let wins = 0,
            draws = 0,
            losses = 0,
            goalsFor = 0,
            goalsAgainst = 0,
            pointsFor = 0,
            pointsAgainst = 0;

          teamGames.forEach((game) => {
            const [homeGoals, awayGoals] = game.score.split(':').map(Number);
            const isHome = game.is_home;

            if (isHome) {
              goalsFor += homeGoals;
              goalsAgainst += awayGoals;
              if (homeGoals > awayGoals) {
                wins++;
                pointsFor += 2;
                pointsAgainst += 0;
              } else if (homeGoals < awayGoals) {
                losses++;
                pointsFor += 0;
                pointsAgainst += 2;
              } else {
                draws++;
                pointsFor += 1;
                pointsAgainst += 1;
              }
            } else {
              goalsFor += awayGoals;
              goalsAgainst += homeGoals;
              if (awayGoals > homeGoals) {
                wins++;
                pointsFor += 2;
                pointsAgainst += 0;
              } else if (awayGoals < homeGoals) {
                losses++;
                pointsFor += 0;
                pointsAgainst += 2;
              } else {
                draws++;
                pointsFor += 1;
                pointsAgainst += 1;
              }
            }
          });

          const points = wins * 2 + draws;
          const goalDiff = goalsFor - goalsAgainst;

          return {
            team: teamName,
            games: teamGames.length,
            wins,
            draws,
            losses,
            goalsFor,
            goalsAgainst,
            goalDiff,
            points,
            pointsFor,
            pointsAgainst,
          };
        });

        // Sort by points (desc), then goal difference (desc), then goals for (desc)
        standingsData.sort((a, b) => {
          if (b.points !== a.points) return b.points - a.points;
          if (b.goalDiff !== a.goalDiff) return b.goalDiff - a.goalDiff;
          return b.goalsFor - a.goalsFor;
        });

        setStandings(standingsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load standings');
      } finally {
        setLoading(false);
      }
    };

    loadStandings();
  }, [league]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500 dark:text-gray-400">Loading standings...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-400">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-blue-900 dark:bg-blue-600 text-white border-b border-blue-200 dark:border-blue-700">
            <th className="px-4 py-3 text-left text-sm font-bold">Platz</th>
            <th className="px-4 py-3 text-left text-sm font-bold">Team</th>
            <th className="px-4 py-3 text-center text-sm font-bold">Sp.</th>
            <th className="px-4 py-3 text-center text-sm font-bold">S</th>
            <th className="px-4 py-3 text-center text-sm font-bold">U</th>
            <th className="px-4 py-3 text-center text-sm font-bold">N</th>
            <th className="px-4 py-3 text-center text-sm font-bold">T</th>
            <th className="px-4 py-3 text-center text-sm font-bold">+/-</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((standing, idx) => (
            <tr
              key={standing.team}
              className={idx % 2 === 0 ? 'bg-white dark:bg-slate-900 hover:bg-blue-50 dark:hover:bg-slate-800' : 'bg-gray-50 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-slate-700'}
            >
              <td className="px-4 py-3 text-center font-bold text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {idx + 1}
              </td>
              <td className="px-4 py-3 text-left text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.team}
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.games}
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.wins}
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.draws}
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.losses}
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                {standing.goalsFor}:{standing.goalsAgainst} <span className={standing.goalDiff > 0 ? 'text-green-600 dark:text-green-400 font-semibold' : standing.goalDiff < 0 ? 'text-red-600 dark:text-red-400 font-semibold' : 'text-gray-500'}>({standing.goalDiff > 0 ? '+' : ''}{standing.goalDiff})</span>
              </td>
              <td className="px-4 py-3 text-center text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-slate-700">
                <span>{standing.pointsFor}</span>
                <span className="text-gray-400 dark:text-gray-500 mx-1">/</span>
                <span>{standing.pointsAgainst}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
