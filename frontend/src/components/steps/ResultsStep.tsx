import React, { RefObject } from 'react';
import { Button } from '../ui/button'; // Adjust path
import { RefreshCw, History, Save, Share2 } from 'lucide-react';

interface ResultsStepProps {
    prompt: string;
    output: string;
    isOffline: boolean;
    outputRef: RefObject<HTMLDivElement>;
    onStartNewAnalysis: () => void;
    onShowHistory: () => void;
    onShareAnalysis: () => void;
    onSaveToHistory: () => void;
}

const ResultsStep: React.FC<ResultsStepProps> = ({
    prompt,
    output,
    isOffline,
    outputRef,
    onStartNewAnalysis,
    onShowHistory,
    onShareAnalysis,
    onSaveToHistory,
}) => {
    return (
        <div className="space-y-6 fadeIn" ref={outputRef}>
            <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-medium text-gray-800 dark:text-white">
                        Ultra Analysis Results
                    </h3>
                    <div className="flex items-center space-x-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onSaveToHistory}
                            disabled={isOffline || !output} // Disable if offline or no output
                            className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:underline disabled:opacity-50 disabled:cursor-not-allowed border-blue-300 dark:border-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/30"
                        >
                            <Save className="h-4 w-4" />
                            Save
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={onShareAnalysis}
                            disabled={isOffline || !output} // Disable if offline or no output
                            className="text-sm text-purple-600 dark:text-purple-400 flex items-center gap-1 hover:underline disabled:opacity-50 disabled:cursor-not-allowed border-purple-300 dark:border-purple-700 hover:bg-purple-50 dark:hover:bg-purple-900/30"
                        >
                            <Share2 className="h-4 w-4" />
                            Share
                        </Button>
                    </div>
                </div>

                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4">
                    <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Your Prompt
                    </h4>
                    <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{prompt}</p>
                </div>

                <div className="prose prose-lg dark:prose-invert max-w-none">
                    {output ? (
                        <div className="whitespace-pre-wrap rounded-lg border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-800/50">
                            {output}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <p>No output generated or loaded.</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 mt-8">
                <Button
                    onClick={onStartNewAnalysis}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    disabled={isOffline} // Disable starting new analysis if offline
                >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Start New Analysis
                </Button>

                <Button
                    onClick={onShowHistory}
                    variant="outline"
                    className="border-gray-300 dark:border-gray-700"
                >
                    <History className="h-4 w-4 mr-2" />
                    View History
                </Button>
            </div>
        </div>
    );
};

export default ResultsStep;