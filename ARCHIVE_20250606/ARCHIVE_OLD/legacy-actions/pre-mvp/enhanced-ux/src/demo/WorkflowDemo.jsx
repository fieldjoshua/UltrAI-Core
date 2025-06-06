import React, { useState } from 'react';
import {
  WorkflowProvider,
  useWorkflow,
  WorkflowNavigator,
  WorkflowStep,
  WorkflowProgress,
  STEP_TYPES,
} from '../workflow';

/**
 * Workflow Optimization Demo
 *
 * Demonstrates the workflow optimization capabilities with a multi-step form.
 */
const WorkflowDemo = () => {
  // Define sample workflows
  const sampleWorkflows = {
    'user-onboarding': {
      title: 'User Onboarding',
      description: 'A simplified user onboarding workflow',
      steps: [
        {
          id: 'welcome',
          type: STEP_TYPES.INFORMATION,
          title: 'Welcome',
          description: 'Welcome to the UltraAI system!',
          content: 'This quick onboarding will help you get started.',
        },
        {
          id: 'profile',
          type: STEP_TYPES.INPUT,
          title: 'Profile Information',
          description: 'Tell us about yourself',
          prevStepId: 'welcome',
          fields: [
            { id: 'name', label: 'Your Name', type: 'text', required: true },
            { id: 'role', label: 'Your Role', type: 'text' },
          ],
        },
        {
          id: 'preferences',
          type: STEP_TYPES.SELECTION,
          title: 'System Preferences',
          description: 'Customize your experience',
          prevStepId: 'profile',
          options: [
            {
              id: 'theme',
              label: 'Theme',
              choices: ['Light', 'Dark', 'Cyberpunk'],
            },
            {
              id: 'notifications',
              label: 'Notifications',
              choices: ['All', 'Important Only', 'None'],
            },
          ],
        },
        {
          id: 'confirmation',
          type: STEP_TYPES.CONFIRMATION,
          title: 'Confirm Settings',
          description: 'Please review your settings',
          prevStepId: 'preferences',
        },
        {
          id: 'complete',
          type: STEP_TYPES.INFORMATION,
          title: 'Setup Complete',
          description: "You're all set!",
          prevStepId: 'confirmation',
          content:
            "Your profile has been set up and you're ready to use the system.",
        },
      ],
    },
    'data-import': {
      title: 'Data Import',
      description: 'Import data into the system',
      steps: [
        {
          id: 'select-source',
          type: STEP_TYPES.SELECTION,
          title: 'Select Data Source',
          description: 'Choose where to import data from',
          options: [
            {
              id: 'source',
              label: 'Data Source',
              choices: ['Local File', 'Cloud Storage', 'API'],
            },
          ],
        },
        {
          id: 'configure',
          type: STEP_TYPES.INPUT,
          title: 'Configure Import',
          description: 'Configure import settings',
          prevStepId: 'select-source',
          fields: [
            { id: 'name', label: 'Import Name', type: 'text', required: true },
            {
              id: 'format',
              label: 'Data Format',
              type: 'select',
              options: ['CSV', 'JSON', 'XML'],
            },
          ],
        },
        {
          id: 'map-fields',
          type: STEP_TYPES.ACTION,
          title: 'Map Fields',
          description: 'Map data fields to system fields',
          prevStepId: 'configure',
        },
        {
          id: 'review',
          type: STEP_TYPES.CONFIRMATION,
          title: 'Review Import',
          description: 'Review the import configuration',
          prevStepId: 'map-fields',
        },
        {
          id: 'import',
          type: STEP_TYPES.PROCESSING,
          title: 'Importing Data',
          description: 'Your data is being imported',
          prevStepId: 'review',
        },
        {
          id: 'complete',
          type: STEP_TYPES.INFORMATION,
          title: 'Import Complete',
          description: 'Your data has been imported',
          prevStepId: 'import',
          content: 'The data import has completed successfully.',
        },
      ],
    },
  };

  return (
    <WorkflowProvider
      initialWorkflows={sampleWorkflows}
      persistenceKey="demo_workflows"
      onWorkflowComplete={(data, workflow) => {
        console.log('Workflow completed:', workflow.id, data);
      }}
    >
      <WorkflowDemoContent />
    </WorkflowProvider>
  );
};

// Component that uses the workflow context
const WorkflowDemoContent = () => {
  const [formValues, setFormValues] = useState({});
  const { activeWorkflowId, currentStep, workflowProgress, startWorkflow } =
    useWorkflow();

  // Main container style
  const containerStyle = {
    fontFamily: 'Arial, sans-serif',
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
  };

  // Card style
  const cardStyle = {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '5px',
    marginBottom: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  };

  // Button style
  const buttonStyle = {
    backgroundColor: '#4a90e2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '10px 15px',
    cursor: 'pointer',
    fontSize: '14px',
    margin: '5px',
  };

  // Handle form change
  const handleInputChange = (e) => {
    setFormValues({
      ...formValues,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div style={containerStyle}>
      <h1 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
        Workflow Optimization Demo
      </h1>

      {/* Workflow selection */}
      {!activeWorkflowId && (
        <div style={cardStyle}>
          <h2>Select a Workflow</h2>
          <p>
            Choose a workflow to see how the workflow optimization system
            streamlines complex processes:
          </p>

          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button
              style={buttonStyle}
              onClick={() => startWorkflow('user-onboarding')}
            >
              User Onboarding
            </button>
            <button
              style={buttonStyle}
              onClick={() => startWorkflow('data-import')}
            >
              Data Import
            </button>
          </div>
        </div>
      )}

      {/* Active workflow */}
      {activeWorkflowId && (
        <div style={cardStyle}>
          <WorkflowProgress
            showTitle={true}
            showPercentage={true}
            showStepCount={true}
          />

          {currentStep && (
            <div style={{ margin: '20px 0' }}>
              <h2>{currentStep.title}</h2>
              <p>{currentStep.description}</p>

              {/* Step content based on step type */}
              <WorkflowStep stepId={currentStep.id}>
                {({ step, onNext }) => (
                  <div>
                    {step.type === STEP_TYPES.INFORMATION && (
                      <div>
                        <p>{step.content}</p>
                      </div>
                    )}

                    {step.type === STEP_TYPES.INPUT && step.fields && (
                      <div style={{ marginTop: '20px' }}>
                        {step.fields.map((field) => (
                          <div key={field.id} style={{ marginBottom: '15px' }}>
                            <label
                              style={{
                                display: 'block',
                                marginBottom: '5px',
                                fontWeight: 'bold',
                              }}
                            >
                              {field.label}
                              {field.required && (
                                <span style={{ color: 'red' }}> *</span>
                              )}
                            </label>
                            <input
                              type={field.type || 'text'}
                              name={field.id}
                              value={formValues[field.id] || ''}
                              onChange={handleInputChange}
                              style={{
                                width: '100%',
                                padding: '8px',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                              }}
                              required={field.required}
                            />
                          </div>
                        ))}

                        <button
                          style={buttonStyle}
                          onClick={() => onNext(formValues)}
                        >
                          Continue
                        </button>
                      </div>
                    )}

                    {step.type === STEP_TYPES.SELECTION && step.options && (
                      <div style={{ marginTop: '20px' }}>
                        {step.options.map((option) => (
                          <div key={option.id} style={{ marginBottom: '15px' }}>
                            <label
                              style={{
                                display: 'block',
                                marginBottom: '5px',
                                fontWeight: 'bold',
                              }}
                            >
                              {option.label}
                            </label>
                            <select
                              name={option.id}
                              value={formValues[option.id] || ''}
                              onChange={handleInputChange}
                              style={{
                                width: '100%',
                                padding: '8px',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                              }}
                            >
                              <option value="">Select...</option>
                              {option.choices.map((choice) => (
                                <option key={choice} value={choice}>
                                  {choice}
                                </option>
                              ))}
                            </select>
                          </div>
                        ))}

                        <button
                          style={buttonStyle}
                          onClick={() => onNext(formValues)}
                        >
                          Continue
                        </button>
                      </div>
                    )}

                    {step.type === STEP_TYPES.CONFIRMATION && (
                      <div style={{ marginTop: '20px' }}>
                        <h3>Please confirm your information:</h3>
                        <div
                          style={{
                            backgroundColor: '#f5f5f5',
                            padding: '15px',
                            borderRadius: '4px',
                            marginBottom: '20px',
                          }}
                        >
                          {Object.entries(formValues).map(([key, value]) => (
                            <div key={key} style={{ margin: '5px 0' }}>
                              <strong>{key}:</strong> {value}
                            </div>
                          ))}
                        </div>

                        <button
                          style={buttonStyle}
                          onClick={() => onNext({ confirmed: true })}
                        >
                          Confirm
                        </button>
                      </div>
                    )}

                    {step.type === STEP_TYPES.PROCESSING && (
                      <div style={{ marginTop: '20px', textAlign: 'center' }}>
                        <div
                          style={{
                            display: 'inline-block',
                            width: '50px',
                            height: '50px',
                            border: '5px solid #f3f3f3',
                            borderTop: '5px solid #3498db',
                            borderRadius: '50%',
                            animation: 'spin 2s linear infinite',
                            marginBottom: '20px',
                          }}
                        />
                        <style>
                          {`
                            @keyframes spin {
                              0% { transform: rotate(0deg); }
                              100% { transform: rotate(360deg); }
                            }
                          `}
                        </style>
                        <p>Processing your request...</p>

                        {/* Auto-advance after delay for demo purposes */}
                        {setTimeout(() => onNext({ processed: true }), 2000)}
                      </div>
                    )}

                    {/* Default continue button for information steps */}
                    {step.type === STEP_TYPES.INFORMATION &&
                      step.id !== 'welcome' &&
                      step.id !== 'complete' && (
                        <button style={buttonStyle} onClick={() => onNext({})}>
                          Continue
                        </button>
                      )}

                    {/* Special handling for welcome and complete steps */}
                    {step.id === 'welcome' && (
                      <button style={buttonStyle} onClick={() => onNext({})}>
                        Get Started
                      </button>
                    )}

                    {step.id === 'complete' && (
                      <button style={buttonStyle} onClick={() => onNext({})}>
                        Finish
                      </button>
                    )}
                  </div>
                )}
              </WorkflowStep>
            </div>
          )}

          {/* Navigation controls */}
          <WorkflowNavigator
            allowBack={true}
            allowSkip={false}
            nextButtonLabel="Continue"
            completeButtonLabel="Finish"
          />
        </div>
      )}

      {/* Features list */}
      <div style={cardStyle}>
        <h2>Key Workflow Features</h2>
        <ul style={{ lineHeight: '1.6' }}>
          <li>
            <strong>Step-by-Step Guidance:</strong> Clear navigation through
            complex processes
          </li>
          <li>
            <strong>Progress Tracking:</strong> Visual indicators of completion
            progress
          </li>
          <li>
            <strong>State Persistence:</strong> Workflows can be paused and
            resumed
          </li>
          <li>
            <strong>Flexible Step Types:</strong> Information, input, selection,
            confirmation, and processing steps
          </li>
          <li>
            <strong>Data Collection:</strong> Gather and validate user input at
            each step
          </li>
        </ul>
      </div>
    </div>
  );
};

export default WorkflowDemo;
