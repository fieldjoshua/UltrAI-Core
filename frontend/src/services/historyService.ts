import { AnalysisResponse } from '../types/analysis';

interface HistoryEntry {
  id: string;
  timestamp: string;
  prompt: string;
  selectedModels: string[];
  pattern: string;
  results: AnalysisResponse['results'];
}

export const historyService = {
  getHistory(): HistoryEntry[] {
    try {
      const history = localStorage.getItem('analysis_history');
      return history ? JSON.parse(history) : [];
    } catch (error) {
      console.error('Error reading history:', error);
      return [];
    }
  },

  addToHistory(entry: Omit<HistoryEntry, 'id' | 'timestamp'>): void {
    try {
      const history = this.getHistory();
      const newEntry: HistoryEntry = {
        ...entry,
        id: `history_${Date.now()}`,
        timestamp: new Date().toISOString(),
      };

      // Keep only the last 50 entries
      const updatedHistory = [newEntry, ...history].slice(0, 50);
      localStorage.setItem('analysis_history', JSON.stringify(updatedHistory));
    } catch (error) {
      console.error('Error saving to history:', error);
    }
  },

  clearHistory(): void {
    try {
      localStorage.removeItem('analysis_history');
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  },

  removeFromHistory(id: string): void {
    try {
      const history = this.getHistory();
      const updatedHistory = history.filter(entry => entry.id !== id);
      localStorage.setItem('analysis_history', JSON.stringify(updatedHistory));
    } catch (error) {
      console.error('Error removing from history:', error);
    }
  },

  getHistoryEntry(id: string): HistoryEntry | null {
    try {
      const history = this.getHistory();
      return history.find(entry => entry.id === id) || null;
    } catch (error) {
      console.error('Error getting history entry:', error);
      return null;
    }
  },
};
