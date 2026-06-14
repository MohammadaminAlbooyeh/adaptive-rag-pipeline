import { useState, useEffect, useCallback } from 'react';

export function useQueryHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    try {
      const stored = localStorage.getItem('query_history');
      setHistory(stored ? JSON.parse(stored) : []);
    } catch (err) {
      setError('Failed to load history');
    } finally {
      setLoading(false);
    }
  }, []);

  const addQuery = useCallback((query) => {
    setHistory((prev) => [
      {
        ...query,
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 99),
    ]);
  }, []);

  const clearHistory = useCallback(() => {
    if (window.confirm('Clear all query history?')) {
      localStorage.removeItem('query_history');
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('query_history', JSON.stringify(history));
  }, [history]);

  return { history, loading, error, addQuery, clearHistory };
}
