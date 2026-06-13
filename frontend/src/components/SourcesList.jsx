import React from 'react';

function SourcesList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-list">
      <h3>Sources</h3>
      <ul>
        {sources.map((source, i) => (
          <li key={i}>{source}</li>
        ))}
      </ul>
    </div>
  );
}

export default SourcesList;
