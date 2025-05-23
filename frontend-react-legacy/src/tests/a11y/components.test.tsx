import React from 'react';
import { render } from '@testing-library/react';
import { axe } from './setup';
import { Button } from '../../components/Button';
import { Link } from '../../components/Link';
import { Slider } from '../../components/Slider';

describe('Accessibility tests', () => {
  it('Button component should not have accessibility violations', async () => {
    const { container } = render(
      <Button onClick={() => {}} disabled={false}>
        Click me
      </Button>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Link component should not have accessibility violations', async () => {
    const { container } = render(
      <Link href="#" external={false} disabled={false}>
        Visit Link
      </Link>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Slider component should not have accessibility violations', async () => {
    const { container } = render(
      <Slider
        id="test-slider"
        label="Test slider"
        value={50}
        onChange={() => {}}
      />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
