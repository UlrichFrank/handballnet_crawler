import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useEffect } from 'react';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { LeagueProvider } from './contexts/LeagueContext';
import { ThemeToggle } from './components/ThemeToggle';
import { Navigation } from './components/Navigation';
import { HandballPage } from './pages/HandballPage';
import { StandingsPage } from './pages/StandingsPage';
import { OfficialsPage } from './pages/OfficialsPage';
import { StatisticsPage } from './pages/StatisticsPage';
import { StatusPage } from './pages/StatusPage';
import teamLogoUrl from '../public/team-logo.svg?url';

function AppContent() {
    const { theme } = useTheme();

    // Apply theme class to HTML element
    useEffect(() => {
        console.log('[AppContent useEffect] theme changed to:', theme)
        const html = document.documentElement;
        
        if (theme === 'dark') {
            html.classList.add('dark');
            console.log('[AppContent] Added dark class, HTML now:', html.className)
        } else {
            html.classList.remove('dark');
            console.log('[AppContent] Removed dark class, HTML now:', html.className)
        }
    }, [theme]);

    return (
        <LeagueProvider>
            <Router basename={import.meta.env.BASE_URL}>
                <div className="min-h-screen bg-white dark:bg-slate-950 text-gray-900 dark:text-gray-100 transition-colors duration-300">
                    <div className="border-b border-gray-200 dark:border-slate-700 p-4">
                        <div className="flex justify-between items-center mb-4">
                            <Link to="/" className="flex items-center gap-2 text-3xl font-bold text-blue-900 dark:text-blue-400 hover:opacity-80 transition-opacity cursor-pointer">
                                <img src={teamLogoUrl} alt="Handball Crawler Logo" className="h-10 w-10 object-contain" />
                                <span>handball.net Crawler</span>
                            </Link>
                            <ThemeToggle />
                        </div>
                        <Navigation />
                    </div>

                    <div className="p-4">
                        <Routes>
                            <Route path="/" element={<HandballPage />} />
                            <Route path="/handball" element={<HandballPage />} />
                            <Route path="/standings" element={<StandingsPage />} />
                            <Route path="/officials" element={<OfficialsPage />} />
                            <Route path="/statistics" element={<StatisticsPage />} />
                            <Route path="/status" element={<StatusPage />} />
                        </Routes>
                    </div>
                </div>
            </Router>
        </LeagueProvider>
    );
}

function App() {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
}

export default App;
