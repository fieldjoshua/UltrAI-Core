import { useState, useEffect, useCallback } from 'react';
import { fetchAvailableModels } from '../services/api'; // Import API service

export const useAnalysisConfig = (isOffline: boolean) => {
  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([]);
  const [ultraLLM, setUltraLLM] = useState<string | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedAnalysisType, setSelectedAnalysisType] =
    useState<string>('confidence'); // Default pattern
  const [configError, setConfigError] = useState<string | null>(null);

  // Fetch available models on mount or when online status changes
  useEffect(() => {
    const loadModels = async () => {
      if (isOffline) {
        setConfigError(
          'Offline: Cannot fetch available models. Using defaults or last known.'
        );
        // Optionally load from cache or keep existing if offline
        return;
      }
      try {
        setConfigError(null);
        const models = await fetchAvailableModels();
        setAvailableModels(models);
        // Optional: Validate selections against new list
        setSelectedLLMs(prev => prev.filter(m => models.includes(m)));
        if (ultraLLM && !models.includes(ultraLLM)) {
          setUltraLLM(null);
        }
      } catch (err: any) {
        setConfigError(`Could not fetch available models: ${err.message}`);
        setAvailableModels([]); // Clear models on error
      }
    };

    loadModels();
  }, [isOffline]); // Re-run if offline status changes

  // Toggle LLM selection
  const toggleModelSelection = useCallback(
    (modelId: string) => {
      setSelectedLLMs(prev => {
        if (prev.includes(modelId)) {
          // If removing the ultra model, unset it
          if (ultraLLM === modelId) {
            setUltraLLM(null);
          }
          return prev.filter(id => id !== modelId);
        } else {
          return [...prev, modelId];
        }
      });
    },
    [ultraLLM]
  ); // Dependency on ultraLLM

  // Handle LLM checkbox change
  const handleLLMChange = useCallback(
    (id: string) => {
      toggleModelSelection(id);
    },
    [toggleModelSelection]
  );

  // Handle setting the Ultra model
  const handleUltraChange = useCallback(
    (id: string) => {
      // Ensure the selected ultra model is also in the selected LLMs list
      if (!selectedLLMs.includes(id)) {
        setSelectedLLMs(prev => [...prev, id]);
      }
      setUltraLLM(id);
    },
    [selectedLLMs]
  ); // Dependency on selectedLLMs

  // Handle analysis type change
  const handleAnalysisTypeChange = useCallback((type: string) => {
    setSelectedAnalysisType(type);
  }, []);

  // Function to reset model/pattern state
  const resetAnalysisConfig = useCallback(() => {
    setSelectedLLMs([]);
    setUltraLLM(null);
    setSelectedAnalysisType('confidence'); // Reset to default
    // availableModels is reset by useEffect when online status changes
    setConfigError(null);
  }, []);

  return {
    selectedLLMs,
    ultraLLM,
    availableModels,
    selectedAnalysisType,
    configError,
    handleLLMChange,
    handleUltraChange,
    handleAnalysisTypeChange,
    resetAnalysisConfig,
  };
};
