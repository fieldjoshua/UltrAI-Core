import React from 'react';
import { render, screen } from '../../../test/test-utils';
import userEvent from '@testing-library/user-event';
import StepNavigation from '../../../components/wizard/StepNavigation';

describe('StepNavigation', () => {
  it('renders buttons 1 through 5 and excludes step 0', () => {
    const steps = [
      { title: 'Intro' },
      { title: 'One' },
      { title: 'Two' },
      { title: 'Three' },
      { title: 'Four' },
      { title: 'Five' },
      { title: 'Six' },
    ];

    render(
      <StepNavigation steps={steps} currentStep={2} onStepClick={() => {}} />
    );

    expect(screen.queryByRole('button', { name: /go to intro/i })).not.toBeInTheDocument();
    // Visible steps should be 1..5 and have distinct aria-labels
    expect(screen.getByRole('button', { name: 'Go to One' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go to Two' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go to Three' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go to Four' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Go to Five' })).toBeInTheDocument();
  });

  it('calls onStepClick with correct index', async () => {
    const user = userEvent.setup();
    const steps = Array.from({ length: 6 }, (_, i) => ({ title: `Step ${i}` }));
    const clicks: number[] = [];
    render(
      <StepNavigation
        steps={steps}
        currentStep={1}
        onStepClick={idx => clicks.push(idx)}
      />
    );

    await user.click(screen.getByText('3'));
    expect(clicks).toContain(3);
  });
});


