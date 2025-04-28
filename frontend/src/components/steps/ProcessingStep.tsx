import React from 'react';
import { Button } from '../ui/button'; // Adjust path
import { Progress } from '../ui/progress'; // Adjust path
import { RefreshCw, Brain } from 'lucide-react';

interface ProcessingStepProps {
  progress: number;
  progressMessage: string;
  error: string | null;
  onRetry: () => void; // Function to trigger a retry if there's an error
}

const ProcessingStep: React.FC<ProcessingStepProps> = ({
  progress,
  progressMessage,
  error,
  onRetry,
}) => {
  return (
    <div className="space-y-6 py-8 px-4 md:px-8 fadeIn">
      <div className="flex flex-col items-center">
        <h2 className="text-xl font-semibold mb-6 text-cyan-200">
          Processing Your Request
        </h2>

        <div className="w-full mb-8">
          <Progress value={progress} className="h-2 bg-gray-800" />
          <p className="text-sm text-gray-400 mt-2 text-center">
            {progressMessage}
          </p>

          {/* Render retry button if there's an error during processing */}
          {error && (
            <div className="mt-4 flex justify-center">
              <Button
                variant="outline"
                size="sm"
                className="flex items-center space-x-2 text-amber-400 border-amber-600 hover:bg-amber-900/30"
                onClick={onRetry} // Use the passed-in retry handler
              >
                <RefreshCw className="h-4 w-4 mr-1" />
                Retry Request
              </Button>
            </div>
          )}
        </div>

        {/* Animated processing indicator */}
        <div className="relative h-32 w-32 mb-6">
          <div className="absolute inset-0 opacity-30 rounded-full border-4 border-cyan-500"></div>
          <div className="absolute inset-0 rounded-full border-t-4 border-cyan-300 animate-spin"></div>
          <div className="absolute inset-2 rounded-full border-b-4 border-pink-500 animate-spin animate-delay-500"></div>
          <div className="absolute inset-4 rounded-full border-r-4 border-green-400 animate-spin animate-delay-1000"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <Brain className="h-12 w-12 text-cyan-400 opacity-80" />
          </div>
        </div>

        <div className="text-center max-w-md">
          <h3 className="text-lg font-medium text-white mb-2">
            AI Models Working Together
          </h3>
          <p className="text-gray-400 text-sm">
            Multiple AI models are analyzing your prompt and synthesizing
            results. This typically takes 15-30 seconds depending on complexity.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingStep;
