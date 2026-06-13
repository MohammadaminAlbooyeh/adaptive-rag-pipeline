import { useState, useCallback } from 'react';

export function useStrategy() {
  const [currentStrategy, setCurrentStrategy] = useState(null);

  const selectStrategy = useCallback((strategy) => {
    setCurrentStrategy(strategy);
  }, []);

  return { currentStrategy, selectStrategy };
}
