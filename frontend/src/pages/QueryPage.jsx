import React, { useState } from 'react';
import QueryInput from '../components/QueryInput';
import AnswerDisplay from '../components/AnswerDisplay';
import StrategyBadge from '../components/StrategyBadge';
import SourcesList from '../components/SourcesList';
import ConfidenceScore from '../components/ConfidenceScore';
import GraderResults from '../components/GraderResults';
import LoadingSpinner from '../components/LoadingSpinner';

function QueryPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleQuery = async (query) => {
    setLoading(true);
    setResult(null);
    setResult({ answer: 'Sample answer', strategy: 'document_rag', sources: [], confidence: 0.85 });
    setLoading(false);
  };

  return (
    <div className="query-page">
      <QueryInput onSubmit={handleQuery} />
      {loading && <LoadingSpinner />}
      {result && (
        <div className="results">
          <StrategyBadge strategy={result.strategy} />
          <ConfidenceScore score={result.confidence} />
          <AnswerDisplay answer={result.answer} />
          <SourcesList sources={result.sources} />
          <GraderResults grading={result.grading} />
        </div>
      )}
    </div>
  );
}

export default QueryPage;
