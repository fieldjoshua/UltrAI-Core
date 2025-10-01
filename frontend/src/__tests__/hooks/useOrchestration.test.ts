import { renderHook, act, waitFor } from '@testing-library/react';
import { useOrchestration } from '../../hooks/useOrchestration';
import * as orchestratorApi from '../../api/orchestrator';

jest.mock('../../api/orchestrator');

const mockProcessWithFeatherOrchestration = orchestratorApi.processWithFeatherOrchestration as jest.MockedFunction<
  typeof orchestratorApi.processWithFeatherOrchestration
>;

describe('useOrchestration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes in idle state', () => {
    const { result } = renderHook(() => useOrchestration());
    
    expect(result.current.status).toBe('idle');
    expect(result.current.isIdle).toBe(true);
    expect(result.current.isProcessing).toBe(false);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.progress).toBe(0);
  });

  it('starts orchestration successfully', async () => {
    const mockResult = {
      ultra_response: 'Test response',
      model_responses: [],
    };
    
    mockProcessWithFeatherOrchestration.mockResolvedValue(mockResult as any);
    
    const { result } = renderHook(() => useOrchestration());
    
    let orchestrationPromise: Promise<any>;
    
    act(() => {
      orchestrationPromise = result.current.startOrchestration({
        prompt: 'Test prompt',
        models: ['gpt-4', 'claude-3-opus'],
        pattern: 'comparative',
      });
    });
    
    // Should be processing
    expect(result.current.isProcessing).toBe(true);
    expect(result.current.status).toBe('processing');
    
    await act(async () => {
      await orchestrationPromise;
    });
    
    // Should be success
    expect(result.current.isSuccess).toBe(true);
    expect(result.current.status).toBe('success');
    expect(result.current.result).toEqual(mockResult);
    expect(result.current.progress).toBe(100);
  });

  it('handles orchestration errors', async () => {
    const mockError = new Error('Network error');
    mockProcessWithFeatherOrchestration.mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useOrchestration());
    
    await act(async () => {
      try {
        await result.current.startOrchestration({
          prompt: 'Test prompt',
          models: ['gpt-4'],
        });
      } catch (err) {
        // Expected to throw
      }
    });
    
    expect(result.current.isError).toBe(true);
    expect(result.current.status).toBe('error');
    expect(result.current.error).toEqual(mockError);
    expect(result.current.result).toBeNull();
  });

  it('resets state', async () => {
    const mockResult = {
      ultra_response: 'Test response',
    };
    
    mockProcessWithFeatherOrchestration.mockResolvedValue(mockResult as any);
    
    const { result } = renderHook(() => useOrchestration());
    
    await act(async () => {
      await result.current.startOrchestration({
        prompt: 'Test',
        models: ['gpt-4'],
      });
    });
    
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.status).toBe('idle');
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.progress).toBe(0);
  });

  it('updates progress during processing', async () => {
    const mockResult = { ultra_response: 'Test' };
    
    // Delay the response to observe progress
    mockProcessWithFeatherOrchestration.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockResult as any), 100))
    );
    
    const { result } = renderHook(() => useOrchestration());
    
    act(() => {
      result.current.startOrchestration({
        prompt: 'Test',
        models: ['gpt-4'],
      });
    });
    
    // Wait a bit for progress to update
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 50));
    });
    
    // Progress should have increased
    expect(result.current.progress).toBeGreaterThan(0);
    expect(result.current.progress).toBeLessThan(100);
  });

  it('calls API with correct parameters', async () => {
    const mockResult = { ultra_response: 'Test' };
    mockProcessWithFeatherOrchestration.mockResolvedValue(mockResult as any);
    
    const { result } = renderHook(() => useOrchestration());
    
    const params = {
      prompt: 'Analyze market trends',
      models: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
      pattern: 'comparative',
      ultraModel: 'gpt-4o',
      outputFormat: 'markdown',
    };
    
    await act(async () => {
      await result.current.startOrchestration(params);
    });
    
    expect(mockProcessWithFeatherOrchestration).toHaveBeenCalledWith(params);
    expect(mockProcessWithFeatherOrchestration).toHaveBeenCalledTimes(1);
  });

  it('provides correct state flags', () => {
    const { result } = renderHook(() => useOrchestration());
    
    // Idle
    expect(result.current.isIdle).toBe(true);
    expect(result.current.isProcessing).toBe(false);
    expect(result.current.isSuccess).toBe(false);
    expect(result.current.isError).toBe(false);
  });
});
