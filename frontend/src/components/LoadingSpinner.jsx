import React from 'react';

function LoadingSpinner() {
  return (
    <div className="loading-spinner">
      <div className="spinner"></div>
      <p>Processing your query...</p>
    </div>
  );
}

export default LoadingSpinner;
