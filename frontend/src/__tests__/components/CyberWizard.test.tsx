import React from 'react';
import { render, screen, waitFor } from '../../test/test-utils';
import CyberWizard from '../../components/CyberWizard';

// @ts-ignore
const jest = globalThis.jest;

// Mock the fetch API
global.fetch = jest.fn();

describe('CyberWizard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock wizard steps response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [
        {
          title: "0. Welcome",
          color: "mint",
          type: "intro",
          narrative: "Welcome to UltrAI"
        }
      ],
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
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
      expect(global.fetch).toHaveBeenCalledWith('/wizard_steps.json', { cache: 'no-store' });
    });
  });
});