import { useState, useCallback } from 'react';
import { analyzePrompt, AnalysisPayload, AnalysisResponse } from '../services/api'; // Adjust path

export const useAnalysisExecution = () => {
    const [isProcessing, setIsProcessing] = useState<boolean>(false);
    const [isComplete, setIsComplete] = useState<boolean>(false);
    const [output, setOutput] = useState<string>('');
    const [error, setError] = useState<string | null>(null);
    const [progress, setProgress] = useState<number>(0);
    const [progressMessage, setProgressMessage] = useState<string>('');
    const [isCached, setIsCached] = useState<boolean>(false);

    // Function to simulate progress updates (can be customized or removed)
    const simulateProgress = useCallback(async () => {
        updateProgress(20, 'Sending request...');
        await new Promise((r) => setTimeout(r, 200));
        updateProgress(40, 'Processing with models...');
        await new Promise((r) => setTimeout(r, 800));
        updateProgress(60, 'Generating insights...');
        await new Promise((r) => setTimeout(r, 700));
        updateProgress(80, 'Comparing results...');
        await new Promise((r) => setTimeout(r, 500));
        updateProgress(100, 'Finalizing output...');
        await new Promise((r) => setTimeout(r, 300));
    }, []); // No dependencies needed if updateProgress is stable

    // Helper to update progress state
    const updateProgress = useCallback((percent: number, message: string) => {
        setProgress(percent);
        setProgressMessage(message);
    }, []);

    // Main analysis execution function
    const executeAnalysis = useCallback(
        async (payload: AnalysisPayload): Promise<{ output: string; cached: boolean }> => {
            setIsProcessing(true);
            setProgress(0);
            setProgressMessage('Initializing analysis...');
            setError(null);
            setOutput('');
            setIsComplete(false);
            setIsCached(false);

            try {
                // Start simulated progress alongside API call
                // simulateProgress(); // Removed simulation for actual API call timing
                updateProgress(10, 'Sending analysis request...');

                const startTime = performance.now();
                const data = await analyzePrompt(payload);
                const endTime = performance.now();

                updateProgress(100, 'Analysis complete!');

                console.log(`Analysis API call took ${((endTime - startTime) / 1000).toFixed(2)} seconds`);

                setOutput(data.ultra_response || 'No response received');
                setIsCached(data.cached || false);
                setIsComplete(true);
                setIsProcessing(false);
                return { output: data.ultra_response || '', cached: data.cached || false };

            } catch (apiError: any) {
                console.error('Analysis execution failed:', apiError);
                const errorMessage = `Analysis failed: ${apiError.message || 'Unknown API error'}`;
                setError(errorMessage);

                // Fallback or indicate error in output
                const mockOutput = `# Analysis Error\n\n${errorMessage}`;
                setOutput(mockOutput);
                setIsCached(false); // Definitely not cached if error
                setIsProcessing(false);
                setIsComplete(true); // Mark as complete to show error output
                // Re-throw or return specific error info if needed by caller
                throw new Error(errorMessage);
            }
        },
        [updateProgress] // Dependency on updateProgress
    );

    // Function to reset execution state
    const resetExecutionState = useCallback(() => {
        setIsProcessing(false);
        setIsComplete(false);
        setOutput('');
        setError(null);
        setProgress(0);
        setProgressMessage('');
        setIsCached(false);
    }, []);

    return {
        isProcessing,
        isComplete,
        output,
        error,
        progress,
        progressMessage,
        isCached,
        executeAnalysis,
        updateProgress, // Expose if needed externally
        resetExecutionState,
    };
};