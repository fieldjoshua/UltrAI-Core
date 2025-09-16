import React, { useState } from 'react';
import SSEPanel from '../components/panels/SSEPanel';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { AlertCircle, Activity } from 'lucide-react';

const ModelMonitor: React.FC = () => {
  const [correlationId, setCorrelationId] = useState('');
  const [activeId, setActiveId] = useState('');

  const handleMonitor = () => {
    if (correlationId.trim()) {
      setActiveId(correlationId.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Activity className="h-8 w-8 text-blue-600" />
            Model Monitoring Dashboard
          </h1>
          <p className="text-gray-600">
            Monitor real-time orchestration events and model activity
          </p>
        </div>

        <Card className="mb-6 p-6">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label
                htmlFor="correlation-id"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Correlation ID
              </label>
              <Input
                id="correlation-id"
                type="text"
                value={correlationId}
                onChange={e => setCorrelationId(e.target.value)}
                placeholder="Enter correlation ID to monitor"
                className="w-full"
              />
            </div>
            <Button onClick={handleMonitor} disabled={!correlationId.trim()}>
              Start Monitoring
            </Button>
          </div>
          <div className="mt-2 text-sm text-gray-500">
            <AlertCircle className="inline h-4 w-4 mr-1" />
            Tip: You can find the correlation ID in the analysis response or
            request headers
          </div>
        </Card>

        {activeId && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Monitoring: {activeId}
            </h2>
            <SSEPanel
              correlationId={activeId}
              title="Real-Time Model Events"
              maxEvents={200}
            />
          </div>
        )}

        {!activeId && (
          <Card className="p-12 text-center">
            <Activity className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">
              Enter a correlation ID above to start monitoring orchestration
              events
            </p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ModelMonitor;
