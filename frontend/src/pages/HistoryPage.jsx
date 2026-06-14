import React, { useState, useEffect } from 'react';
import { useQueryHistory } from '../hooks/useQueryHistory';
import StrategyBadge from '../components/StrategyBadge';
import ConfidenceScore from '../components/ConfidenceScore';
import '../styles/HistoryPage.css';

function HistoryPage() {
  const { history, loading, error, clearHistory } = useQueryHistory();
  const [selectedQuery, setSelectedQuery] = useState(null);

  const handleDelete = (index) => {
    const newHistory = history.filter((_, i) => i !== index);
    localStorage.setItem('query_history', JSON.stringify(newHistory));
    window.location.reload();
  };

  const handleSelectQuery = (query) => {
    setSelectedQuery(query);
  };

  return (
    <div className="history-page">
      <div className="history-container">
        <h1>📜 Query History</h1>

        <div className="history-controls">
          {history && history.length > 0 && (
            <button className="clear-btn" onClick={clearHistory}>
              🗑️ Clear History
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span>❌</span> {error}
          </div>
        )}

        {loading ? (
          <div className="loading">Loading history...</div>
        ) : history && history.length > 0 ? (
          <div className="history-grid">
            <div className="history-list-column">
              <div className="list-header">Recent Queries</div>
              <div className="history-list">
                {history.map((query, idx) => (
                  <div
                    key={idx}
                    className={`history-item ${
                      selectedQuery === query ? 'selected' : ''
                    }`}
                    onClick={() => handleSelectQuery(query)}
                  >
                    <div className="item-header">
                      <div className="item-query">
                        {query.query.substring(0, 50)}
                        {query.query.length > 50 ? '...' : ''}
                      </div>
                      <button
                        className="delete-icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(idx);
                        }}
                      >
                        ×
                      </button>
                    </div>
                    <div className="item-meta">
                      <StrategyBadge strategy={query.strategy} />
                      <span className="timestamp">
                        {new Date(query.timestamp || Date.now()).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {selectedQuery && (
              <div className="details-column">
                <div className="details-header">Query Details</div>
                <div className="details-content">
                  <div className="detail-section">
                    <h3>Question</h3>
                    <p className="full-query">{selectedQuery.query}</p>
                  </div>

                  <div className="detail-section">
                    <h3>Strategy & Confidence</h3>
                    <div className="badge-group">
                      <StrategyBadge strategy={selectedQuery.strategy} />
                      <ConfidenceScore score={selectedQuery.confidence} />
                    </div>
                  </div>

                  <div className="detail-section">
                    <h3>Answer</h3>
                    <p className="answer">{selectedQuery.answer}</p>
                  </div>

                  {selectedQuery.sources && selectedQuery.sources.length > 0 && (
                    <div className="detail-section">
                      <h3>Sources ({selectedQuery.sources.length})</h3>
                      <div className="sources-list">
                        {selectedQuery.sources.map((source, idx) => (
                          <div key={idx} className="source">
                            <div className="source-title">
                              {typeof source === 'object'
                                ? source.source
                                : source}
                            </div>
                            {typeof source === 'object' && source.score && (
                              <div className="source-score">
                                Relevance: {Math.round(source.score * 100)}%
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedQuery.latency && (
                    <div className="detail-section">
                      <h3>Metrics</h3>
                      <div className="metrics">
                        <div className="metric">
                          <span>Response Time:</span>
                          <strong>{selectedQuery.latency.toFixed(3)}s</strong>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <p>No query history yet.</p>
            <p>Start asking questions to see your query history!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default HistoryPage;
