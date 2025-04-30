/**
 * WorkflowOptimizer
 *
 * Provides functionality to simplify complex workflows and guide users
 * through multi-step processes with optimal efficiency.
 */

// Workflow status enumeration
const WORKFLOW_STATUS = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  PAUSED: 'paused',
  ERROR: 'error',
};

// Step types for workflow creation
const STEP_TYPES = {
  INPUT: 'input',
  SELECTION: 'selection',
  CONFIRMATION: 'confirmation',
  PROCESSING: 'processing',
  INFORMATION: 'information',
  ACTION: 'action',
};

/**
 * Creates and manages optimized workflows
 */
class WorkflowOptimizer {
  constructor(options = {}) {
    this.workflows = {};
    this.activeWorkflowId = null;
    this.onStepChange = options.onStepChange || (() => {});
    this.onWorkflowComplete = options.onWorkflowComplete || (() => {});
    this.onWorkflowError = options.onWorkflowError || (() => {});
    this.persistenceKey = options.persistenceKey || 'ultraai_workflow_state';
    this.autoSave = options.autoSave !== false;

    // Optional analytics callback
    this.analyticsCallback = options.analyticsCallback;

    // Load saved workflow state if available
    if (options.loadSavedState !== false) {
      this.loadSavedState();
    }
  }

  /**
   * Create a new workflow definition
   * @param {String} workflowId Unique identifier for the workflow
   * @param {Object} workflowConfig Configuration for the workflow
   * @returns {String} The workflow ID
   */
  createWorkflow(workflowId, workflowConfig = {}) {
    if (!workflowId) {
      throw new Error('Workflow ID is required');
    }

    if (this.workflows[workflowId]) {
      console.warn(
        `Workflow with ID "${workflowId}" already exists and will be overwritten`
      );
    }

    const steps = workflowConfig.steps || [];

    // Validate steps
    steps.forEach((step, index) => {
      if (!step.id) {
        throw new Error(`Step at index ${index} is missing an ID`);
      }
      if (!step.type || !Object.values(STEP_TYPES).includes(step.type)) {
        throw new Error(`Step "${step.id}" has an invalid type`);
      }
    });

    this.workflows[workflowId] = {
      id: workflowId,
      title: workflowConfig.title || workflowId,
      description: workflowConfig.description || '',
      category: workflowConfig.category || 'general',
      steps,
      currentStepIndex: 0,
      status: WORKFLOW_STATUS.NOT_STARTED,
      data: {},
      startTime: null,
      endTime: null,
      userCanSkip: workflowConfig.userCanSkip === true,
      userCanPause: workflowConfig.userCanPause !== false,
      autoAdvance: workflowConfig.autoAdvance === true,
      completionCallback: workflowConfig.onComplete,
      errorCallback: workflowConfig.onError,
    };

    return workflowId;
  }

  /**
   * Start a workflow
   * @param {String} workflowId The workflow to start
   * @param {Object} initialData Initial data to populate the workflow
   * @returns {Object} The current workflow step
   */
  startWorkflow(workflowId, initialData = {}) {
    const workflow = this.workflows[workflowId];

    if (!workflow) {
      throw new Error(`Workflow "${workflowId}" not found`);
    }

    // Close any active workflow first
    if (this.activeWorkflowId && this.activeWorkflowId !== workflowId) {
      this.pauseWorkflow(this.activeWorkflowId);
    }

    workflow.status = WORKFLOW_STATUS.IN_PROGRESS;
    workflow.currentStepIndex = 0;
    workflow.data = { ...initialData };
    workflow.startTime = new Date().toISOString();
    workflow.endTime = null;
    this.activeWorkflowId = workflowId;

    // Log workflow start to analytics
    this._logAnalytics('workflow_started', {
      workflowId,
      title: workflow.title,
    });

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return this.getCurrentStep();
  }

  /**
   * Move to the next step in the active workflow
   * @param {Object} stepData Data collected from the current step
   * @returns {Object} The new current step or completion status
   */
  nextStep(stepData = {}) {
    if (!this.activeWorkflowId) {
      throw new Error('No active workflow');
    }

    const workflow = this.workflows[this.activeWorkflowId];
    const currentStep = this.getCurrentStep();

    // Merge step data into workflow data
    workflow.data = {
      ...workflow.data,
      [currentStep.id]: stepData,
    };

    // Check if this was the last step
    if (workflow.currentStepIndex >= workflow.steps.length - 1) {
      return this.completeWorkflow();
    }

    // Move to next step
    workflow.currentStepIndex++;

    // Call the step change callback
    this.onStepChange(this.getCurrentStep(), workflow);

    // Log step transition to analytics
    this._logAnalytics('workflow_step_completed', {
      workflowId: workflow.id,
      stepId: currentStep.id,
      nextStepId: this.getCurrentStep().id,
    });

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return this.getCurrentStep();
  }

  /**
   * Move to a specific step in the active workflow
   * @param {String} stepId ID of the step to navigate to
   * @param {Object} stepData Data from the current step to save
   * @returns {Object} The new current step
   */
  goToStep(stepId, stepData = {}) {
    if (!this.activeWorkflowId) {
      throw new Error('No active workflow');
    }

    const workflow = this.workflows[this.activeWorkflowId];
    const currentStep = this.getCurrentStep();

    // Save current step data if provided
    if (Object.keys(stepData).length > 0) {
      workflow.data = {
        ...workflow.data,
        [currentStep.id]: stepData,
      };
    }

    // Find target step index
    const targetIndex = workflow.steps.findIndex((step) => step.id === stepId);

    if (targetIndex === -1) {
      throw new Error(
        `Step "${stepId}" not found in workflow "${workflow.id}"`
      );
    }

    // Update current step
    workflow.currentStepIndex = targetIndex;

    // Call the step change callback
    this.onStepChange(this.getCurrentStep(), workflow);

    // Log navigation to analytics
    this._logAnalytics('workflow_step_navigation', {
      workflowId: workflow.id,
      fromStepId: currentStep.id,
      toStepId: stepId,
      isBackNavigation: targetIndex < workflow.currentStepIndex,
    });

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return this.getCurrentStep();
  }

  /**
   * Complete the current workflow
   * @returns {Object} Workflow completion status
   */
  completeWorkflow() {
    if (!this.activeWorkflowId) {
      throw new Error('No active workflow');
    }

    const workflow = this.workflows[this.activeWorkflowId];

    workflow.status = WORKFLOW_STATUS.COMPLETED;
    workflow.endTime = new Date().toISOString();

    // Call the completion callbacks
    if (typeof workflow.completionCallback === 'function') {
      workflow.completionCallback(workflow.data, workflow);
    }

    this.onWorkflowComplete(workflow.data, workflow);

    // Log completion to analytics
    this._logAnalytics('workflow_completed', {
      workflowId: workflow.id,
      title: workflow.title,
      duration: new Date(workflow.endTime) - new Date(workflow.startTime),
    });

    // Clear active workflow
    const completedWorkflowId = this.activeWorkflowId;
    this.activeWorkflowId = null;

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return {
      status: WORKFLOW_STATUS.COMPLETED,
      workflowId: completedWorkflowId,
      data: workflow.data,
    };
  }

  /**
   * Pause the current workflow
   * @param {String} workflowId Optional workflow ID to pause
   * @returns {Boolean} Success status
   */
  pauseWorkflow(workflowId = this.activeWorkflowId) {
    if (!workflowId) {
      return false;
    }

    const workflow = this.workflows[workflowId];

    if (!workflow) {
      throw new Error(`Workflow "${workflowId}" not found`);
    }

    if (workflow.status !== WORKFLOW_STATUS.IN_PROGRESS) {
      return false;
    }

    workflow.status = WORKFLOW_STATUS.PAUSED;

    // Log pause to analytics
    this._logAnalytics('workflow_paused', {
      workflowId: workflow.id,
      currentStepId: this.getCurrentStep(workflowId)?.id,
    });

    // Clear active workflow if it's the one being paused
    if (this.activeWorkflowId === workflowId) {
      this.activeWorkflowId = null;
    }

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return true;
  }

  /**
   * Resume a paused workflow
   * @param {String} workflowId ID of workflow to resume
   * @returns {Object} The current workflow step
   */
  resumeWorkflow(workflowId) {
    const workflow = this.workflows[workflowId];

    if (!workflow) {
      throw new Error(`Workflow "${workflowId}" not found`);
    }

    if (workflow.status !== WORKFLOW_STATUS.PAUSED) {
      throw new Error(`Workflow "${workflowId}" is not paused`);
    }

    // Close any active workflow first
    if (this.activeWorkflowId && this.activeWorkflowId !== workflowId) {
      this.pauseWorkflow(this.activeWorkflowId);
    }

    workflow.status = WORKFLOW_STATUS.IN_PROGRESS;
    this.activeWorkflowId = workflowId;

    // Log resume to analytics
    this._logAnalytics('workflow_resumed', {
      workflowId,
      currentStepId: this.getCurrentStep()?.id,
    });

    // Save state
    if (this.autoSave) {
      this.saveState();
    }

    return this.getCurrentStep();
  }

  /**
   * Get the current step for the active workflow
   * @param {String} workflowId Optional workflow ID
   * @returns {Object} The current step
   */
  getCurrentStep(workflowId = this.activeWorkflowId) {
    if (!workflowId) {
      return null;
    }

    const workflow = this.workflows[workflowId];

    if (!workflow) {
      return null;
    }

    return workflow.steps[workflow.currentStepIndex];
  }

  /**
   * Get workflow progress information
   * @param {String} workflowId Optional workflow ID
   * @returns {Object} Progress information
   */
  getProgress(workflowId = this.activeWorkflowId) {
    if (!workflowId) {
      return { percentage: 0, current: 0, total: 0 };
    }

    const workflow = this.workflows[workflowId];

    if (!workflow) {
      return { percentage: 0, current: 0, total: 0 };
    }

    const current = workflow.currentStepIndex + 1;
    const total = workflow.steps.length;
    const percentage = Math.round((current / total) * 100);

    return {
      percentage,
      current,
      total,
      status: workflow.status,
    };
  }

  /**
   * Get data collected in the workflow
   * @param {String} workflowId Optional workflow ID
   * @returns {Object} Collected workflow data
   */
  getWorkflowData(workflowId = this.activeWorkflowId) {
    if (!workflowId) {
      return {};
    }

    const workflow = this.workflows[workflowId];

    if (!workflow) {
      return {};
    }

    return { ...workflow.data };
  }

  /**
   * Save workflow state to storage
   */
  saveState() {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    // Prepare simplified workflow state for storage
    const workflowState = Object.values(this.workflows)
      .filter((workflow) => workflow.status !== WORKFLOW_STATUS.NOT_STARTED)
      .map((workflow) => ({
        id: workflow.id,
        status: workflow.status,
        currentStepIndex: workflow.currentStepIndex,
        data: workflow.data,
        startTime: workflow.startTime,
        endTime: workflow.endTime,
      }));

    try {
      localStorage.setItem(
        this.persistenceKey,
        JSON.stringify({
          activeWorkflowId: this.activeWorkflowId,
          workflows: workflowState,
        })
      );
    } catch (error) {
      console.error('Failed to save workflow state:', error);
    }
  }

  /**
   * Load workflow state from storage
   */
  loadSavedState() {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }

    try {
      const savedState = localStorage.getItem(this.persistenceKey);

      if (!savedState) {
        return;
      }

      const { activeWorkflowId, workflows } = JSON.parse(savedState);

      // Restore workflow states
      workflows.forEach((savedWorkflow) => {
        // Skip if workflow definition doesn't exist
        if (!this.workflows[savedWorkflow.id]) {
          return;
        }

        // Restore workflow state
        this.workflows[savedWorkflow.id] = {
          ...this.workflows[savedWorkflow.id],
          status: savedWorkflow.status,
          currentStepIndex: savedWorkflow.currentStepIndex,
          data: savedWorkflow.data,
          startTime: savedWorkflow.startTime,
          endTime: savedWorkflow.endTime,
        };
      });

      // Restore active workflow
      if (activeWorkflowId && this.workflows[activeWorkflowId]) {
        this.activeWorkflowId = activeWorkflowId;
      }
    } catch (error) {
      console.error('Failed to load workflow state:', error);
    }
  }

  /**
   * Clear all workflow state and definitions
   */
  reset() {
    this.workflows = {};
    this.activeWorkflowId = null;

    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(this.persistenceKey);
    }
  }

  /**
   * Log analytics data if analytics callback is defined
   * @param {String} event Event name
   * @param {Object} data Event data
   * @private
   */
  _logAnalytics(event, data) {
    if (typeof this.analyticsCallback === 'function') {
      this.analyticsCallback(event, data);
    }
  }
}

export { WorkflowOptimizer, WORKFLOW_STATUS, STEP_TYPES };
export default WorkflowOptimizer;
