import React from 'react';
import { render, screen, waitFor } from '../../test/test-utils';
import CyberWizard from '../../components/CyberWizard';

// @ts-ignore
const jest = globalThis.jest;

// Use a fetch spy so MSW can still intercept
let fetchSpy: jest.SpyInstance;

describe('CyberWizard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fetchSpy = jest.spyOn(globalThis as any, 'fetch');
  });

  afterEach(() => {
    jest.restoreAllMocks();
    fetchSpy?.mockRestore();
  });

  it('should render the welcome screen', async () => {
    render(<CyberWizard />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText(/Welcome to the future/i)).toBeInTheDocument();
    });
  });

  it('should have the Enter UltrAI button', async () => {
    render(<CyberWizard />);

    await waitFor(() => {
      const enterButton = screen.getByRole('button', { name: /Enter UltrAI/i });
      expect(enterButton).toBeInTheDocument();
    });
  });

  it('should fetch wizard steps on mount', async () => {
    render(<CyberWizard />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/wizard_steps.json', {
        cache: 'no-store',
      });
    });
  });
});
