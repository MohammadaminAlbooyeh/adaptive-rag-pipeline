import React from 'react';
import '../styles/StrategyFlow.css';

function StrategyFlow({ classification }) {
  if (!classification) return null;

  const {
    query_type,
    complexity,
    needs_docs,
    needs_web,
    is_time_sensitive,
    needs_graph,
  } = classification;

  const characteristics = [
    { label: 'Type', value: query_type },
    { label: 'Complexity', value: complexity },
    { label: 'Needs Documents', value: needs_docs ? '✓' : '✗' },
    { label: 'Needs Web Search', value: needs_web ? '✓' : '✗' },
    { label: 'Time Sensitive', value: is_time_sensitive ? '✓' : '✗' },
    { label: 'Needs Graph', value: needs_graph ? '✓' : '✗' },
  ];

  return (
    <div className="strategy-flow">
      <h3>🎯 Query Analysis</h3>
      <div className="classification-details">
        {characteristics.map((char, idx) => (
          <div key={idx} className="characteristic">
            <span className="label">{char.label}:</span>
            <span className="value">{char.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default StrategyFlow;
