import { useState, useEffect } from 'react';
import { useLeague } from '../contexts/LeagueContext';
import { dataService } from '../services/dataService';
import { PlayerStatisticsTable } from '../components/statistics/PlayerStatisticsTable';
import { SevenMeterShooterTable } from '../components/statistics/SevenMeterShooterTable';
import { TeamRatioTable } from '../components/statistics/TeamRatioTable';
import { TeamOffenseTable } from '../components/statistics/TeamOffenseTable';
import { TeamDefenseTable } from '../components/statistics/TeamDefenseTable';
import { TeamDisciplineTable } from '../components/statistics/TeamDisciplineTable';
import { GoalDistributionTable } from '../components/statistics/GoalDistributionTable';

type StatisticTab = 'scorers' | 'seven-meter' | 'ratio' | 'offense' | 'defense' | 'discipline' | 'goal-distribution';

export function StatisticsPage() {
  const { selectedLeague } = useLeague();
  const [activeTab, setActiveTab] = useState<StatisticTab>('scorers');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Pre-load data for the active tab
    const loadData = async () => {
      if (!selectedLeague) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        // Just validate that we can load the base data
        await dataService.getAggregatedGameData(selectedLeague.name);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedLeague]);

  if (!selectedLeague) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">Keine Liga ausgewählt</div>
          <div className="text-gray-500 dark:text-gray-400">Bitte wähle eine Liga aus der Dropdown-Liste oben aus.</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-900 rounded-lg p-4 text-red-700 dark:text-red-200 m-6">
        <strong>Fehler:</strong> {error}
      </div>
    );
  }

  const tabs: Array<{ id: StatisticTab; label: string; icon: string }> = [
    { id: 'scorers', label: 'Torschützen', icon: '🏆' },
    { id: 'seven-meter', label: 'Bester 7m-Schütze', icon: '🎯' },
    { id: 'ratio', label: 'Torverhältnis', icon: '⚖️' },
    { id: 'offense', label: 'Bester Angriff', icon: '⚔️' },
    { id: 'goal-distribution', label: 'Verteilung', icon: '🎲' },
    { id: 'defense', label: 'Beste Verteidigung', icon: '🛡️' },
    { id: 'discipline', label: 'Fair-Play', icon: '📋' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400">📊 Statistiken & Ranglisten</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Übersicht der Saison-Statistiken für {selectedLeague.display_name}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex overflow-x-auto gap-2 py-2">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-900 dark:bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-700'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-500 dark:text-gray-400">Statistiken werden geladen...</div>
          </div>
        )}

        {!loading && (
          <>
            {activeTab === 'scorers' && <PlayerStatisticsTable league={selectedLeague} />}
            {activeTab === 'seven-meter' && <SevenMeterShooterTable league={selectedLeague} />}
            {activeTab === 'ratio' && <TeamRatioTable league={selectedLeague} />}
            {activeTab === 'offense' && <TeamOffenseTable league={selectedLeague} />}
            {activeTab === 'goal-distribution' && <GoalDistributionTable league={selectedLeague} />}
            {activeTab === 'defense' && <TeamDefenseTable league={selectedLeague} />}
            {activeTab === 'discipline' && <TeamDisciplineTable league={selectedLeague} />}
          </>
        )}
      </div>
    </div>
  );
}
