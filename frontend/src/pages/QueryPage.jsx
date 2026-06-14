import React, { useState } from 'react';
import QueryInput from '../components/QueryInput';
import AnswerDisplay from '../components/AnswerDisplay';
import StrategyBadge from '../components/StrategyBadge';
import SourcesList from '../components/SourcesList';
import ConfidenceScore from '../components/ConfidenceScore';
import GraderResults from '../components/GraderResults';
import LoadingSpinner from '../components/LoadingSpinner';
import StrategyFlow from '../components/StrategyFlow';
import { useAdaptiveRAG } from '../hooks/useAdaptiveRAG';
import '../styles/QueryPage.css';

function QueryPage() {
  const { loading, result, error, query } = useAdaptiveRAG();
  const [queryHistory, setQueryHistory] = useState([]);

  const handleQuery = async (text) => {
    await query(text);
  };

  React.useEffect(() => {
    if (result) {
      setQueryHistory((prev) => [result, ...prev.slice(0, 9)]);
    }
  }, [result]);

  return (
    <div className="query-page">
      <div className="query-container">
        <h1>Ask Your Question</h1>
        <p className="subtitle">
          The system will automatically select the best retrieval strategy
        </p>
        <QueryInput onSubmit={handleQuery} disabled={loading} />

        {error && (
          <div className="error-message">
            <span>❌</span> {error}
          </div>
        )}

        {loading && <LoadingSpinner />}

        {result && (
          <div className="results-container">
            <div className="results-header">
              <h2>Results</h2>
              <div className="result-meta">
                <ConfidenceScore score={result.confidence} />
                <span className="latency">⏱️ {result.latency}s</span>
              </div>
            </div>

            <div className="results-grid">
              <div className="results-main">
                <StrategyBadge strategy={result.strategy} />
                <AnswerDisplay answer={result.answer} />
                {result.sources && result.sources.length > 0 && (
                  <SourcesList sources={result.sources} />
                )}
              </div>

              <div className="results-sidebar">
                <StrategyFlow classification={result.classification} />
              </div>
            </div>
          </div>
        )}

        {queryHistory.length > 0 && !result && (
          <div className="history-preview">
            <h3>Recent Queries</h3>
            <div className="history-list">
              {queryHistory.slice(0, 5).map((item, idx) => (
                <div
                  key={idx}
                  className="history-item"
                  onClick={() => handleQuery(item.query)}
                >
                  <div className="history-query">{item.query}</div>
                  <div className="history-strategy">{item.strategy}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default QueryPage;
