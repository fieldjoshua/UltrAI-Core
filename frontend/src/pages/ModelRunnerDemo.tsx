import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Base URL for API (can be overridden from environment)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Model {
  name: string;
}

const ModelRunnerDemo: React.FC = () => {
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [prompt, setPrompt] = useState<string>('');
  const [response, setResponse] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available models on component mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        setIsLoading(true);
        const response = await axios.get(`${API_URL}/api/modelrunner/models`);
        setModels(response.data.models || []);
        if (response.data.models && response.data.models.length > 0) {
          setSelectedModel(response.data.models[0]);
        }
      } catch (err) {
        console.error('Error fetching models:', err);
        setError(
          'Failed to fetch models. Make sure Docker Model Runner is running.'
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchModels();
  }, []);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt) return;

    try {
      setIsLoading(true);
      setResponse('');
      setError(null);

      const response = await axios.post(`${API_URL}/api/modelrunner/generate`, {
        prompt,
        model: selectedModel,
      });

      const apiResponse = response.data.response;
      setResponse(
        typeof apiResponse === 'string'
          ? apiResponse
          : typeof apiResponse === 'object' && apiResponse !== null
            ? JSON.stringify(apiResponse, null, 2)
            : String(apiResponse || 'No response received')
      );
    } catch (err: any) {
      console.error('Error generating response:', err);
      setError(err.response?.data?.detail || 'Failed to generate response');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Docker Model Runner Demo</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Available Models</h2>
        {isLoading && models.length === 0 ? (
          <p>Loading models...</p>
        ) : models.length > 0 ? (
          <div className="mb-4">
            <select
              className="w-full p-2 border rounded"
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
            >
              {models.map(model => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <p>
            No models available. Please make sure Docker Model Runner is
            running.
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Generate Response</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Prompt</label>
            <textarea
              className="w-full p-2 border rounded"
              rows={4}
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Enter your prompt here..."
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || !selectedModel || !prompt}
          >
            {isLoading ? 'Generating...' : 'Generate'}
          </button>
        </form>

        {response && (
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-2">Response</h3>
            <div className="bg-gray-50 p-4 rounded border whitespace-pre-wrap">
              {response}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelRunnerDemo;
