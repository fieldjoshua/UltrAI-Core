import React from 'react';
import { render, screen } from '../../../test/test-utils';
import userEvent from '@testing-library/user-event';
import WizardStep from '../../../components/wizard/WizardStep';

function Harness({ step, stepIndex }: { step: any; stepIndex: number }) {
  const [selections, setSelections] = React.useState<Record<number, any>>({});
  const [inputs, setInputs] = React.useState<Record<string, string>>({});
  return (
    <WizardStep
      step={step}
      stepIndex={stepIndex}
      selections={selections}
      onSelectionsChange={(i, v) =>
        setSelections(prev => ({ ...prev, [i]: v }))
      }
      inputs={inputs}
      onInputChange={(k, v) => setInputs(prev => ({ ...prev, [k]: v }))}
    />
  );
}

describe('WizardStep', () => {
  it('renders intro step', () => {
    render(
      <WizardStep
        step={{ title: 'Welcome', type: 'intro' }}
        stepIndex={0}
        selections={{}}
        onSelectionsChange={() => {}}
        inputs={{}}
        onInputChange={() => {}}
      />
    );
    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText(/welcome to the wizard/i)).toBeInTheDocument();
  });

  it('renders checkbox step and toggles selections', async () => {
    const user = userEvent.setup();
    const changes: any[] = [];
    render(
      <Harness
        step={{
          title: 'Select Options',
          type: 'checkbox',
          options: [
            { label: 'A', value: 'a' },
            { label: 'B', value: 'b' },
          ],
        }}
        stepIndex={1}
      />
    );

    await user.click(screen.getByLabelText('A'));
    await user.click(screen.getByLabelText('B'));
    // Both checkboxes should be checked now
    expect(
      (screen.getByLabelText('A') as HTMLInputElement).checked
    ).toBe(true);
    expect(
      (screen.getByLabelText('B') as HTMLInputElement).checked
    ).toBe(true);
  });

  it('renders textarea step and updates input', async () => {
    const user = userEvent.setup();
    render(<Harness step={{ title: 'Describe', type: 'textarea' }} stepIndex={2} />);

    await user.type(screen.getByLabelText('Describe'), 'hello');
    expect(
      (screen.getByLabelText('Describe') as HTMLTextAreaElement).value
    ).toBe('hello');
  });

  it('renders groupbox step and selects option', async () => {
    const user = userEvent.setup();
    render(
      <Harness
        step={{
          title: 'Pick One',
          type: 'groupbox',
          options: [
            { label: 'One', value: '1' },
            { label: 'Two', value: '2' },
          ],
        }}
        stepIndex={3}
      />
    );

    await user.click(screen.getByRole('button', { name: 'One' }));
    expect(
      screen.getByRole('button', { name: 'One' }).getAttribute('aria-pressed')
    ).toBe('true');
  });
});


