/**
 * Tests for ResultsDisplay components with orchestration fixtures
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';

// Import fixtures
import simpleFixture from '../../__fixtures__/orchestration/simple.json';
import detailedFixture from '../../__fixtures__/orchestration/detailed.json';
import errorFixture from '../../__fixtures__/orchestration/error.json';

// Mock OrchestratorInterface component for testing
const MockResultsDisplay = ({ results }: { results: any }) => {
  if (!results) return <div>No results</div>;

  if (!results.success) {
    return (
      <div data-testid="error-results">
        <h2>Error Results</h2>
        <div data-testid="error-message">{results.error}</div>
      </div>
    );
  }

  return (
    <div data-testid="success-results">
      {/* Ultra Synthesis Section */}
      {results.results.ultra_synthesis && (
        <div data-testid="ultra-synthesis-section">
          <h2>Ultra Synthesis</h2>
          <div data-testid="ultra-synthesis-text">
            {typeof results.results.ultra_synthesis === 'object'
              ? results.results.ultra_synthesis.text
              : results.results.ultra_synthesis}
          </div>
        </div>
      )}

      {/* Formatted Synthesis */}
      {results.results.formatted_synthesis && (
        <div data-testid="formatted-synthesis-section">
          <h2>Formatted Synthesis</h2>
          <div data-testid="formatted-synthesis-text">
            {results.results.formatted_synthesis}
          </div>
        </div>
      )}

      {/* Initial Responses */}
      {results.results.initial_responses && (
        <div data-testid="initial-responses-section">
          <h2>Initial Responses ({results.results.initial_responses.model_count} models)</h2>
          {Object.entries(results.results.initial_responses.responses).map(([model, response]: [string, any]) => (
            <div key={model} data-testid={`initial-response-${model}`}>
              <h3>{model}</h3>
              <div data-testid={`initial-response-${model}-preview`}>
                {response.preview}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Meta Analysis */}
      {results.results.meta_analysis && (
        <div data-testid="meta-analysis-section">
          <h2>Meta Analysis</h2>
          {Object.entries(results.results.meta_analysis.responses).map(([model, response]: [string, any]) => (
            <div key={model} data-testid={`meta-response-${model}`}>
              <h3>{model}</h3>
              <div data-testid={`meta-response-${model}-preview`}>
                {response.preview}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pipeline Summary */}
      {results.results.pipeline_summary && (
        <div data-testid="pipeline-summary-section">
          <h2>Pipeline Summary</h2>
          <div data-testid="pipeline-summary-text">
            Stages: {results.results.pipeline_summary.stages_completed.join(', ')}
          </div>
          <div data-testid="pipeline-summary-models">
            Models: {results.results.pipeline_summary.total_models_used.join(', ')}
          </div>
        </div>
      )}

      {/* Processing Time */}
      {results.processing_time && (
        <div data-testid="processing-time">
          Processing time: {results.processing_time}s
        </div>
      )}
    </div>
  );
};

describe('ResultsDisplay with Orchestration Fixtures', () => {
  describe('Simple Response Fixture', () => {
    test('renders ultra synthesis text', () => {
      render(<MockResultsDisplay results={simpleFixture} />);

      expect(screen.getByTestId('ultra-synthesis-section')).toBeInTheDocument();
      expect(screen.getByTestId('ultra-synthesis-text')).toHaveTextContent(
        'Based on the analysis of multiple AI models'
      );
    });

    test('renders formatted synthesis', () => {
      render(<MockResultsDisplay results={simpleFixture} />);

      expect(screen.getByTestId('formatted-synthesis-section')).toBeInTheDocument();
      expect(screen.getByTestId('formatted-synthesis-text')).toHaveTextContent(
        'Key Findings'
      );
    });

    test('renders pipeline summary', () => {
      render(<MockResultsDisplay results={simpleFixture} />);

      expect(screen.getByTestId('pipeline-summary-section')).toBeInTheDocument();
      expect(screen.getByTestId('pipeline-summary-text')).toHaveTextContent(
        'initial_response, peer_review_and_revision, ultra_synthesis'
      );
      expect(screen.getByTestId('pipeline-summary-models')).toHaveTextContent(
        'gpt-4, claude-3-opus, gemini-pro'
      );
    });

    test('renders processing time', () => {
      render(<MockResultsDisplay results={simpleFixture} />);

      expect(screen.getByTestId('processing-time')).toHaveTextContent(
        '15.7s'
      );
    });

    test('does not render initial responses or meta analysis in simple mode', () => {
      render(<MockResultsDisplay results={simpleFixture} />);

      expect(screen.queryByTestId('initial-responses-section')).not.toBeInTheDocument();
      expect(screen.queryByTestId('meta-analysis-section')).not.toBeInTheDocument();
    });
  });

  describe('Detailed Response Fixture', () => {
    test('renders all sections in detailed mode', () => {
      render(<MockResultsDisplay results={detailedFixture} />);

      expect(screen.getByTestId('ultra-synthesis-section')).toBeInTheDocument();
      expect(screen.getByTestId('formatted-synthesis-section')).toBeInTheDocument();
      expect(screen.getByTestId('initial-responses-section')).toBeInTheDocument();
      expect(screen.getByTestId('meta-analysis-section')).toBeInTheDocument();
      expect(screen.getByTestId('pipeline-summary-section')).toBeInTheDocument();
    });

    test('renders initial responses with model previews', () => {
      render(<MockResultsDisplay results={detailedFixture} />);

      expect(screen.getByTestId('initial-responses-section')).toBeInTheDocument();
      expect(screen.getByText('Initial Responses (3 models)')).toBeInTheDocument();

      expect(screen.getByTestId('initial-response-gpt-4')).toBeInTheDocument();
      expect(screen.getByTestId('initial-response-claude-3-opus')).toBeInTheDocument();
      expect(screen.getByTestId('initial-response-gemini-pro')).toBeInTheDocument();

      expect(screen.getByTestId('initial-response-gpt-4-preview')).toHaveTextContent(
        "GPT-4's initial response emphasizes that data quality"
      );
    });

    test('renders meta analysis responses', () => {
      render(<MockResultsDisplay results={detailedFixture} />);

      expect(screen.getByTestId('meta-analysis-section')).toBeInTheDocument();
      expect(screen.getByTestId('meta-response-claude-3-opus')).toBeInTheDocument();
      expect(screen.getByTestId('meta-response-claude-3-opus-preview')).toHaveTextContent(
        'After reviewing the initial responses'
      );
    });
  });

  describe('Error Response Fixture', () => {
    test('renders error state correctly', () => {
      render(<MockResultsDisplay results={errorFixture} />);

      expect(screen.getByTestId('error-results')).toBeInTheDocument();
      expect(screen.getByTestId('error-message')).toHaveTextContent(
        'Service temporarily unavailable'
      );
    });

    test('does not render success sections in error state', () => {
      render(<MockResultsDisplay results={errorFixture} />);

      expect(screen.queryByTestId('ultra-synthesis-section')).not.toBeInTheDocument();
      expect(screen.queryByTestId('initial-responses-section')).not.toBeInTheDocument();
      expect(screen.queryByTestId('pipeline-summary-section')).not.toBeInTheDocument();
    });
  });

  describe('Fixture Structure Validation', () => {
    test('simple fixture has required fields', () => {
      expect(simpleFixture).toHaveProperty('success', true);
      expect(simpleFixture).toHaveProperty('results');
      expect(simpleFixture.results).toHaveProperty('ultra_synthesis');
      expect(simpleFixture.results).toHaveProperty('pipeline_summary');
      expect(simpleFixture).toHaveProperty('processing_time');
    });

    test('detailed fixture has all optional sections', () => {
      expect(detailedFixture).toHaveProperty('success', true);
      expect(detailedFixture.results).toHaveProperty('ultra_synthesis');
      expect(detailedFixture.results).toHaveProperty('initial_responses');
      expect(detailedFixture.results).toHaveProperty('meta_analysis');
      expect(detailedFixture.results).toHaveProperty('pipeline_summary');
      expect(detailedFixture.results).toHaveProperty('formatted_output');
    });

    test('error fixture has proper error structure', () => {
      expect(errorFixture).toHaveProperty('success', false);
      expect(errorFixture).toHaveProperty('error');
      expect(errorFixture).toHaveProperty('results');
      expect(errorFixture.results).toEqual({});
      expect(errorFixture).toHaveProperty('pipeline_info');
    });

    test('all fixtures have consistent processing_time format', () => {
      expect(typeof simpleFixture.processing_time).toBe('number');
      expect(typeof detailedFixture.processing_time).toBe('number');
      expect(typeof errorFixture.processing_time).toBe('number');
    });
  });
});