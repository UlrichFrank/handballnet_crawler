import { useEffect, useState } from 'react';
import { Card } from '../components/ui/card';
import { dataService } from '../services/dataService';

interface MetaData {
  last_updated: string;
  leagues: {
    [key: string]: {
      name: string;
      spieltage: string[];
      last_updated: string;
    };
  };
}

export function StatusPage() {
  const [meta, setMeta] = useState<MetaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMetaData = async () => {
      try {
        setLoading(true);
        const data = await dataService.loadMeta();
        setMeta(data);
        setError(null);
      } catch (err) {
        console.error('Error loading meta.json:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setMeta(null);
      } finally {
        setLoading(false);
      }
    };

    loadMetaData();
  }, []);

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const formatGameDate = (dateStr: string) => {
    if (dateStr.length !== 8) return dateStr;
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    return `${day}.${month}.${year}`;
  };

  const getTotalStats = () => {
    if (!meta) return { spieltage: 0, games: 0 };
    
    let totalSpiele = 0;
    Object.values(meta.leagues).forEach((league) => {
      totalSpiele += league.spieltage.length;
    });

    return {
      spieltage: totalSpiele,
      games: 0, // We don't have total games count in meta.json
    };
  };

  const stats = getTotalStats();

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">Lädt Daten...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card className="p-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
          <h3 className="text-red-900 dark:text-red-100 font-semibold mb-2">
            ❌ Fehler beim Laden der Daten
          </h3>
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </Card>
      </div>
    );
  }

  if (!meta) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card className="p-6">
          <p className="text-gray-500 dark:text-gray-400">
            Keine Daten verfügbar. Bitte führen Sie zuerst den Scraper aus.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Overall Status */}
      <Card className="p-6 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
        <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-100 mb-4">
          📊 Handball-Daten Status
        </h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-blue-700 dark:text-blue-300">Ligen</p>
            <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
              {Object.keys(meta.leagues).length}
            </p>
          </div>
          <div>
            <p className="text-sm text-blue-700 dark:text-blue-300">Spieltage</p>
            <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
              {stats.spieltage}
            </p>
          </div>
          <div>
            <p className="text-sm text-blue-700 dark:text-blue-300">Zuletzt aktualisiert</p>
            <p className="text-sm font-mono text-blue-900 dark:text-blue-100">
              {formatDate(meta.last_updated)}
            </p>
          </div>
        </div>
      </Card>

      {/* Leagues Detail */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">Ligen Details</h3>
        
        {Object.entries(meta.leagues).map(([ligaId, league]) => (
          <Card
            key={ligaId}
            className="p-6 border-l-4 border-l-blue-500 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  🏐 {league.name}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                  {ligaId}
                </p>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {league.spieltage.length}
                </p>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Spieltage
                </p>
              </div>
            </div>

            <div className="mb-4 text-xs text-gray-600 dark:text-gray-400">
              <p>
                Zuletzt aktualisiert: <span className="font-mono">{formatDate(league.last_updated)}</span>
              </p>
            </div>

            {/* Spieltage List */}
            <div className="mt-4">
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                📅 Verfügbare Spieltage:
              </p>
              <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-2">
                {league.spieltage.map((spieltag) => (
                  <div
                    key={spieltag}
                    className="flex items-center justify-center px-3 py-2 bg-gray-100 dark:bg-slate-800 rounded-lg text-xs font-mono text-gray-700 dark:text-gray-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors cursor-help"
                    title={`${formatGameDate(spieltag)}`}
                  >
                    {spieltag}
                  </div>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="mt-4 text-xs text-gray-600 dark:text-gray-400">
              {league.spieltage.length > 0 && (
                <p>
                  📆 Zeitraum: {formatGameDate(league.spieltage[0])} bis{' '}
                  {formatGameDate(league.spieltage[league.spieltage.length - 1])}
                </p>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Footer Info */}
      <Card className="p-4 bg-gray-50 dark:bg-slate-800">
        <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
          Datenquelle: <code className="bg-gray-200 dark:bg-slate-900 px-2 py-1 rounded">meta.json</code> |
          Automatisch generiert vom Handball Scraper
        </p>
      </Card>
    </div>
  );
}
