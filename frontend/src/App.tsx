import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Theme } from '@radix-ui/themes';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { LeagueProvider } from './contexts/LeagueContext';
import { ThemeToggle } from './components/ThemeToggle';
import { Navigation } from './components/Navigation';
import { HandballPage } from './pages/HandballPage';
import { StandingsPage } from './pages/StandingsPage';
import { OfficialsPage } from './pages/OfficialsPage';
import '@radix-ui/themes/styles.css';

function AppContent() {
    const { theme } = useTheme();

    return (
        <Theme appearance={theme}>
            <LeagueProvider>
                <Router>
                    <div className="min-h-screen bg-white dark:bg-slate-950 text-gray-900 dark:text-gray-100">
                        <div className="border-b border-gray-200 dark:border-slate-700 p-4">
                            <div className="flex justify-between items-center mb-4">
                                <h1 className="text-3xl font-bold text-blue-900 dark:text-blue-400">🏐 handball.net Grabber</h1>
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
                            </Routes>
                        </div>
                    </div>
                </Router>
            </LeagueProvider>
        </Theme>
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
