import { useState, useCallback } from 'react';
import { submitQuery } from '../services/rag_api';

export function useAdaptiveRAG() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const query = useCallback(async (text) => {
    setLoading(true);
    setError(null);
    try {
      const res = await submitQuery(text);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, result, error, query };
}
