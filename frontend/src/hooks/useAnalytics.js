import { useState, useCallback } from 'react';
import { getAnalytics } from '../services/analytics_api';

export function useAnalytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    const data = await getAnalytics();
    setStats(data);
    setLoading(false);
  }, []);

  return { stats, loading, fetchStats };
}
