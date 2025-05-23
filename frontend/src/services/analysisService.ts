import { AnalysisRequest, AnalysisResponse } from '../types/analysis';

const API_BASE_URL = '/api';

export const analysisService = {
  async analyzePrompt(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Analysis failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    }
  },

  async getAnalysisProgress(analysisId: string): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/analyze/${analysisId}/progress`
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to get analysis progress');
      }

      return await response.json();
    } catch (error) {
      console.error('Progress check error:', error);
      throw error;
    }
  },

  async getAnalysisResults(analysisId: string): Promise<any> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/analyze/${analysisId}/results`
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to get analysis results');
      }

      return await response.json();
    } catch (error) {
      console.error('Results fetch error:', error);
      throw error;
    }
  },
};
