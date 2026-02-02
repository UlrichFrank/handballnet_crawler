import { NavLink, useLocation } from 'react-router-dom';
import { BarChartIcon, TableIcon, InfoCircledIcon } from '@radix-ui/react-icons';
import { LeagueSelector } from './handball/LeagueSelector';
import { useLeague } from '../contexts/LeagueContext';

const navigationItems = [
  {
    path: '/handball',
    label: 'Spieler',
    icon: BarChartIcon,
  },
  {
    path: '/standings',
    label: 'Tabelle',
    icon: TableIcon,
  },
  {
    path: '/statistics',
    label: 'Statistiken',
    icon: BarChartIcon,
  },
  {
    path: '/officials',
    label: 'Spielleitung',
    icon: BarChartIcon,
  },
  {
    path: '/status',
    label: 'Status',
    icon: InfoCircledIcon,
  },
];

export function Navigation() {
  const location = useLocation();
  const { leagues, selectedLeague, setSelectedLeague } = useLeague();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname.startsWith('/project/');
    }
    return location.pathname === path;
  };

  return (
    <div className="flex gap-4 wrap items-center justify-between">
      <div className="flex gap-4 wrap items-center">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                active
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                  : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          );
        })}
      </div>
      
      <div style={{ minWidth: '250px' }}>
        <LeagueSelector
          leagues={leagues}
          selectedLeague={selectedLeague}
          onLeagueChange={setSelectedLeague}
        />
      </div>
    </div>
  );
}
