import { AnalysisResponse } from '../types/analysis';

export const exportFormats = {
  JSON: 'json',
  CSV: 'csv',
  MARKDOWN: 'markdown',
} as const;

type ExportFormat = (typeof exportFormats)[keyof typeof exportFormats];

export const exportUtils = {
  formatTimestamp(date: string): string {
    return new Date(date).toLocaleString();
  },

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round((seconds % 60) * 100) / 100;
    return `${minutes}m ${remainingSeconds}s`;
  },

  formatTokenCount(count: number): string {
    return count.toLocaleString();
  },

  exportToJSON(results: AnalysisResponse['results']): string {
    return JSON.stringify(results, null, 2);
  },

  exportToCSV(results: AnalysisResponse['results']): string {
    const headers = [
      'Model',
      'Response',
      'Timestamp',
      'Processing Time',
      'Token Count',
    ];
    const rows = results.model_responses.map(response => [
      response.model_name,
      response.content,
      this.formatTimestamp(response.timestamp),
      this.formatDuration(
        results.performance.model_times[response.model_id] || 0
      ),
      this.formatTokenCount(
        results.performance.token_counts[response.model_id] || 0
      ),
    ]);

    return [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');
  },

  exportToMarkdown(results: AnalysisResponse['results']): string {
    const sections = results.model_responses.map(response => {
      const processingTime = this.formatDuration(
        results.performance.model_times[response.model_id] || 0
      );
      const tokenCount = this.formatTokenCount(
        results.performance.token_counts[response.model_id] || 0
      );

      return `## ${response.model_name}
**Timestamp:** ${this.formatTimestamp(response.timestamp)}
**Processing Time:** ${processingTime}
**Token Count:** ${tokenCount}

${response.content}
`;
    });

    return sections.join('\n\n');
  },

  exportResults(
    results: AnalysisResponse['results'],
    format: ExportFormat
  ): string {
    switch (format) {
      case exportFormats.JSON:
        return this.exportToJSON(results);
      case exportFormats.CSV:
        return this.exportToCSV(results);
      case exportFormats.MARKDOWN:
        return this.exportToMarkdown(results);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  },

  downloadFile(content: string, filename: string): void {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
};
