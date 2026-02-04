import { LeagueConfig, GameData, AppConfig } from '../types/handball';

// Bestimme den Basis-Pfad abhängig von der Umgebung
const getBasePath = (): string => {
  // Auf GitHub Pages ist der Basis-Pfad /handballnet_crawler/, lokal ist es /
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return '';
  }
  return '/handballnet_crawler';
};

const getConfigPath = (): string => `${getBasePath()}/config.json`;
const getMetaPath = (): string => `${getBasePath()}/data/meta.json`;

interface MetaIndex {
  last_updated: string;
  leagues: {
    [key: string]: {
      name: string;
      spieltage: string[];
      last_updated: string;
    };
  };
}

class DataService {
  private configCache: AppConfig | null = null;
  private metaCache: MetaIndex | null = null;
  private gameDataCache: Map<string, GameData> = new Map();

  async loadConfig(): Promise<AppConfig> {
    if (this.configCache) {
      return this.configCache;
    }

    const response = await fetch(getConfigPath());
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.statusText}`);
    }
    const config = await response.json();
    this.configCache = config;
    return config;
  }

  async loadMeta(): Promise<MetaIndex> {
    if (this.metaCache) {
      return this.metaCache;
    }

    const response = await fetch(`${getMetaPath()}?t=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`Failed to load meta index: ${response.statusText}`);
    }
    const meta = await response.json();
    this.metaCache = meta;
    return meta;
  }

  async getLeagues(): Promise<LeagueConfig[]> {
    const config = await this.loadConfig();
    return config.leagues;
  }

  async getGameData(leagueId: string, spieltag: string | null = null): Promise<GameData> {
    // Use league name directly
    const meta = await this.loadMeta();
    if (!meta.leagues[leagueId]) {
      throw new Error(`League ${leagueId} not found in meta.json`);
    }

    // Wenn kein Spieltag angegeben, lade den letzten
    let spieltagFile = spieltag;
    if (!spieltagFile) {
      const liga = meta.leagues[leagueId];
      if (liga && liga.spieltage && liga.spieltage.length > 0) {
        // Lade letzten Spieltag (yyyymmdd)
        spieltagFile = liga.spieltage[liga.spieltage.length - 1];
      } else {
        throw new Error(`No Spieltag data available for ${leagueId}`);
      }
    }

    const cacheKey = `${leagueId}_${spieltagFile}`;
    if (this.gameDataCache.has(cacheKey)) {
      return this.gameDataCache.get(cacheKey)!;
    }

    // Lade Spieltag JSON (format: yyyymmdd.json)
    const response = await fetch(`${getBasePath()}/data/${leagueId}/${spieltagFile}.json?t=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`Failed to load game data for ${leagueId}, Spieltag ${spieltagFile}: ${response.statusText}`);
    }
    const data = await response.json();
    this.gameDataCache.set(cacheKey, data);
    return data;
  }

  /**
   * Get aggregated game data for entire league (all Spieltage combined)
   */
  async getAggregatedGameData(leagueId: string): Promise<GameData> {
    // Try to resolve via meta.json leagues keys
    const meta = await this.loadMeta();
    if (!meta.leagues[leagueId]) {
      throw new Error(`League not found: ${leagueId}`);
    }

    const cacheKey = `${leagueId}_aggregated`;
    if (this.gameDataCache.has(cacheKey)) {
      return this.gameDataCache.get(cacheKey)!;
    }

    const liga = meta.leagues[leagueId];
    if (!liga || !liga.spieltage || liga.spieltage.length === 0) {
      throw new Error(`No Spieltag data available for ${leagueId}`);
    }

    // Load all Spieltag files
    const allGames: any[] = [];
    for (const spieltag of liga.spieltage) {
      try {
        const response = await fetch(`${getBasePath()}/data/${leagueId}/${spieltag}.json?t=${Date.now()}`);
        if (response.ok) {
          const data = await response.json();
          if (data.games && Array.isArray(data.games)) {
            allGames.push(...data.games);
          }
        }
      } catch (err) {
        console.warn(`Failed to load Spieltag ${spieltag}:`, err);
      }
    }

    const aggregatedData: GameData = {
      games: allGames,
    };

    this.gameDataCache.set(cacheKey, aggregatedData);
    return aggregatedData;
  }

  /**
   * Get all unique teams for a league sorted alphabetically (aggregated from all Spieltage)
   */
  async getTeamsForLeague(outName: string): Promise<string[]> {
    const gameData = await this.getAggregatedGameData(outName);
    const teams = new Set<string>();

    gameData.games.forEach((game) => {
      if (game.home.team_name) teams.add(game.home.team_name);
      if (game.away.team_name) teams.add(game.away.team_name);
    });

    return Array.from(teams).sort();
  }

  /**
   * Get all games for a team in a league (home + away)
   */
  getTeamGames(gameData: GameData, teamName: string) {
    const teamGames: Map<string, any> = new Map();

    gameData.games.forEach((game) => {
      const { game_id, order, date, graphic_path } = game;

      // Calculate score
      const homeGoals = game.home.players.reduce((sum, p) => sum + p.goals, 0);
      const awayGoals = game.away.players.reduce((sum, p) => sum + p.goals, 0);
      const score = `${homeGoals}:${awayGoals}`;

      // Home game
      if (game.home.team_name === teamName) {
        teamGames.set(`home_${game_id}`, {
          game_id,
          order,
          date,
          score,
          opponent: game.away.team_name,
          is_home: true,
          players: game.home.players,
          graphic_path,
        });
      }

      // Away game
      if (game.away.team_name === teamName) {
        teamGames.set(`away_${game_id}`, {
          game_id,
          order,
          date,
          score,
          opponent: game.home.team_name,
          is_home: false,
          players: game.away.players,
          graphic_path,
        });
      }
    });

    // Sort by order
    return Array.from(teamGames.values()).sort((a, b) => a.order - b.order);
  }

  /**
   * Get all players for a team across all games
   */
  getTeamPlayers(teamGames: any[]): string[] {
    const players = new Set<string>();
    teamGames.forEach((game) => {
      game.players.forEach((player: any) => {
        players.add(player.name);
      });
    });
    return Array.from(players).sort();
  }

  /**
   * Get player stats for a specific game
   */
  getPlayerGameStats(game: any, playerName: string) {
    const player = game.players.find((p: any) => p.name === playerName);
    if (!player) {
      return null;
    }
    return {
      goals: player.goals,
      seven_meters: player.seven_meters,
      seven_meters_goals: player.seven_meters_goals,
      two_min_penalties: player.two_min_penalties,
      yellow_cards: player.yellow_cards,
      red_cards: player.red_cards,
      blue_cards: player.blue_cards,
    };
  }

  /**
   * Get aggregated stats for a player across all games
   */
  getPlayerTotalStats(teamGames: any[], playerName: string) {
    const stats = {
      goals: 0,
      seven_meters: 0,
      seven_meters_goals: 0,
      two_min_penalties: 0,
      yellow_cards: 0,
      red_cards: 0,
      blue_cards: 0,
      games: 0,
    };

    teamGames.forEach((game) => {
      const gameStats = this.getPlayerGameStats(game, playerName);
      if (gameStats) {
        stats.goals += gameStats.goals;
        stats.seven_meters += gameStats.seven_meters;
        stats.seven_meters_goals += gameStats.seven_meters_goals;
        stats.two_min_penalties += gameStats.two_min_penalties;
        stats.yellow_cards += gameStats.yellow_cards;
        stats.red_cards += gameStats.red_cards;
        stats.blue_cards += gameStats.blue_cards;
        stats.games += 1;
      }
    });

    return stats;
  }

  /**
   * Get game totals across all players
   */
  getGameTotals(game: any) {
    const totals = {
      goals: 0,
      seven_meters: 0,
      seven_meters_goals: 0,
      two_min_penalties: 0,
      yellow_cards: 0,
      red_cards: 0,
      blue_cards: 0,
    };

    game.players.forEach((player: any) => {
      totals.goals += player.goals;
      totals.seven_meters += player.seven_meters;
      totals.seven_meters_goals += player.seven_meters_goals;
      totals.two_min_penalties += player.two_min_penalties;
      totals.yellow_cards += player.yellow_cards;
      totals.red_cards += player.red_cards;
      totals.blue_cards += player.blue_cards;
    });

    return totals;
  }

  /**
   * Get all officials (referees, timekeepers, secretaries) for a league with their games
   */
  async getAllOfficials(outName: string): Promise<{
    referees: Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>;
    timekeepers: Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>;
    secretaries: Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>;
  }> {
    const gameData = await this.getAggregatedGameData(outName);
    
    const referees = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();
    const timekeepers = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();
    const secretaries = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();

    gameData.games.forEach((game: any) => {
      const gameInfo = {
        date: game.date,
        home: game.home.team_name,
        away: game.away.team_name,
        score: game.final_score || '?:?',
      };

      if (game.officials) {
        // Count referees with games
        game.officials.referees?.forEach((name: string) => {
          if (!referees.has(name)) {
            referees.set(name, { count: 0, games: [] });
          }
          const data = referees.get(name)!;
          data.count++;
          data.games.push(gameInfo);
        });

        // Count timekeepers with games
        game.officials.timekeepers?.forEach((name: string) => {
          if (!timekeepers.has(name)) {
            timekeepers.set(name, { count: 0, games: [] });
          }
          const data = timekeepers.get(name)!;
          data.count++;
          data.games.push(gameInfo);
        });

        // Count secretaries with games
        game.officials.secretaries?.forEach((name: string) => {
          if (!secretaries.has(name)) {
            secretaries.set(name, { count: 0, games: [] });
          }
          const data = secretaries.get(name)!;
          data.count++;
          data.games.push(gameInfo);
        });
      }
    });

    return { referees, timekeepers, secretaries };
  }

  /**
   * Get player statistics (top scorers) for a league
   */
  async getPlayerStatistics(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const playerStats = new Map<string, {
      goals: number;
      sevenMetersGoals: number;
      sevenMetersAttempts: number;
      team: string;
      games: number;
    }>();

    gameData.games.forEach(game => {
      // Home team players
      game.home.players.forEach(player => {
        const key = `${player.name}|${game.home.team_name}`;
        if (!playerStats.has(key)) {
          playerStats.set(key, {
            goals: 0,
            sevenMetersGoals: 0,
            sevenMetersAttempts: 0,
            team: game.home.team_name,
            games: 0,
          });
        }
        const stats = playerStats.get(key)!;
        stats.goals += player.goals;
        stats.sevenMetersGoals += player.seven_meters_goals;
        stats.sevenMetersAttempts += player.seven_meters;
        stats.games += 1;
      });

      // Away team players
      game.away.players.forEach(player => {
        const key = `${player.name}|${game.away.team_name}`;
        if (!playerStats.has(key)) {
          playerStats.set(key, {
            goals: 0,
            sevenMetersGoals: 0,
            sevenMetersAttempts: 0,
            team: game.away.team_name,
            games: 0,
          });
        }
        const stats = playerStats.get(key)!;
        stats.goals += player.goals;
        stats.sevenMetersGoals += player.seven_meters_goals;
        stats.sevenMetersAttempts += player.seven_meters;
        stats.games += 1;
      });
    });

    // Convert to sorted array
    return Array.from(playerStats.entries())
      .map(([key, stats]) => {
        const name = key.split('|')[0];
        return {
          name,
          team: stats.team,
          goals: stats.goals,
          sevenMetersGoals: stats.sevenMetersGoals,
          sevenMetersAttempts: stats.sevenMetersAttempts,
          sevenMeterPercent: stats.sevenMetersAttempts > 0
            ? Math.round((stats.sevenMetersGoals / stats.sevenMetersAttempts) * 100)
            : 0,
          games: stats.games,
        };
      })
      .sort((a, b) => b.goals - a.goals);
  }

  /**
   * Get 7-meter shooters (players with at least 1 attempt)
   */
  async getSevenMeterShooters(outName: string) {
    const playerStats = await this.getPlayerStatistics(outName);
    
    return playerStats
      .filter(p => p.sevenMetersAttempts > 0)
      .map(p => ({
        ...p,
        sevenMeterMissed: p.sevenMetersAttempts - p.sevenMetersGoals,
      }))
      .sort((a, b) => b.sevenMetersGoals - a.sevenMetersGoals);
  }

  /**
   * Get team ratio statistics (goal difference)
   */
  async getTeamRatioStats(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const teamStats = new Map<string, {
      goalsFor: number;
      goalsAgainst: number;
      games: number;
    }>();

    gameData.games.forEach(game => {
      // Sum player goals for home team
      const homeGoals = game.home.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);
      // Sum player goals for away team
      const awayGoals = game.away.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);

      if (!teamStats.has(game.home.team_name)) {
        teamStats.set(game.home.team_name, { goalsFor: 0, goalsAgainst: 0, games: 0 });
      }
      if (!teamStats.has(game.away.team_name)) {
        teamStats.set(game.away.team_name, { goalsFor: 0, goalsAgainst: 0, games: 0 });
      }

      const homeStats = teamStats.get(game.home.team_name)!;
      homeStats.goalsFor += homeGoals;
      homeStats.goalsAgainst += awayGoals;
      homeStats.games += 1;

      const awayStats = teamStats.get(game.away.team_name)!;
      awayStats.goalsFor += awayGoals;
      awayStats.goalsAgainst += homeGoals;
      awayStats.games += 1;
    });

    return Array.from(teamStats.entries())
      .map(([teamName, stats]) => ({
        teamName,
        goalsFor: stats.goalsFor,
        goalsAgainst: stats.goalsAgainst,
        difference: stats.goalsFor - stats.goalsAgainst,
        games: stats.games,
      }))
      .sort((a, b) => b.difference - a.difference);
  }

  /**
   * Get team offense statistics (goals thrown)
   */
  async getTeamOffenseStats(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const teamStats = new Map<string, {
      goals: number;
      games: number;
    }>();

    gameData.games.forEach(game => {
      // Sum player goals for home team
      const homeGoals = game.home.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);
      // Sum player goals for away team
      const awayGoals = game.away.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);

      if (!teamStats.has(game.home.team_name)) {
        teamStats.set(game.home.team_name, { goals: 0, games: 0 });
      }
      if (!teamStats.has(game.away.team_name)) {
        teamStats.set(game.away.team_name, { goals: 0, games: 0 });
      }

      const homeStats = teamStats.get(game.home.team_name)!;
      homeStats.goals += homeGoals;
      homeStats.games += 1;

      const awayStats = teamStats.get(game.away.team_name)!;
      awayStats.goals += awayGoals;
      awayStats.games += 1;
    });

    return Array.from(teamStats.entries())
      .map(([teamName, stats]) => ({
        teamName,
        totalGoals: stats.goals,
        games: stats.games,
        avgGoalsPerGame: parseFloat((stats.goals / stats.games).toFixed(1)),
      }))
      .sort((a, b) => b.totalGoals - a.totalGoals);
  }

  /**
   * Get team defense statistics (goals conceded)
   */
  async getTeamDefenseStats(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const teamStats = new Map<string, {
      conceded: number;
      games: number;
    }>();

    gameData.games.forEach(game => {
      // Sum opponent player goals for home team (from away team)
      const awayGoals = game.away.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);
      // Sum opponent player goals for away team (from home team)
      const homeGoals = game.home.players.reduce((sum: number, player: any) => sum + (player.goals || 0), 0);

      if (!teamStats.has(game.home.team_name)) {
        teamStats.set(game.home.team_name, { conceded: 0, games: 0 });
      }
      if (!teamStats.has(game.away.team_name)) {
        teamStats.set(game.away.team_name, { conceded: 0, games: 0 });
      }

      const homeStats = teamStats.get(game.home.team_name)!;
      homeStats.conceded += awayGoals;
      homeStats.games += 1;

      const awayStats = teamStats.get(game.away.team_name)!;
      awayStats.conceded += homeGoals;
      awayStats.games += 1;
    });

    return Array.from(teamStats.entries())
      .map(([teamName, stats]) => ({
        teamName,
        totalConceded: stats.conceded,
        games: stats.games,
        avgConcededPerGame: parseFloat((stats.conceded / stats.games).toFixed(1)),
      }))
      .sort((a, b) => a.totalConceded - b.totalConceded);
  }

  /**
   * Get team discipline statistics (Fair-Play ranking)
   */
  async getTeamDisciplineStats(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const teamStats = new Map<string, {
      blueCards: number;
      redCards: number;
      twoMinPenalties: number;
      yellowCards: number;
    }>();

    gameData.games.forEach(game => {
      // Home team
      if (!teamStats.has(game.home.team_name)) {
        teamStats.set(game.home.team_name, {
          blueCards: 0,
          redCards: 0,
          twoMinPenalties: 0,
          yellowCards: 0,
        });
      }
      const homeStats = teamStats.get(game.home.team_name)!;
      game.home.players.forEach(player => {
        homeStats.blueCards += player.blue_cards || 0;
        homeStats.redCards += player.red_cards || 0;
        homeStats.twoMinPenalties += player.two_min_penalties || 0;
        homeStats.yellowCards += player.yellow_cards || 0;
      });

      // Away team
      if (!teamStats.has(game.away.team_name)) {
        teamStats.set(game.away.team_name, {
          blueCards: 0,
          redCards: 0,
          twoMinPenalties: 0,
          yellowCards: 0,
        });
      }
      const awayStats = teamStats.get(game.away.team_name)!;
      game.away.players.forEach(player => {
        awayStats.blueCards += player.blue_cards || 0;
        awayStats.redCards += player.red_cards || 0;
        awayStats.twoMinPenalties += player.two_min_penalties || 0;
        awayStats.yellowCards += player.yellow_cards || 0;
      });
    });

    return Array.from(teamStats.entries())
      .map(([teamName, stats]) => ({
        teamName,
        blueCards: stats.blueCards,
        redCards: stats.redCards,
        twoMinPenalties: stats.twoMinPenalties,
        yellowCards: stats.yellowCards,
        totalDisciplinePoints: (stats.blueCards * 4) + (stats.redCards * 3) + (stats.twoMinPenalties * 2) + (stats.yellowCards * 1),
      }))
      .sort((a, b) => a.totalDisciplinePoints - b.totalDisciplinePoints);
  }

  /**
   * Calculate Gini coefficient for goal distribution
   * Measures inequality in goal distribution across players
   * 0 = perfect equality, 1 = perfect inequality
   */
  private calculateGiniCoefficient(values: number[]): number {
    if (values.length === 0) return 0;
    
    const sorted = [...values].sort((a, b) => a - b);
    const n = sorted.length;
    const mean = sorted.reduce((a, b) => a + b, 0) / n;
    
    if (mean === 0) return 0;
    
    const sumAbsDiff = sorted.reduce((sum, val, i) => {
      return sum + ((i + 1) * val);
    }, 0);
    
    return (2 * sumAbsDiff) / (n * n * mean) - (n + 1) / n;
  }

  /**
   * Get goal distribution statistics (avg, median, Gini coefficient)
   */
  async getGoalDistributionStats(outName: string) {
    const gameData = await this.getAggregatedGameData(outName);
    const teamStats = new Map<string, number[]>();

    gameData.games.forEach(game => {
      // Home team
      if (!teamStats.has(game.home.team_name)) {
        teamStats.set(game.home.team_name, []);
      }
      game.home.players.forEach(player => {
        const goals = player.goals || 0;
        teamStats.get(game.home.team_name)!.push(goals);
      });

      // Away team
      if (!teamStats.has(game.away.team_name)) {
        teamStats.set(game.away.team_name, []);
      }
      game.away.players.forEach(player => {
        const goals = player.goals || 0;
        teamStats.get(game.away.team_name)!.push(goals);
      });
    });

    return Array.from(teamStats.entries())
      .map(([teamName, playerGoals]) => {
        const sorted = [...playerGoals].sort((a, b) => a - b);
        const avg = playerGoals.reduce((a, b) => a + b, 0) / playerGoals.length;
        
        let median: number;
        if (sorted.length % 2 === 0) {
          median = (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2;
        } else {
          median = sorted[Math.floor(sorted.length / 2)];
        }

        return {
          teamName,
          avgGoalsPerPlayer: avg,
          medianGoalsPerPlayer: median,
          giniCoefficient: this.calculateGiniCoefficient(playerGoals),
        };
      })
      .sort((a, b) => b.avgGoalsPerPlayer - a.avgGoalsPerPlayer);
  }
}

export const dataService = new DataService();
