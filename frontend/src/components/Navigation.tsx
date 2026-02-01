import { Flex, Button } from '@radix-ui/themes';
import { NavLink, useLocation } from 'react-router-dom';
import { BarChartIcon, TableIcon } from '@radix-ui/react-icons';
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
    path: '/officials',
    label: 'Spielleitung',
    icon: BarChartIcon,
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
    <Flex gap="4" wrap="wrap" align="center" justify="between">
      <Flex gap="4" wrap="wrap">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <Button
              key={item.path}
              asChild
              variant="ghost"
              size="2"
              color={active ? "blue" : "gray"}
              style={{ 
                backgroundColor: active ? 'var(--accent-3)' : 'transparent',
                minWidth: 'fit-content'
              }}
            >
              <NavLink to={item.path} style={{ textDecoration: 'none' }}>
                <Icon />
                {item.label}
              </NavLink>
            </Button>
          );
        })}
      </Flex>
      
      <div style={{ minWidth: '250px' }}>
        <LeagueSelector
          leagues={leagues}
          selectedLeague={selectedLeague}
          onLeagueChange={setSelectedLeague}
        />
      </div>
    </Flex>
  );
}
