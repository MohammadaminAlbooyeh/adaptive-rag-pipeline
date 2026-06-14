import React from 'react';
import '../styles/SourcesList.css';

function SourcesList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-list">
      <h3>📚 Sources ({sources.length})</h3>
      <div className="sources-content">
        {sources.map((source, i) => (
          <div key={i} className="source-item">
            <div className="source-header">
              <span className="source-name">
                {typeof source === 'object' ? source.source : source}
              </span>
              {typeof source === 'object' && source.score && (
                <span className="source-score">
                  Relevance: {Math.round(source.score * 100)}%
                </span>
              )}
            </div>
            {typeof source === 'object' && source.content && (
              <p className="source-preview">{source.content.substring(0, 150)}...</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default SourcesList;
