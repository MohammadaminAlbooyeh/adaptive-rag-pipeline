import React from 'react';

const STRATEGY_COLORS = {
  direct_llm: 'green',
  document_rag: 'blue',
  web_search_rag: 'orange',
  hybrid_rag: 'purple',
  graph_rag: 'red',
  self_rag: 'teal',
};

function StrategyBadge({ strategy }) {
  const color = STRATEGY_COLORS[strategy] || 'gray';
  return (
    <span className="strategy-badge" style={{ backgroundColor: color }}>
      {strategy.replace('_', ' ')}
    </span>
  );
}

export default StrategyBadge;
