import { useLeague } from '../contexts/LeagueContext';

export function OfficialsPage() {
  const { selectedLeague } = useLeague();

  if (!selectedLeague) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">No League Selected</div>
          <div className="text-gray-500 dark:text-gray-400">Please select a league from the dropdown above.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6 bg-gray-50 dark:bg-slate-950 min-h-screen">
      <div>
        <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-400 mb-2">Spielleitung</h1>
        <p className="text-gray-600 dark:text-gray-400">Übersicht der Schiedsrichter, Zeitnehmer und Sekretäre</p>
      </div>

      <div className="space-y-6">
        {/* Referees */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">🏆 Schiedsrichter</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Schiedsrichter 1</span>
              <span className="text-gray-600 dark:text-gray-400">12 Spiele geleitet</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Schiedsrichter 2</span>
              <span className="text-gray-600 dark:text-gray-400">10 Spiele geleitet</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Schiedsrichter 3</span>
              <span className="text-gray-600 dark:text-gray-400">11 Spiele geleitet</span>
            </div>
          </div>
        </div>

        {/* Timekeepers */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">⏱️ Zeitnehmer</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Zeitnehmer 1</span>
              <span className="text-gray-600 dark:text-gray-400">8 Spiele</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Zeitnehmer 2</span>
              <span className="text-gray-600 dark:text-gray-400">9 Spiele</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Zeitnehmer 3</span>
              <span className="text-gray-600 dark:text-gray-400">10 Spiele</span>
            </div>
          </div>
        </div>

        {/* Secretaries */}
        <div className="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-400 mb-4">📋 Sekretäre</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Sekretär 1</span>
              <span className="text-gray-600 dark:text-gray-400">9 Spiele</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Sekretär 2</span>
              <span className="text-gray-600 dark:text-gray-400">8 Spiele</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 dark:border-slate-700 pb-3">
              <span className="text-gray-900 dark:text-gray-100 font-semibold">Sekretär 3</span>
              <span className="text-gray-600 dark:text-gray-400">10 Spiele</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
