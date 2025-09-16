// Models API implementation
import axios from 'axios';
import type { Model } from './types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function getModels(): Promise<Model[]> {
  try {
    const response = await axios.get(`${API_BASE}/models`);
    return response.data.models || [];
  } catch (error) {
    console.error('Error fetching models:', error);
    return [];
  }
}

export async function getModelStatus(modelId: string): Promise<{ status: string; details?: any }> {
  try {
    const response = await axios.get(`${API_BASE}/models/${modelId}/status`);
    return response.data;
  } catch (error) {
    console.error('Error fetching model status:', error);
    throw error;
  }
}