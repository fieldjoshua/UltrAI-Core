/**
 * Contract drift guard test for frontend.
 * 
 * This test imports backend sample JSON files and validates their structure.
 * Fails if backend changes break frontend expectations.
 */

import { describe, it, expect } from '@jest/globals';

const simpleSample = require('../../../reports/samples/analysis_response_simple.json');
const detailedSample = require('../../../reports/samples/analysis_response_detailed.json');
const errorSample = require('../../../reports/samples/analysis_response_error.json');

describe('Backend Contract Drift Guard', () => {
  describe('Simple Mode Response', () => {
    it('has required top-level fields', () => {
      expect(simpleSample).toHaveProperty('success');
      expect(simpleSample).toHaveProperty('results');
      expect(simpleSample).toHaveProperty('processing_time');
      expect(simpleSample).toHaveProperty('pipeline_info');
    });
    
    it('has results with ultra_synthesis or formatted_synthesis', () => {
      expect(simpleSample.success).toBe(true);
      const hasUltraSynthesis = 'ultra_synthesis' in simpleSample.results;
      const hasFormattedSynthesis = 'formatted_synthesis' in simpleSample.results;
      expect(hasUltraSynthesis || hasFormattedSynthesis).toBe(true);
    });
    
    it('has completed status', () => {
      expect(simpleSample.results.status).toBe('completed');
    });
    
    it('has pipeline_info with models_used array', () => {
      expect(Array.isArray(simpleSample.pipeline_info.models_used)).toBe(true);
      expect(simpleSample.pipeline_info.models_used.length).toBeGreaterThan(0);
    });
  });
  
  describe('Detailed Mode Response', () => {
    it('has required top-level fields', () => {
      expect(detailedSample).toHaveProperty('success');
      expect(detailedSample).toHaveProperty('results');
      expect(detailedSample).toHaveProperty('processing_time');
    });
    
    it('has formatted_output with synthesis field', () => {
      expect(detailedSample.results).toHaveProperty('formatted_output');
      expect(detailedSample.results.formatted_output).toHaveProperty('synthesis');
      
      const synthesis = detailedSample.results.formatted_output.synthesis;
      expect(synthesis).toHaveProperty('text');
      expect(synthesis).toHaveProperty('sections');
      expect(Array.isArray(synthesis.sections)).toBe(true);
    });
    
    it('has pipeline_summary', () => {
      expect(detailedSample.results.formatted_output).toHaveProperty('pipeline_summary');
      const summary = detailedSample.results.formatted_output.pipeline_summary;
      
      expect(summary).toHaveProperty('stages_completed');
      expect(summary).toHaveProperty('total_models_used');
      expect(summary).toHaveProperty('success');
      expect(Array.isArray(summary.stages_completed)).toBe(true);
    });
    
    it('has full_document string', () => {
      expect(detailedSample.results.formatted_output).toHaveProperty('full_document');
      expect(typeof detailedSample.results.formatted_output.full_document).toBe('string');
    });
  });
  
  describe('Error Mode Response', () => {
    it('has success=false', () => {
      expect(errorSample.success).toBe(false);
    });
    
    it('has error message', () => {
      const hasTopLevelError = errorSample.error !== null;
      const hasResultsError = errorSample.results && errorSample.results.error;
      expect(hasTopLevelError || hasResultsError).toBe(true);
    });
    
    it('has failed status', () => {
      expect(errorSample.results.status).toBe('failed');
    });
    
    it('includes partial pipeline_info on error', () => {
      expect(errorSample).toHaveProperty('pipeline_info');
      expect(errorSample.pipeline_info).toHaveProperty('stages_completed');
      expect(Array.isArray(errorSample.pipeline_info.stages_completed)).toBe(true);
    });
  });
  
  describe('Cross-Sample Consistency', () => {
    it('all samples have consistent top-level structure', () => {
      const samples = [simpleSample, detailedSample, errorSample];
      
      samples.forEach((sample, index) => {
        expect(sample).toHaveProperty('success');
        expect(sample).toHaveProperty('results');
        expect(typeof sample.success).toBe('boolean');
        expect(typeof sample.results).toBe('object');
      });
    });
    
    it('processing_time is numeric when present', () => {
      const samples = [simpleSample, detailedSample, errorSample];
      
      samples.forEach(sample => {
        if (sample.processing_time !== null) {
          expect(typeof sample.processing_time).toBe('number');
          expect(sample.processing_time).toBeGreaterThan(0);
        }
      });
    });
    
    it('pipeline_info has consistent structure across samples', () => {
      const samples = [simpleSample, detailedSample, errorSample];
      
      samples.forEach(sample => {
        if (sample.pipeline_info) {
          expect(sample.pipeline_info).toHaveProperty('stages_completed');
          expect(sample.pipeline_info).toHaveProperty('total_stages');
          expect(sample.pipeline_info).toHaveProperty('models_used');
          expect(Array.isArray(sample.pipeline_info.stages_completed)).toBe(true);
          expect(Array.isArray(sample.pipeline_info.models_used)).toBe(true);
        }
      });
    });
  });
  
  describe('Breaking Change Detection', () => {
    it('detects if success field type changed', () => {
      expect(typeof simpleSample.success).toBe('boolean');
      expect(typeof detailedSample.success).toBe('boolean');
      expect(typeof errorSample.success).toBe('boolean');
    });
    
    it('detects if results shape changed', () => {
      expect(simpleSample.results).toBeInstanceOf(Object);
      expect(detailedSample.results).toBeInstanceOf(Object);
      expect(errorSample.results).toBeInstanceOf(Object);
    });
    
    it('detects if pipeline_info removed', () => {
      expect(simpleSample).toHaveProperty('pipeline_info');
      expect(detailedSample).toHaveProperty('pipeline_info');
      expect(errorSample).toHaveProperty('pipeline_info');
    });
    
    it('detects if ultra_synthesis field renamed in simple mode', () => {
      const hasExpectedField = 
        'ultra_synthesis' in simpleSample.results || 
        'formatted_synthesis' in simpleSample.results;
      
      expect(hasExpectedField).toBe(true);
    });
  });
});
