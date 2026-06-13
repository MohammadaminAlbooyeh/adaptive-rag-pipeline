import React from 'react';

function ConfidenceScore({ score }) {
  const percentage = Math.round((score || 0) * 100);
  return (
    <div className="confidence-score">
      <span>Confidence: {percentage}%</span>
      <progress value={score} max="1" />
    </div>
  );
}

export default ConfidenceScore;
