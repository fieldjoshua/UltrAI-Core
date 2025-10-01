import React, { useState } from 'react';

interface QueryStepProps {
  onNext: (query: string) => void;
}

export const QueryStep: React.FC<QueryStepProps> = ({ onNext }) => {
  const [query, setQuery] = useState('');

  const handleNext = () => {
    if (query.trim()) {
      onNext(query);
    }
  };

  return (
    <div className="query-step">
      <h2>What is your query?</h2>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your query here..."
        rows={5}
      />
      <button onClick={handleNext} disabled={!query.trim()}>Next</button>
    </div>
  );
};