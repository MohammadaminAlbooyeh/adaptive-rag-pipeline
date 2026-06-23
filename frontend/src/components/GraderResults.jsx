import React from 'react';

function GraderResults({ grading }) {
  if (!grading) return null;

  const { relevance_score, is_relevant, hallucination_check, is_grounded, quality_score, answers_query, explanation } = grading;

  const relevanceScore = relevance_score ?? (is_relevant !== undefined ? (is_relevant ? 1 : 0) : null);
  const hallucinated = hallucination_check !== undefined ? hallucination_check : (is_grounded !== undefined ? !is_grounded : null);
  const quality = quality_score ?? (answers_query !== undefined ? (answers_query ? 1 : 0.5) : null);
  const gradeText = grading.explanation || explanation;

  const scoreColor = (score) => {
    if (score >= 0.7) return '#22c55e';
    if (score >= 0.4) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="grader-results">
      <h3>Grading Results</h3>
      <div className="grader-cards">
        {relevanceScore !== null && (
          <div className="grader-card" style={{ borderLeftColor: scoreColor(relevanceScore) }}>
            <div className="grader-card-header">Relevance</div>
            <div className="grader-card-score" style={{ color: scoreColor(relevanceScore) }}>
              {Math.round(relevanceScore * 100)}%
            </div>
            <div className="grader-card-label">{relevanceScore >= 0.5 ? 'Relevant' : 'Not Relevant'}</div>
          </div>
        )}
        {hallucinated !== null && (
          <div className="grader-card" style={{ borderLeftColor: hallucinated ? '#ef4444' : '#22c55e' }}>
            <div className="grader-card-header">Hallucination</div>
            <div className="grader-card-icon">
              {hallucinated ? <span className="icon-fail">&#10007;</span> : <span className="icon-pass">&#10003;</span>}
            </div>
            <div className="grader-card-label">{hallucinated ? 'Hallucination Detected' : 'Grounded'}</div>
          </div>
        )}
        {quality !== null && (
          <div className="grader-card" style={{ borderLeftColor: scoreColor(quality) }}>
            <div className="grader-card-header">Answer Quality</div>
            <div className="grader-card-score" style={{ color: scoreColor(quality) }}>
              {Math.round(quality * 100)}%
            </div>
            <div className="grader-card-label">{quality >= 0.5 ? 'Good' : 'Poor'}</div>
          </div>
        )}
      </div>
      {gradeText && (
        <div className="grader-explanation">
          <strong>Explanation:</strong> {gradeText}
        </div>
      )}
    </div>
  );
}

export default GraderResults;
