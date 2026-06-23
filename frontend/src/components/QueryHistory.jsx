import React from 'react';
import { useQueryHistory } from '../hooks/useQueryHistory';

function QueryHistory({ onSelect }) {
  const { history, loading, error, clearHistory } = useQueryHistory();

  if (loading) return <div className="query-history"><h3>Recent Queries</h3><p>Loading...</p></div>;
  if (error) return <div className="query-history"><h3>Recent Queries</h3><p className="error">{error}</p></div>;

  return (
    <div className="query-history">
      <div className="query-history-header">
        <h3>Recent Queries</h3>
        {history.length > 0 && (
          <button className="clear-btn" onClick={clearHistory}>Clear</button>
        )}
      </div>
      {history.length === 0 ? (
        <p className="empty-state">No queries yet. Submit a query to see history.</p>
      ) : (
        <ul>
          {history.map((item, index) => (
            <li key={index} onClick={() => onSelect && onSelect(item)} className="history-item">
              <span className="history-query">{item.query ? (item.query.length > 50 ? item.query.slice(0, 50) + '...' : item.query) : 'Unknown query'}</span>
              <span className="history-meta">
                {item.strategy && <span className="history-strategy">{item.strategy}</span>}
                {item.timestamp && <span className="history-time">{new Date(item.timestamp).toLocaleString()}</span>}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default QueryHistory;
