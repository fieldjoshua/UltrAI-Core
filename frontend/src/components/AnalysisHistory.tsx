import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { historyService } from '../services/historyService';
import { AnalysisResponse } from '../types/analysis';

interface AnalysisHistoryProps {
  onSelectHistory: (entry: {
    prompt: string;
    selectedModels: string[];
    pattern: string;
    results: AnalysisResponse['results'];
  }) => void;
}

export const AnalysisHistory: React.FC<AnalysisHistoryProps> = ({
  onSelectHistory,
}) => {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    setHistory(historyService.getHistory());
  }, []);

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      historyService.clearHistory();
      setHistory([]);
    }
  };

  const handleRemoveEntry = (id: string) => {
    historyService.removeFromHistory(id);
    setHistory(history.filter(entry => entry.id !== id));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (history.length === 0) {
    return (
      <Card className="p-4">
        <div className="text-center text-gray-500">
          No analysis history available.
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Analysis History</h3>
        <Button variant="outline" size="sm" onClick={handleClearHistory}>
          Clear History
        </Button>
      </div>
      <ScrollArea className="h-[400px]">
        <div className="space-y-4">
          {history.map(entry => (
            <Card key={entry.id} className="p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium">{entry.prompt}</p>
                  <p className="text-sm text-gray-500">
                    {formatDate(entry.timestamp)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveEntry(entry.id)}
                >
                  Remove
                </Button>
              </div>
              <div className="text-sm text-gray-600 mb-2">
                <p>Models: {entry.selectedModels.join(', ')}</p>
                <p>Pattern: {entry.pattern}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => onSelectHistory(entry)}
              >
                Load Analysis
              </Button>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
};
