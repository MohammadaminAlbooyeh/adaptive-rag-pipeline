import React from 'react';

function StrategyFlow() {
  return (
    <div className="strategy-flow">
      <h3>Strategy Decision Flow</h3>
      <div className="flow-diagram">
        <div className="node">Query</div>
        <div className="arrow">&darr;</div>
        <div className="node">Classifier</div>
        <div className="arrow">&darr;</div>
        <div className="node">Strategy Selector</div>
      </div>
    </div>
  );
}

export default StrategyFlow;
