// Handball League & Game Data Types

export interface PlayerStats {
  name: string;
  goals: number;
  two_min_penalties: number;
  yellow_cards: number;
  red_cards: number;
  blue_cards: number;
  seven_meters: number;
  seven_meters_goals: number;
}

export interface TeamData {
  team_name: string;
  players: PlayerStats[];
}

export interface GoalEvent {
  minute: number;
  second: number;
  scorer: string;
  team: 'home' | 'away';
  seven_meter?: boolean;
}

export interface Game {
  game_id: string;
  order: number;
  date: string;
  home: TeamData;
  away: TeamData;
  final_score?: string;
  goals_timeline?: GoalEvent[];
  graphic_path?: string;
}

export interface GameData {
  games: Game[];
}

export interface LeagueConfig {
  name: string;
  display_name: string;
  out_name: string;
  data_folder: string;
  half_duration: number;
  age_group: string;
}

export interface AppConfig {
  ref: {
    base_url: string;
  };
  leagues: LeagueConfig[];
}

export interface TeamGameStats {
  order: number;
  date: string;
  score: string;
  opponent: string;
  is_home: boolean;
  players: PlayerStats[];
  graphic_path?: string;
}

// Statistics helper type
export interface AggregatedPlayerStats {
  goals: number;
  seven_meters: number;
  seven_meters_goals: number;
  two_min_penalties: number;
  yellow_cards: number;
  red_cards: number;
  blue_cards: number;
}

export interface GameTotals {
  goals: number;
  seven_meters: number;
  seven_meters_goals: number;
  two_min_penalties: number;
  yellow_cards: number;
  red_cards: number;
  blue_cards: number;
}
