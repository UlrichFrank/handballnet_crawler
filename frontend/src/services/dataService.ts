import { LeagueConfig, GameData, AppConfig } from '../types/handball';

const CONFIG_PATH = '/hb_grabber/config.json';
const META_PATH = '/hb_grabber/data/meta.json';

interface MetaIndex {
  last_updated: string;
  leagues: {
    [key: string]: {
      name: string;
      spieltage: number[];
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

    const response = await fetch(CONFIG_PATH);
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

    const response = await fetch(`${META_PATH}?t=${Date.now()}`);
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

  async getGameData(outName: string, spieltag: number = 1): Promise<GameData> {
    const cacheKey = `${outName}_${spieltag}`;
    if (this.gameDataCache.has(cacheKey)) {
      return this.gameDataCache.get(cacheKey)!;
    }

    // Mappe outName zu Liga-ID (c_jugend, d_jugend)
    let ligaId = outName;
    if (outName.includes('MC-OL') || outName.includes('mc-ol')) {
      ligaId = 'c_jugend';
    } else if (outName.includes('Landesliga') || outName.includes('landesliga')) {
      ligaId = 'd_jugend';
    }

    // Lade Spieltag JSON
    const response = await fetch(`/hb_grabber/data/${ligaId}/spieltag_${spieltag}.json?t=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`Failed to load game data for ${outName}, Spieltag ${spieltag}: ${response.statusText}`);
    }
    const data = await response.json();
    this.gameDataCache.set(cacheKey, data);
    return data;
  }

  /**
   * Get all unique teams for a league sorted alphabetically
   */
  async getTeamsForLeague(outName: string): Promise<string[]> {
    const gameData = await this.getGameData(outName);
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
    const gameData = await this.getGameData(outName);
    console.log('[dataService] getAllOfficials - games count:', gameData.games.length);
    
    const referees = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();
    const timekeepers = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();
    const secretaries = new Map<string, { count: number; games: Array<{ date: string; home: string; away: string; score: string }> }>();

    gameData.games.forEach((game: any, idx: number) => {
      const gameInfo = {
        date: game.date,
        home: game.home.team_name,
        away: game.away.team_name,
        score: game.final_score || '?:?',
      };

      // Debug: log first 3 games to see if officials exist
      if (idx < 3) {
        console.log(`[dataService] Game ${idx}:`, {
          game_id: game.game_id,
          has_officials: !!game.officials,
          officials: game.officials,
        });
      }

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

    console.log('[dataService] Final officials - referees:', referees.size, 'timekeepers:', timekeepers.size, 'secretaries:', secretaries.size);
    return { referees, timekeepers, secretaries };
  }
}

export const dataService = new DataService();
