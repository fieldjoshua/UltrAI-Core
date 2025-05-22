/**
 * Workflow Module
 *
 * Provides components and utilities for simplifying complex workflows
 * and guiding users through multi-step processes.
 */

import WorkflowOptimizer, {
  WORKFLOW_STATUS,
  STEP_TYPES,
} from './WorkflowOptimizer';
import {
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
} from './WorkflowUI';

// Export all components and utilities
export {
  WorkflowOptimizer,
  WORKFLOW_STATUS,
  STEP_TYPES,
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
};

// Default export for easier imports
export default {
  WorkflowOptimizer,
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
};
