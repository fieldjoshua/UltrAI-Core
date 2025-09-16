import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import AnalysisForm from '../AnalysisForm';
import * as apiService from '../../services/api';

// Mock the API service
vi.mock('../../services/api', () => ({
  fetchAvailableModels: vi.fn(),
  analyzePrompt: vi.fn(),
}));

// Helper function to render component with router
const renderWithRouter = ui => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe('AnalysisForm Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks();

    // Setup default mock responses
    apiService.fetchAvailableModels.mockResolvedValue([
      'gpt4o',
      'claude37',
      'gemini15',
    ]);

    apiService.analyzePrompt.mockResolvedValue({
      status: 'success',
      analysis_id: 'test-analysis-id',
      results: {
        model_responses: {
          gpt4o: 'Test response from GPT-4o',
          claude37: 'Test response from Claude 3.7',
        },
        ultra_response: 'Combined ultra response from all models',
        performance: {
          total_time_seconds: 3.5,
          model_times: {
            gpt4o: 2.1,
            claude37: 2.8,
          },
          token_counts: {
            gpt4o: {
              prompt_tokens: 50,
              completion_tokens: 150,
              total_tokens: 200,
            },
            claude37: {
              prompt_tokens: 45,
              completion_tokens: 160,
              total_tokens: 205,
            },
          },
        },
      },
    });
  });

  test('renders the form with all required elements', () => {
    renderWithRouter(<AnalysisForm />);

    // Verify form elements are present
    expect(screen.getByLabelText(/prompt/i)).toBeInTheDocument();
    expect(screen.getByText(/run analysis/i)).toBeInTheDocument();

    // Model selection should load after API call resolves
    expect(apiService.fetchAvailableModels).toHaveBeenCalled();
  });

  test('loads available models on mount', async () => {
    renderWithRouter(<AnalysisForm />);

    // Wait for models to load
    await waitFor(() => {
      expect(apiService.fetchAvailableModels).toHaveBeenCalled();
    });

    // Models should be displayed after loading
    await waitFor(() => {
      expect(screen.getByText(/gpt4o/i)).toBeInTheDocument();
      expect(screen.getByText(/claude37/i)).toBeInTheDocument();
      expect(screen.getByText(/gemini15/i)).toBeInTheDocument();
    });
  });

  test('shows error when models fail to load', async () => {
    // Mock API failure
    apiService.fetchAvailableModels.mockRejectedValue(
      new Error('Failed to load models')
    );

    renderWithRouter(<AnalysisForm />);

    // Wait for error to appear
    await waitFor(() => {
      expect(screen.getByText(/failed to load models/i)).toBeInTheDocument();
    });
  });

  test('submits analysis request with correct data', async () => {
    renderWithRouter(<AnalysisForm />);

    // Wait for models to load
    await waitFor(() => {
      expect(apiService.fetchAvailableModels).toHaveBeenCalled();
    });

    // Fill out the form
    const promptInput = screen.getByLabelText(/prompt/i);
    fireEvent.change(promptInput, {
      target: { value: 'Test analysis prompt' },
    });

    // Select a model (assumes model checkboxes are rendered)
    await waitFor(() => {
      const modelCheckbox = screen.getByLabelText(/gpt4o/i);
      fireEvent.click(modelCheckbox);
    });

    // Select a pattern (assumes pattern radio buttons are rendered)
    await waitFor(() => {
      const patternRadio = screen.getByLabelText(/confidence/i);
      fireEvent.click(patternRadio);
    });

    // Submit the form
    const submitButton = screen.getByText(/run analysis/i);
    fireEvent.click(submitButton);

    // Verify API call was made with correct parameters
    await waitFor(() => {
      expect(apiService.analyzePrompt).toHaveBeenCalledWith({
        prompt: 'Test analysis prompt',
        selected_models: expect.arrayContaining(['gpt4o']),
        ultra_model: 'gpt4o',
        pattern: 'confidence',
        options: expect.any(Object),
      });
    });
  });

  test('displays loading state during analysis', async () => {
    // Mock delayed response
    apiService.analyzePrompt.mockImplementation(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            status: 'success',
            results: {
              ultra_response: 'Test response',
            },
          });
        }, 100);
      });
    });

    renderWithRouter(<AnalysisForm />);

    // Fill out the form
    const promptInput = screen.getByLabelText(/prompt/i);
    fireEvent.change(promptInput, { target: { value: 'Test prompt' } });

    // Submit the form
    const submitButton = screen.getByText(/run analysis/i);
    fireEvent.click(submitButton);

    // Check loading indicator appears
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();

    // Verify loading state disappears after response
    await waitFor(() => {
      expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
    });
  });

  test('displays error when analysis fails', async () => {
    // Mock API failure
    apiService.analyzePrompt.mockRejectedValue(new Error('Analysis failed'));

    renderWithRouter(<AnalysisForm />);

    // Fill out the form
    const promptInput = screen.getByLabelText(/prompt/i);
    fireEvent.change(promptInput, { target: { value: 'Test prompt' } });

    // Submit the form
    const submitButton = screen.getByText(/run analysis/i);
    fireEvent.click(submitButton);

    // Check error message appears
    await waitFor(() => {
      expect(screen.getByText(/analysis failed/i)).toBeInTheDocument();
    });
  });

  test('displays results after successful analysis', async () => {
    renderWithRouter(<AnalysisForm />);

    // Fill out the form
    const promptInput = screen.getByLabelText(/prompt/i);
    fireEvent.change(promptInput, { target: { value: 'Test prompt' } });

    // Submit the form
    const submitButton = screen.getByText(/run analysis/i);
    fireEvent.click(submitButton);

    // Check results are displayed
    await waitFor(() => {
      expect(
        screen.getByText(/combined ultra response from all models/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/test response from gpt-4o/i)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/test response from claude 3.7/i)
      ).toBeInTheDocument();
    });

    // Check performance metrics are displayed
    await waitFor(() => {
      expect(screen.getByText(/3.5s/i)).toBeInTheDocument(); // Total time
      expect(screen.getByText(/200/i)).toBeInTheDocument(); // Token count
    });
  });
});
