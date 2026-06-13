import React from 'react';

function AnswerDisplay({ answer }) {
  return (
    <div className="answer-display">
      <h3>Answer</h3>
      <p>{answer}</p>
    </div>
  );
}

export default AnswerDisplay;
