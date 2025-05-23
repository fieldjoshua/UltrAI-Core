import React, { useState } from 'react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { AnalysisResponse } from '../types/analysis';
import { exportUtils, exportFormats } from '../utils/exportUtils';

interface ExportButtonProps {
  results: AnalysisResponse['results'];
  disabled?: boolean;
}

export const ExportButton: React.FC<ExportButtonProps> = ({
  results,
  disabled = false,
}) => {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (
    format: (typeof exportFormats)[keyof typeof exportFormats]
  ) => {
    try {
      setIsExporting(true);
      const content = exportUtils.exportResults(results, format);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `analysis-results-${timestamp}.${format}`;
      exportUtils.downloadFile(content, filename);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export results. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          disabled={disabled || isExporting}
          className="w-full"
        >
          {isExporting ? 'Exporting...' : 'Export Results'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => handleExport(exportFormats.JSON)}>
          Export as JSON
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport(exportFormats.CSV)}>
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport(exportFormats.MARKDOWN)}>
          Export as Markdown
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
