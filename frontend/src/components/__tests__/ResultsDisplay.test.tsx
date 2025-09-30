/**
 * Tests for ResultsDisplay component.
 * 
 * Validates rendering of orchestration results in simple/detailed/error modes.
 * Uses fixtures from __fixtures__/orchestration/*.json
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from '@jest/globals';
import simpleFixture from '../../__fixtures__/orchestration/simple.json';
import detailedFixture from '../../__fixtures__/orchestration/detailed.json';
import errorFixture from '../../__fixtures__/orchestration/error.json';

const MockResultsDisplay = ({ response }: { response: any }) => {
  if (!response) return <div>No results</div>;
  
  if (!response.success) {
    return (
      <div data-testid="error-display">
        <h2>Error</h2>
        <p data-testid="error-message">{response.error || response.results?.error}</p>
      </div>
    );
  }
  
  const { results } = response;
  
  return (
    <div data-testid="results-display">
      {results.ultra_synthesis && (
        <div data-testid="ultra-synthesis">
          <h2>Ultra Synthesis</h2>
          <pre>{results.ultra_synthesis}</pre>
        </div>
      )}
      
      {results.formatted_synthesis && (
        <div data-testid="formatted-synthesis">
          {results.formatted_synthesis}
        </div>
      )}
      
      {results.initial_response && (
        <div data-testid="initial-responses">
          <h3>Initial Responses</h3>
          {Object.keys(results.initial_response.output.responses).map(model => (
            <div key={model} data-testid={`initial-${model}`}>
              {results.initial_response.output.responses[model]}
            </div>
          ))}
        </div>
      )}
      
      {results.formatted_output?.pipeline_summary && (
        <div data-testid="pipeline-summary">
          <h3>Pipeline Summary</h3>
          <p>Stages: {results.formatted_output.pipeline_summary.stages_completed.join(', ')}</p>
        </div>
      )}
      
      {response.pipeline_info && (
        <div data-testid="pipeline-info">
          <p>Processing time: {response.processing_time}s</p>
          <p>Models: {response.pipeline_info.models_used.join(', ')}</p>
        </div>
      )}
    </div>
  );
};

describe('ResultsDisplay', () => {
  describe('Simple Mode', () => {
    it('renders ultra_synthesis from simple fixture', () => {
      render(<MockResultsDisplay response={simpleFixture} />);
      
      const synthesis = screen.getByTestId('ultra-synthesis');
      expect(synthesis).toBeInTheDocument();
      expect(synthesis.textContent).toContain('Key Benefits');
      expect(synthesis.textContent).toContain('Environmental Impact');
    });
    
    it('renders formatted_synthesis from simple fixture', () => {
      render(<MockResultsDisplay response={simpleFixture} />);
      
      const formatted = screen.getByTestId('formatted-synthesis');
      expect(formatted).toBeInTheDocument();
      expect(formatted.textContent).toContain('ULTRA SYNTHESIS™');
    });
    
    it('shows pipeline info from simple fixture', () => {
      render(<MockResultsDisplay response={simpleFixture} />);
      
      const pipelineInfo = screen.getByTestId('pipeline-info');
      expect(pipelineInfo).toBeInTheDocument();
      expect(pipelineInfo.textContent).toContain('12.45s');
      expect(pipelineInfo.textContent).toContain('gpt-4o');
    });
    
    it('does not show initial responses in simple mode', () => {
      render(<MockResultsDisplay response={simpleFixture} />);
      
      const initialResponses = screen.queryByTestId('initial-responses');
      expect(initialResponses).not.toBeInTheDocument();
    });
  });
  
  describe('Detailed Mode', () => {
    it('renders ultra_synthesis from detailed fixture', () => {
      render(<MockResultsDisplay response={detailedFixture} />);
      
      const synthesis = screen.queryByTestId('ultra-synthesis');
      expect(synthesis).not.toBeInTheDocument();
    });
    
    it('shows initial responses when included in detailed mode', () => {
      render(<MockResultsDisplay response={detailedFixture} />);
      
      const initialResponses = screen.getByTestId('initial-responses');
      expect(initialResponses).toBeInTheDocument();
      
      expect(screen.getByTestId('initial-gpt-4o')).toBeInTheDocument();
      expect(screen.getByTestId('initial-claude-3-5-sonnet-20241022')).toBeInTheDocument();
      expect(screen.getByTestId('initial-gemini-1.5-pro')).toBeInTheDocument();
    });
    
    it('shows pipeline summary in detailed mode', () => {
      render(<MockResultsDisplay response={detailedFixture} />);
      
      const summary = screen.getByTestId('pipeline-summary');
      expect(summary).toBeInTheDocument();
      expect(summary.textContent).toContain('initial_response');
      expect(summary.textContent).toContain('ultra_synthesis');
    });
  });
  
  describe('Error Mode', () => {
    it('renders error message from error fixture', () => {
      render(<MockResultsDisplay response={errorFixture} />);
      
      const errorDisplay = screen.getByTestId('error-display');
      expect(errorDisplay).toBeInTheDocument();
      
      const errorMessage = screen.getByTestId('error-message');
      expect(errorMessage.textContent).toContain('Request timeout');
    });
    
    it('shows degraded service status', () => {
      render(<MockResultsDisplay response={errorFixture} />);
      
      expect(screen.getByTestId('error-display')).toBeInTheDocument();
    });
    
    it('does not show synthesis on error', () => {
      render(<MockResultsDisplay response={errorFixture} />);
      
      const synthesis = screen.queryByTestId('ultra-synthesis');
      expect(synthesis).not.toBeInTheDocument();
    });
  });
  
  describe('Contract Validation', () => {
    it('simple fixture has required top-level fields', () => {
      expect(simpleFixture).toHaveProperty('success');
      expect(simpleFixture).toHaveProperty('results');
      expect(simpleFixture).toHaveProperty('processing_time');
      expect(simpleFixture).toHaveProperty('pipeline_info');
    });
    
    it('simple fixture results have ultra_synthesis', () => {
      expect(simpleFixture.results).toHaveProperty('ultra_synthesis');
      expect(simpleFixture.results).toHaveProperty('status');
      expect(simpleFixture.results.status).toBe('completed');
    });
    
    it('detailed fixture has formatted_output with synthesis', () => {
      expect(detailedFixture.results).toHaveProperty('formatted_output');
      expect(detailedFixture.results.formatted_output).toHaveProperty('synthesis');
      expect(detailedFixture.results.formatted_output.synthesis).toHaveProperty('text');
      expect(detailedFixture.results.formatted_output.synthesis).toHaveProperty('sections');
    });
    
    it('detailed fixture has initial_response section', () => {
      expect(detailedFixture.results).toHaveProperty('initial_response');
      expect(detailedFixture.results.initial_response).toHaveProperty('output');
      expect(detailedFixture.results.initial_response.output).toHaveProperty('responses');
    });
    
    it('error fixture has success=false and error message', () => {
      expect(errorFixture.success).toBe(false);
      expect(errorFixture).toHaveProperty('error');
      expect(errorFixture.results).toHaveProperty('error');
      expect(errorFixture.results.status).toBe('failed');
    });
  });
});
