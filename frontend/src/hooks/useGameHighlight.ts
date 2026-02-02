import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

interface HighlightState {
  type: 'game' | 'official' | null;
  id: string | null;
}

/**
 * Hook zur Verwaltung von Highlight-Status aus URL-Query-Parametern
 * Unterstützt:
 * - ?highlightGame=date-home-away (für Game-Highlighting)
 * - ?highlightOfficial=name&role=referee (für Official-Highlighting)
 */
export function useGameHighlight() {
  const [searchParams] = useSearchParams();
  const [highlight, setHighlight] = useState<HighlightState>({ type: null, id: null });

  useEffect(() => {
    const highlightGame = searchParams.get('highlightGame');
    const highlightOfficial = searchParams.get('highlightOfficial');

    if (highlightGame) {
      setHighlight({ type: 'game', id: highlightGame });
    } else if (highlightOfficial) {
      setHighlight({ type: 'official', id: highlightOfficial });
    } else {
      setHighlight({ type: null, id: null });
    }
  }, [searchParams]);

  const applyHighlight = (element: HTMLElement | null) => {
    if (!element || !highlight.id) return;

    // Scroll into view
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Add highlight class
    element.classList.add(
      'bg-yellow-100',
      'dark:bg-yellow-900/30',
      'ring-2',
      'ring-yellow-400',
      'highlight-active'
    );

    // Auto-remove after 3 seconds
    const timeout = setTimeout(() => {
      element.classList.remove(
        'bg-yellow-100',
        'dark:bg-yellow-900/30',
        'ring-2',
        'ring-yellow-400',
        'highlight-active'
      );
    }, 3000);

    return () => clearTimeout(timeout);
  };

  const clearHighlight = () => {
    setHighlight({ type: null, id: null });
  };

  return {
    highlight,
    isHighlightActive: highlight.type !== null && highlight.id !== null,
    applyHighlight,
    clearHighlight,
  };
}

/**
 * Utility-Funktionen für URL-Encoding von Game-Daten
 */
export const GameHighlightUtils = {
  encodeGame: (game: { date: string; home: string; away: string }) => {
    return `${game.date}-${encodeURIComponent(game.home)}-${encodeURIComponent(game.away)}`;
  },

  decodeGame: (encoded: string): { date: string; home: string; away: string } | null => {
    const parts = encoded.split('-');
    if (parts.length < 3) return null;
    
    // Split on first two dashes, rest is the second team name
    const match = encoded.match(/^([^-]+)-(.+)-(.+)$/);
    if (!match) return null;
    
    return {
      date: match[1],
      home: decodeURIComponent(match[2]),
      away: decodeURIComponent(match[3]),
    };
  },

  encodeOfficial: (name: string, role: string) => {
    return `${encodeURIComponent(name)}&role=${encodeURIComponent(role)}`;
  },

  decodeOfficial: (encoded: string): { name: string; role: string } | null => {
    const parts = encoded.split('&role=');
    if (parts.length !== 2) return null;
    return {
      name: decodeURIComponent(parts[0]),
      role: decodeURIComponent(parts[1]),
    };
  },
};

/**
 * Helper-Hook für Navigation mit Highlight
 */
export function useNavigateWithHighlight() {
  const navigate = useNavigate();

  return (
    path: string,
    queryType: 'game' | 'official',
    queryValue: string
  ) => {
    const params = new URLSearchParams();
    if (queryType === 'game') {
      params.set('highlightGame', queryValue);
    } else if (queryType === 'official') {
      params.set('highlightOfficial', queryValue);
    }
    navigate(`${path}?${params.toString()}`);
  };
}

