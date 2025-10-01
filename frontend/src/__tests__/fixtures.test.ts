/**
 * Frontend fixture validation tests
 *
 * These tests ensure frontend expectations match backend fixture structure
 * and prevent drift between frontend and backend data contracts.
 */

// Import fixtures as if they were backend responses
import simpleFixture from '../__fixtures__/orchestration/simple.json';
import detailedFixture from '../__fixtures__/orchestration/detailed.json';
import errorFixture from '../__fixtures__/orchestration/error.json';

// Define expected types based on backend schema
interface OrchestrationResults {
  ultra_synthesis?: any;
  formatted_synthesis?: string;
  initial_responses?: {
    responses: Record<string, {
      text: string;
      word_count: number;
      preview: string;
    }>;
    model_count: number;
    successful_models: string[];
  };
  meta_analysis?: {
    responses: Record<string, {
      text: string;
      word_count: number;
      preview: string;
    }>;
    revision_count: number;
    models_with_revisions: string[];
  };
  pipeline_summary?: {
    stages_completed: string[];
    total_models_used: string[];
    stage_count: number;
    success: boolean;
    metadata?: {
      timestamp: string;
      pipeline_version: string;
    };
  };
  formatted_output?: any;
}

interface AnalysisResponse {
  success: boolean;
  results: OrchestrationResults;
  error?: string;
  processing_time?: number;
  saved_files?: Record<string, string>;
  pipeline_info?: {
    correlation_id?: string;
    stages?: Array<{
      name: string;
      status: string;
      models?: string[];
    }>;
    error_stage?: string;
    failed_models?: string[];
    available_providers?: string[];
    required_providers?: string[];
  };
}

describe('Orchestration Fixtures', () => {
  describe('TypeScript Compatibility', () => {
    test('simple fixture matches expected AnalysisResponse structure', () => {
      const fixture: AnalysisResponse = simpleFixture;

      // Required fields
      expect(typeof fixture.success).toBe('boolean');
      expect(fixture.results).toBeDefined();
      expect(typeof fixture.results).toBe('object');

      // Success case validation
      expect(fixture.success).toBe(true);
      expect(fixture.error).toBeUndefined();

      // Results structure
      expect(fixture.results.ultra_synthesis).toBeDefined();
      expect(fixture.results.pipeline_summary).toBeDefined();

      // Optional fields
      expect(fixture.processing_time).toBeDefined();
      expect(typeof fixture.processing_time).toBe('number');
    });

    test('detailed fixture includes all optional sections', () => {
      const fixture: AnalysisResponse = detailedFixture;

      expect(fixture.success).toBe(true);
      expect(fixture.results.ultra_synthesis).toBeDefined();
      expect(fixture.results.initial_responses).toBeDefined();
      expect(fixture.results.meta_analysis).toBeDefined();
      expect(fixture.results.pipeline_summary).toBeDefined();
      expect(fixture.results.formatted_output).toBeDefined();

      // Validate detailed structure
      expect(fixture.results.initial_responses?.model_count).toBeGreaterThan(0);
      expect(fixture.results.meta_analysis?.revision_count).toBeGreaterThanOrEqual(0);
    });

    test('error fixture has proper error structure', () => {
      const fixture: AnalysisResponse = errorFixture;

      // Error case validation
      expect(fixture.success).toBe(false);
      expect(fixture.error).toBeDefined();
      expect(typeof fixture.error).toBe('string');
      expect(fixture.error!.length).toBeGreaterThan(0);

      // Empty results on error
      expect(fixture.results).toEqual({});

      // Pipeline info for debugging
      expect(fixture.pipeline_info).toBeDefined();
      expect(fixture.pipeline_info?.error_stage).toBeDefined();
    });
  });

  describe('Field Consistency', () => {
    test('all fixtures have consistent processing_time format', () => {
      [simpleFixture, detailedFixture, errorFixture].forEach(fixture => {
        if (fixture.processing_time !== undefined) {
          expect(typeof fixture.processing_time).toBe('number');
          expect(fixture.processing_time).toBeGreaterThan(0);
        }
      });
    });

    test('success fixtures have non-empty results', () => {
      [simpleFixture, detailedFixture].forEach(fixture => {
        expect(fixture.success).toBe(true);
        expect(Object.keys(fixture.results).length).toBeGreaterThan(0);
      });
    });

    test('error fixture has empty results and error message', () => {
      expect(errorFixture.success).toBe(false);
      expect(Object.keys(errorFixture.results).length).toBe(0);
      expect(errorFixture.error).toBeDefined();
      expect(errorFixture.error!.length).toBeGreaterThan(0);
    });
  });

  describe('Data Integrity', () => {
    test('ultra_synthesis has required fields when present', () => {
      [simpleFixture, detailedFixture].forEach(fixture => {
        const ultra = fixture.results.ultra_synthesis;
        if (ultra) {
          expect(ultra.text || ultra).toBeDefined();
          if (typeof ultra === 'object') {
            expect(ultra.word_count).toBeDefined();
            expect(typeof ultra.word_count).toBe('number');
          }
        }
      });
    });

    test('initial_responses has consistent model counts', () => {
      if (detailedFixture.results.initial_responses) {
        const { responses, model_count } = detailedFixture.results.initial_responses;
        expect(Object.keys(responses).length).toBe(model_count);
      }
    });

    test('pipeline_summary has valid stage information', () => {
      [simpleFixture, detailedFixture].forEach(fixture => {
        const summary = fixture.results.pipeline_summary;
        if (summary) {
          expect(summary.stages_completed).toBeDefined();
          expect(Array.isArray(summary.stages_completed)).toBe(true);
          expect(summary.total_models_used).toBeDefined();
          expect(Array.isArray(summary.total_models_used)).toBe(true);
          expect(summary.stage_count).toBeDefined();
          expect(typeof summary.stage_count).toBe('number');
        }
      });
    });

    test('formatted_output matches OutputFormatter structure when present', () => {
      if (detailedFixture.results.formatted_output) {
        const formatted = detailedFixture.results.formatted_output;

        // Should have synthesis section
        expect(formatted.synthesis).toBeDefined();

        // Should match the main synthesis data
        expect(formatted.synthesis_model).toBeDefined();
        expect(formatted.initial_responses).toBeDefined();
        expect(formatted.pipeline_summary).toBeDefined();
        expect(formatted.full_document).toBeDefined();
      }
    });
  });

  describe('Cross-Fixture Validation', () => {
    test('consistent correlation_id format across fixtures', () => {
      [simpleFixture, detailedFixture, errorFixture].forEach(fixture => {
        if (fixture.pipeline_info?.correlation_id) {
          expect(typeof fixture.pipeline_info.correlation_id).toBe('string');
          expect(fixture.pipeline_info.correlation_id.length).toBeGreaterThan(0);
          // Should follow pattern: prefix_number format
          expect(/^[a-zA-Z_]+_\d+$/.test(fixture.pipeline_info.correlation_id)).toBe(true);
        }
      });
    });

    test('error fixture has debugging information', () => {
      expect(errorFixture.pipeline_info).toBeDefined();
      expect(errorFixture.pipeline_info?.error_stage).toBeDefined();
      expect(errorFixture.pipeline_info?.failed_models).toBeDefined();
      expect(Array.isArray(errorFixture.pipeline_info?.failed_models)).toBe(true);
    });

    test('processing_time values are reasonable', () => {
      [simpleFixture, detailedFixture, errorFixture].forEach(fixture => {
        if (fixture.processing_time !== undefined) {
          // Should be between 0.1 seconds and 5 minutes (300 seconds)
          expect(fixture.processing_time).toBeGreaterThan(0.1);
          expect(fixture.processing_time).toBeLessThan(300);
        }
      });
    });
  });

  describe('Frontend Usage Compatibility', () => {
    test('fixtures can be used as mock API responses', () => {
      // Simulate API response structure
      const mockApiResponse = (fixture: any) => ({
        data: fixture,
        status: 200,
        statusText: 'OK'
      });

      [simpleFixture, detailedFixture, errorFixture].forEach(fixture => {
        const response = mockApiResponse(fixture);

        // Should have expected response structure
        expect(response.data).toBeDefined();
        expect(response.status).toBe(200);

        // Data should match original fixture
        expect(response.data.success).toBe(fixture.success);
        expect(response.data.results).toEqual(fixture.results);
      });
    });

    test('error fixture triggers appropriate error handling', () => {
      const errorResponse = errorFixture;

      // Frontend error handling would check these fields
      expect(errorResponse.success).toBe(false);
      expect(errorResponse.error).toBeDefined();
      expect(errorResponse.error!.includes('unavailable')).toBe(true);

      // Should not have successful results
      expect(Object.keys(errorResponse.results).length).toBe(0);
    });

    test('detailed fixture provides all expected data sections', () => {
      const detailed = detailedFixture;

      // Frontend components expect these sections to be available
      expect(detailed.results.ultra_synthesis).toBeDefined();
      expect(detailed.results.initial_responses).toBeDefined();
      expect(detailed.results.meta_analysis).toBeDefined();
      expect(detailed.results.pipeline_summary).toBeDefined();

      // Should be able to access nested data safely
      expect(detailed.results.initial_responses?.responses).toBeDefined();
      expect(detailed.results.meta_analysis?.responses).toBeDefined();
    });
  });
});