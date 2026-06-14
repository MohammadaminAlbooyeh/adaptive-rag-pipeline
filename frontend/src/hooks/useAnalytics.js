import { useState, useCallback, useEffect } from 'react';
import { getAnalytics } from '../services/analytics_api';

export function useAnalytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalytics();
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
      setAnalytics({
        total_queries: 0,
        avg_latency: 0,
        avg_confidence: 0,
        success_rate: 0,
        strategy_distribution: {},
        top_queries: [],
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, [fetchAnalytics]);

  return { analytics, loading, error, fetchAnalytics };
}
