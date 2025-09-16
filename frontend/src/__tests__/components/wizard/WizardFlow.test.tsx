import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock function for testing
let mockOnComplete: any;

// Simplified wizard component for testing core flow
const SimpleWizard: React.FC = () => {
  const [step, setStep] = React.useState(0);
  const [selections, setSelections] = React.useState<any>({});

  const steps = [
    { title: 'Welcome', type: 'intro' },
    { title: 'Select Goals', type: 'checkbox' },
    { title: 'Enter Query', type: 'textarea' },
    { title: 'Review', type: 'review' },
  ];

  const currentStep = steps[step];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      mockOnComplete(selections);
    }
  };

  const handlePrev = () => {
    if (step > 0) setStep(step - 1);
  };

  return (
    <div role="main" aria-label="Wizard">
      <h1>{currentStep.title}</h1>

      <div role="navigation" aria-label="Wizard steps">
        {steps.map((s, i) => (
          <button
            key={i}
            onClick={() => setStep(i)}
            aria-current={i === step ? 'step' : undefined}
            aria-label={`Go to ${s.title}`}
          >
            {i + 1}. {s.title}
          </button>
        ))}
      </div>

      {currentStep.type === 'intro' && (
        <div>
          <p>Welcome to the wizard</p>
        </div>
      )}

      {currentStep.type === 'checkbox' && (
        <div>
          <label>
            <input
              type="checkbox"
              onChange={e =>
                setSelections({
                  ...selections,
                  goal1: e.target.checked,
                })
              }
            />
            Goal 1
          </label>
        </div>
      )}

      {currentStep.type === 'textarea' && (
        <div>
          <label htmlFor="query">Enter your query:</label>
          <textarea
            id="query"
            onChange={e =>
              setSelections({
                ...selections,
                query: e.target.value,
              })
            }
          />
        </div>
      )}

      {currentStep.type === 'review' && (
        <div>
          <h2>Review your selections</h2>
          <pre>{JSON.stringify(selections, null, 2)}</pre>
        </div>
      )}

      <div>
        <button onClick={handlePrev} disabled={step === 0}>
          Previous
        </button>
        <button onClick={handleNext}>
          {step === steps.length - 1 ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  );
};

describe('Wizard Flow', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    mockOnComplete = (selections: any) => {
      // Store the selections for verification
      mockOnComplete.lastCall = selections;
    };
    mockOnComplete.calls = [];
    mockOnComplete.lastCall = null;
  });

  it('should render the welcome step initially', () => {
    render(<SimpleWizard />);
    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText('Welcome to the wizard')).toBeInTheDocument();
  });

  it('should navigate between steps', async () => {
    render(<SimpleWizard />);

    // Click next to go to step 2
    await user.click(screen.getByText('Next'));
    expect(screen.getByText('Select Goals')).toBeInTheDocument();

    // Click previous to go back
    await user.click(screen.getByText('Previous'));
    expect(screen.getByText('Welcome')).toBeInTheDocument();
  });

  it('should allow direct navigation via step buttons', async () => {
    render(<SimpleWizard />);

    // Click on step 3 directly
    await user.click(screen.getByLabelText('Go to Enter Query'));
    expect(screen.getByLabelText('Enter your query:')).toBeInTheDocument();
  });

  it('should collect user selections', async () => {
    render(<SimpleWizard />);

    // Navigate to goals
    await user.click(screen.getByText('Next'));

    // Select a goal
    await user.click(screen.getByLabelText('Goal 1'));

    // Navigate to query
    await user.click(screen.getByText('Next'));

    // Enter a query
    await user.type(screen.getByLabelText('Enter your query:'), 'Test query');

    // Navigate to review
    await user.click(screen.getByText('Next'));

    // Should see selections
    expect(screen.getByText(/goal1.*true/)).toBeInTheDocument();
    expect(screen.getByText(/query.*Test query/)).toBeInTheDocument();
  });

  it('should complete wizard with collected data', async () => {
    render(<SimpleWizard />);

    // Quick navigation through wizard
    await user.click(screen.getByText('Next')); // to goals
    await user.click(screen.getByLabelText('Goal 1'));
    await user.click(screen.getByText('Next')); // to query
    await user.type(screen.getByLabelText('Enter your query:'), 'Test');
    await user.click(screen.getByText('Next')); // to review

    // Complete wizard
    await user.click(screen.getByText('Complete'));

    expect(mockOnComplete.lastCall).toEqual({
      goal1: true,
      query: 'Test',
    });
  });

  it('should disable previous button on first step', () => {
    render(<SimpleWizard />);
    expect(screen.getByText('Previous')).toBeDisabled();
  });

  it('should have proper ARIA attributes for accessibility', () => {
    render(<SimpleWizard />);

    // Check main region
    expect(screen.getByRole('main')).toHaveAttribute('aria-label', 'Wizard');

    // Check navigation
    expect(screen.getByRole('navigation')).toHaveAttribute(
      'aria-label',
      'Wizard steps'
    );

    // Check current step
    const firstStepButton = screen.getByLabelText('Go to Welcome');
    expect(firstStepButton).toHaveAttribute('aria-current', 'step');
  });
});
