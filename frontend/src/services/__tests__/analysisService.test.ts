import { analysisService } from '../analysisService';
import { AnalysisRequest } from '../../types/analysis';

// Mock fetch
global.fetch = jest.fn();

describe('analysisService', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  describe('analyzePrompt', () => {
    const mockRequest: AnalysisRequest = {
      prompt: 'Test prompt',
      selected_models: ['gpt-4', 'claude-3'],
      ultra_model: 'ultra-default',
      pattern: 'basic',
    };

    const mockResponse = {
      status: 'success',
      analysis_id: 'test-analysis-123',
      results: {
        model_responses: [
          {
            model_id: 'gpt-4',
            model_name: 'GPT-4',
            content: 'Test response',
            timestamp: '2024-04-28T12:00:00Z',
          },
        ],
        ultra_response: {
          model_id: 'ultra-default',
          model_name: 'Ultra Default',
          content: 'Ultra response',
          timestamp: '2024-04-28T12:00:00Z',
        },
        performance: {
          total_time_seconds: 1.5,
          model_times: { 'gpt-4': 1.0, 'claude-3': 0.5 },
          token_counts: { 'gpt-4': 100, 'claude-3': 50 },
        },
      },
    };

    it('should successfully analyze a prompt', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await analysisService.analyzePrompt(mockRequest);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockRequest),
      });
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Analysis failed';
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ message: errorMessage }),
      });

      await expect(analysisService.analyzePrompt(mockRequest)).rejects.toThrow(
        errorMessage
      );
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(analysisService.analyzePrompt(mockRequest)).rejects.toThrow(
        'Network error'
      );
    });
  });

  describe('getAnalysisProgress', () => {
    const mockProgressResponse = {
      status: 'success',
      progress: {
        stage: 'processing',
        status: 'in_progress',
        progress: 50,
        message: 'Analyzing with GPT-4',
      },
    };

    it('should successfully get analysis progress', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockProgressResponse),
      });

      const result =
        await analysisService.getAnalysisProgress('test-analysis-123');
      expect(result).toEqual(mockProgressResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/analyze/test-analysis-123/progress'
      );
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Failed to get progress';
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ message: errorMessage }),
      });

      await expect(
        analysisService.getAnalysisProgress('test-analysis-123')
      ).rejects.toThrow(errorMessage);
    });
  });

  describe('getAnalysisResults', () => {
    const mockResultsResponse = {
      status: 'success',
      results: {
        model_responses: [
          {
            model_id: 'gpt-4',
            model_name: 'GPT-4',
            content: 'Test response',
            timestamp: '2024-04-28T12:00:00Z',
          },
        ],
        ultra_response: {
          model_id: 'ultra-default',
          model_name: 'Ultra Default',
          content: 'Ultra response',
          timestamp: '2024-04-28T12:00:00Z',
        },
        performance: {
          total_time_seconds: 1.5,
          model_times: { 'gpt-4': 1.0 },
          token_counts: { 'gpt-4': 100 },
        },
      },
    };

    it('should successfully get analysis results', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResultsResponse),
      });

      const result =
        await analysisService.getAnalysisResults('test-analysis-123');
      expect(result).toEqual(mockResultsResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/analyze/test-analysis-123/results'
      );
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Failed to get results';
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ message: errorMessage }),
      });

      await expect(
        analysisService.getAnalysisResults('test-analysis-123')
      ).rejects.toThrow(errorMessage);
    });
  });
});
