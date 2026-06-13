import React from 'react';

function GraderResults({ grading }) {
  if (!grading) return null;

  return (
    <div className="grader-results">
      <h3>Grading Results</h3>
      <pre>{JSON.stringify(grading, null, 2)}</pre>
    </div>
  );
}

export default GraderResults;
