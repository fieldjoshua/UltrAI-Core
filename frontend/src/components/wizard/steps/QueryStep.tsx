import React, { useState } from 'react';

interface QueryStepProps {
  query: string;
  onChange: (query: string) => void;
}

export default function QueryStep({ query, onChange }: QueryStepProps) {
  const [charCount, setCharCount] = useState(query.length);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setCharCount(newValue.length);
  };

  const handleOptimize = () => {
    // Simple query optimization - add context
    const optimized = `${query}\n\nPlease provide a detailed analysis with examples and actionable insights.`;
    onChange(optimized);
    setCharCount(optimized.length);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Enter your query</h2>
      <p className="text-gray-400 mb-6">Describe what you need help with. The more detail, the better the results.</p>
      
      <textarea
        value={query}
        onChange={handleChange}
        placeholder="e.g., Analyze market trends for electric vehicles in 2024..."
        className="w-full h-64 p-4 bg-gray-800 border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none resize-none"
        maxLength={1000}
      />
      
      <div className="flex justify-between items-center mt-4">
        <span className="text-sm text-gray-500">{charCount} / 1000</span>
        {query.length > 10 && (
          <button
            onClick={handleOptimize}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm transition-colors"
          >
            ✨ Allow UltrAI to optimize my query
          </button>
        )}
      </div>
    </div>
  );
}
