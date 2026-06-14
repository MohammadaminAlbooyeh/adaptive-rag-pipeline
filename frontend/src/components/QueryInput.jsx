import React, { useState } from 'react';
import '../styles/QueryInput.css';

function QueryInput({ onSubmit, disabled = false }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSubmit(query);
      setQuery('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && e.ctrlKey && !disabled) {
      handleSubmit(e);
    }
  };

  return (
    <form className="query-input" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question... (Ctrl+Enter to submit)"
          disabled={disabled}
          rows="4"
        />
        <button
          type="submit"
          disabled={!query.trim() || disabled}
          className="submit-btn"
        >
          {disabled ? 'Processing...' : 'Ask'}
        </button>
      </div>
    </form>
  );
}

export default QueryInput;
