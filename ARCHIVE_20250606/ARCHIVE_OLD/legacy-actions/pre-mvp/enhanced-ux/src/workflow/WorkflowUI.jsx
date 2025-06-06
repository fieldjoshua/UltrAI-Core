import React, { useContext, createContext, useState, useEffect } from 'react';
import {
  WorkflowOptimizer,
  WORKFLOW_STATUS,
  STEP_TYPES,
} from './WorkflowOptimizer';

// Create a context for workflow data
const WorkflowContext = createContext(null);

/**
 * Workflow Provider Component
 *
 * Provides workflow functionality to child components.
 */
const WorkflowProvider = ({
  children,
  initialWorkflows = {},
  persistenceKey,
  onWorkflowComplete,
  onStepChange,
  analyticsCallback,
}) => {
  // Initialize workflow optimizer
  const [workflowManager] = useState(
    () =>
      new WorkflowOptimizer({
        persistenceKey,
        onWorkflowComplete,
        onStepChange,
        analyticsCallback,
      })
  );

  // Track active workflow and current step
  const [activeWorkflowId, setActiveWorkflowId] = useState(null);
  const [currentStep, setCurrentStep] = useState(null);
  const [workflowData, setWorkflowData] = useState({});
  const [workflowProgress, setWorkflowProgress] = useState({
    percentage: 0,
    current: 0,
    total: 0,
  });

  // Initialize workflows from props
  useEffect(() => {
    // Register all initial workflows
    Object.entries(initialWorkflows).forEach(([id, config]) => {
      workflowManager.createWorkflow(id, config);
    });

    // Check if there's an active workflow already
    const activeId = workflowManager.activeWorkflowId;
    if (activeId) {
      setActiveWorkflowId(activeId);
      setCurrentStep(workflowManager.getCurrentStep());
      setWorkflowData(workflowManager.getWorkflowData());
      setWorkflowProgress(workflowManager.getProgress());
    }
  }, []);

  // Start a workflow
  const startWorkflow = (workflowId, initialData = {}) => {
    try {
      const step = workflowManager.startWorkflow(workflowId, initialData);
      setActiveWorkflowId(workflowId);
      setCurrentStep(step);
      setWorkflowData(workflowManager.getWorkflowData());
      setWorkflowProgress(workflowManager.getProgress());
      return step;
    } catch (error) {
      console.error('Failed to start workflow:', error);
      return null;
    }
  };

  // Move to next step
  const nextStep = (stepData = {}) => {
    try {
      const result = workflowManager.nextStep(stepData);

      // Check if workflow completed
      if (result && result.status === WORKFLOW_STATUS.COMPLETED) {
        setActiveWorkflowId(null);
        setCurrentStep(null);
        setWorkflowProgress({ percentage: 100, current: 0, total: 0 });
        return result;
      }

      // Update current step state
      setCurrentStep(result);
      setWorkflowData(workflowManager.getWorkflowData());
      setWorkflowProgress(workflowManager.getProgress());
      return result;
    } catch (error) {
      console.error('Failed to advance workflow:', error);
      return null;
    }
  };

  // Go to specific step
  const goToStep = (stepId, stepData = {}) => {
    try {
      const step = workflowManager.goToStep(stepId, stepData);
      setCurrentStep(step);
      setWorkflowData(workflowManager.getWorkflowData());
      setWorkflowProgress(workflowManager.getProgress());
      return step;
    } catch (error) {
      console.error('Failed to navigate to step:', error);
      return null;
    }
  };

  // Pause active workflow
  const pauseWorkflow = () => {
    if (!activeWorkflowId) return false;

    const result = workflowManager.pauseWorkflow();
    if (result) {
      setActiveWorkflowId(null);
      setCurrentStep(null);
    }

    return result;
  };

  // Resume a paused workflow
  const resumeWorkflow = (workflowId) => {
    try {
      const step = workflowManager.resumeWorkflow(workflowId);
      setActiveWorkflowId(workflowId);
      setCurrentStep(step);
      setWorkflowData(workflowManager.getWorkflowData());
      setWorkflowProgress(workflowManager.getProgress());
      return step;
    } catch (error) {
      console.error('Failed to resume workflow:', error);
      return null;
    }
  };

  // Complete current workflow
  const completeWorkflow = () => {
    if (!activeWorkflowId) return null;

    try {
      const result = workflowManager.completeWorkflow();
      setActiveWorkflowId(null);
      setCurrentStep(null);
      setWorkflowProgress({ percentage: 100, current: 0, total: 0 });
      return result;
    } catch (error) {
      console.error('Failed to complete workflow:', error);
      return null;
    }
  };

  // Register a new workflow
  const registerWorkflow = (workflowId, config) => {
    try {
      return workflowManager.createWorkflow(workflowId, config);
    } catch (error) {
      console.error('Failed to register workflow:', error);
      return null;
    }
  };

  // Context value
  const contextValue = {
    // State
    activeWorkflowId,
    currentStep,
    workflowData,
    workflowProgress,

    // Actions
    startWorkflow,
    nextStep,
    goToStep,
    pauseWorkflow,
    resumeWorkflow,
    completeWorkflow,
    registerWorkflow,

    // Raw workflow manager access for advanced usage
    workflowManager,
  };

  return (
    <WorkflowContext.Provider value={contextValue}>
      {children}
    </WorkflowContext.Provider>
  );
};

/**
 * Hook to access workflow functionality
 */
const useWorkflow = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
};

/**
 * Workflow Navigator Component
 *
 * Displays navigation controls for workflow steps.
 */
const WorkflowNavigator = ({
  showProgress = true,
  showStepCount = true,
  allowSkip = false,
  allowBack = true,
  nextButtonLabel = 'Next',
  backButtonLabel = 'Back',
  skipButtonLabel = 'Skip',
  completeButtonLabel = 'Complete',
  className = '',
  style = {},
}) => {
  const {
    currentStep,
    workflowProgress,
    nextStep,
    goToStep,
    completeWorkflow,
  } = useWorkflow();

  if (!currentStep) return null;

  const isLastStep = workflowProgress.current === workflowProgress.total;

  // Navigation element styles
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    gap: '10px',
    ...style,
  };

  const progressStyle = {
    width: '100%',
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  };

  const progressBarStyle = {
    height: '100%',
    width: `${workflowProgress.percentage}%`,
    backgroundColor: '#4a90e2',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  };

  const buttonContainerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '10px',
  };

  const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#4a90e2',
    color: 'white',
  };

  const secondaryButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#f5f5f5',
    color: '#333',
  };

  return (
    <div className={`workflow-navigator ${className}`} style={containerStyle}>
      {showProgress && (
        <div style={progressStyle}>
          <div style={progressBarStyle} />
        </div>
      )}

      {showStepCount && (
        <div style={{ textAlign: 'center', fontSize: '14px', color: '#666' }}>
          Step {workflowProgress.current} of {workflowProgress.total}
        </div>
      )}

      <div style={buttonContainerStyle}>
        <div>
          {allowBack && workflowProgress.current > 1 && (
            <button
              style={secondaryButtonStyle}
              onClick={() => {
                // Find previous step ID
                const prevIndex = workflowProgress.current - 2; // Convert to 0-based index
                goToStep(currentStep.prevStepId);
              }}
            >
              {backButtonLabel}
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {allowSkip && !isLastStep && (
            <button
              style={secondaryButtonStyle}
              onClick={() => nextStep({ skipped: true })}
            >
              {skipButtonLabel}
            </button>
          )}

          <button
            style={primaryButtonStyle}
            onClick={() => (isLastStep ? completeWorkflow() : nextStep())}
          >
            {isLastStep ? completeButtonLabel : nextButtonLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * Workflow Step Component
 *
 * Renders a specific workflow step.
 */
const WorkflowStep = ({ children, stepId, onNext, onBack, validate }) => {
  const { currentStep, nextStep, goToStep } = useWorkflow();

  // Skip rendering if this isn't the current step
  if (!currentStep || currentStep.id !== stepId) {
    return null;
  }

  // Handle next button click with validation
  const handleNext = async (data = {}) => {
    // Validate if needed
    if (validate) {
      const isValid = await validate(data);
      if (!isValid) return;
    }

    // Execute custom handler if provided
    if (onNext) {
      onNext(data, nextStep);
    } else {
      nextStep(data);
    }
  };

  // Handle back button click
  const handleBack = (data = {}) => {
    if (onBack) {
      onBack(data, (targetStepId) => goToStep(targetStepId, data));
    } else if (currentStep.prevStepId) {
      goToStep(currentStep.prevStepId, data);
    }
  };

  // Render children with handlers
  return children({
    step: currentStep,
    onNext: handleNext,
    onBack: handleBack,
  });
};

/**
 * Workflow Progress Component
 *
 * Displays workflow progress information.
 */
const WorkflowProgress = ({
  showPercentage = true,
  showStepCount = true,
  showTitle = false,
  className = '',
  style = {},
}) => {
  const { workflowProgress, activeWorkflowId, workflowManager } = useWorkflow();

  if (!activeWorkflowId) return null;

  // Get workflow title if needed
  let title = '';
  if (showTitle && workflowManager.workflows[activeWorkflowId]) {
    title = workflowManager.workflows[activeWorkflowId].title;
  }

  // Progress element styles
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    gap: '5px',
    ...style,
  };

  const progressBarStyle = {
    width: '100%',
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  };

  const progressFillStyle = {
    height: '100%',
    width: `${workflowProgress.percentage}%`,
    backgroundColor: '#4a90e2',
    borderRadius: '4px',
    transition: 'width 0.3s ease',
  };

  return (
    <div className={`workflow-progress ${className}`} style={containerStyle}>
      {showTitle && title && (
        <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{title}</div>
      )}

      <div style={progressBarStyle}>
        <div style={progressFillStyle} />
      </div>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '14px',
          color: '#666',
        }}
      >
        {showStepCount && (
          <div>
            Step {workflowProgress.current} of {workflowProgress.total}
          </div>
        )}

        {showPercentage && <div>{workflowProgress.percentage}% Complete</div>}
      </div>
    </div>
  );
};

export {
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
  WORKFLOW_STATUS,
  STEP_TYPES,
};

export default {
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
};
