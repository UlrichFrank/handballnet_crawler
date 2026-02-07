import { NavLink, useLocation } from 'react-router-dom';
import { PlayIcon, TableIcon, BarChartIcon, MixerVerticalIcon, InfoCircledIcon } from '@radix-ui/react-icons';
import { LeagueSelector } from './handball/LeagueSelector';
import { useLeague } from '../contexts/LeagueContext';

const navigationItems = [
  {
    path: '/handball',
    label: 'Spiele',
    icon: PlayIcon,
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
    icon: MixerVerticalIcon,
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
    <div className="flex flex-col gap-3 md:flex-row md:gap-4 md:items-center md:justify-between">
      <div className="flex gap-2 md:gap-4 flex-wrap items-center overflow-x-auto">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`flex items-center gap-1 md:gap-2 px-2 md:px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap text-sm md:text-base ${
                active
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100'
                  : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-800'
              }`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span className="hidden sm:inline">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
      
      <div className="w-full md:w-auto md:min-w-[250px]">
        <LeagueSelector
          leagues={leagues}
          selectedLeague={selectedLeague}
          onLeagueChange={setSelectedLeague}
        />
      </div>
    </div>
  );
}
