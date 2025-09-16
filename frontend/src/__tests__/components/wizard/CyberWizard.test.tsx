import React from 'react';
import { jest } from '@jest/globals';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  render,
  mockModel,
  mockOrchestratorResult,
} from '../../../test/test-utils';
import CyberWizard from '../../../components/wizard/CyberWizard';
import * as orchestratorApi from '../../../api/orchestrator';
import { useAuthStore } from '../../../stores/authStore';

// Mock dependencies
// Use spies so MSW can serve available models; we control orchestration only
// Remove ESM export spying; rely on MSW handlers instead
jest.mock('../../../stores/authStore', () => ({
  __esModule: true,
  useAuthStore: jest.fn(() => ({
    isAuthenticated: true,
    user: { id: '123', email: 'test@example.com' },
  })),
}));

// Allow per-test control over orchestration without real network
jest.mock('../../../api/orchestrator', () => ({
  __esModule: true,
  ...jest.requireActual('../../../api/orchestrator'),
  processWithFeatherOrchestration: jest.fn(),
}));

// Spy on fetch for wizard steps
let fetchSpy: jest.SpyInstance;

const mockWizardSteps = [
  {
    title: '0. Welcome',
    color: 'mint',
    type: 'intro',
    narrative: 'Welcome to UltrAI',
  },
  {
    title: '1. Select your goals',
    color: 'mint',
    type: 'checkbox',
    options: [
      { label: 'Deep analysis', cost: 0.08, icon: '🔍' },
      { label: 'Creative exploration', cost: 0.1, icon: '🎨' },
      { label: 'Problem solving', cost: 0.12, icon: '🧩' },
    ],
  },
  {
    title: '2. What do you need?',
    color: 'blue',
    type: 'textarea',
    narrative: 'Tell us what you need analyzed',
  },
  {
    title: '3. Model selection',
    color: 'purple',
    type: 'checkbox',
    options: [],
  },
  {
    title: '4. Add-ons & formatting',
    color: 'pink',
    type: 'checkbox',
    options: [
      { label: 'Citations', cost: 0.05, icon: '📚' },
      { label: 'Summary', cost: 0.03, icon: '📝' },
    ],
  },
];

const mockAvailableModels = [
  mockModel({ name: 'gpt-4', cost_per_1k_tokens: 0.03 }),
  mockModel({ name: 'claude-3-opus', cost_per_1k_tokens: 0.04 }),
  mockModel({ name: 'gemini-1.5-pro', cost_per_1k_tokens: 0.02 }),
];

describe('CyberWizard', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();

    // Ensure fetch is spy-able from whatwg-fetch polyfill
    const originalFetch = (globalThis as any).fetch;
    fetchSpy = jest.spyOn(globalThis as any, 'fetch');
    // Route wizard steps to mock; delegate others to original or MSW
    fetchSpy.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === 'string' ? input : (input as Request).url;
      if (typeof url === 'string' && url.includes('/wizard_steps.json')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockWizardSteps,
        } as any);
      }
      return (originalFetch as any)(input as any, init as any);
    });

    // Spy on orchestration (models come from MSW)
    // no-op; keep defaults

    // Auth store mocked via jest factory above
  });

  afterEach(() => {
    jest.restoreAllMocks();
    // no-op
    fetchSpy?.mockRestore();
  });

  describe('Initial Render', () => {
    it('should render the welcome screen on initial load', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(screen.getByText(/Intelligence Multiplication Platform/i)).toBeInTheDocument();
      });

      expect(
        screen.getByRole('button', { name: /Enter UltrAI/i })
      ).toBeInTheDocument();
    });

    it('should load wizard steps from JSON', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/wizard_steps.json', {
          cache: 'no-store',
        });
      });
    });

    it('should show loading state while fetching steps', () => {
      fetchSpy.mockImplementationOnce(
        () => new Promise(() => {})
      );

      render(<CyberWizard />);

      expect(screen.getByText(/Loading UltrAI.../i)).toBeInTheDocument();
    });
  });

  describe('Step Navigation', () => {
    it('should navigate to step 1 when clicking Enter UltrAI', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Wait for navigation to complete and step content to appear
      await waitFor(() => {
        expect(screen.getByText(/Select your goals/i)).toBeInTheDocument();
      });
    });

    it('should allow navigation between steps using step markers', async () => {
      render(<CyberWizard />);

      // Start from step 1
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Click on step 2 marker
      const step2Button = screen.getByRole('button', { name: /Go to step 2/i });
      await user.click(step2Button);

      expect(screen.getByText(/What do you need?/i)).toBeInTheDocument();
    });

    it('should support keyboard navigation with arrow keys', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Press Enter to go to step 1
      await user.keyboard('{Enter}');
      await waitFor(() => {
        expect(screen.getByText(/Select your goals/i)).toBeInTheDocument();
      });

      // Press right arrow to go to step 2
      await user.keyboard('{ArrowRight}');
      expect(screen.getByText(/What do you need?/i)).toBeInTheDocument();

      // Press left arrow to go back to step 1
      await user.keyboard('{ArrowLeft}');
      await waitFor(() => {
        expect(screen.getByText(/Select your goals/i)).toBeInTheDocument();
      });
    });
  });

  describe('Goal Selection (Step 1)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
    });

    it('should display all goal options', () => {
      expect(screen.getByText(/Deep analysis/i)).toBeInTheDocument();
      expect(screen.getByText(/Creative exploration/i)).toBeInTheDocument();
      expect(screen.getByText(/Problem solving/i)).toBeInTheDocument();
    });

    it('should update receipt when selecting goals', async () => {
      const deepAnalysis = await screen.findByText(/Deep analysis/i);
      await user.click(deepAnalysis);

      // Check receipt shows selected item
      expect(screen.getByText(/Deep analysis.*\$0\.08/)).toBeInTheDocument();
      expect(screen.getByText(/Total: \$0\.08/)).toBeInTheDocument();
    });

    it('should allow multiple goal selections', async () => {
      await user.click(await screen.findByText(/Deep analysis/i));
      await user.click(screen.getByText(/Creative exploration/i));

      expect(screen.getByText(/Total: \$0\.18/)).toBeInTheDocument();
    });
  });

  describe('Query Input (Step 2)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Navigate to step 2
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      await user.click(screen.getByRole('button', { name: /Go to step 2/i })); // Step 1 → 2
      await user.click(screen.getByRole('button', { name: /Go to step 3/i })); // Step 2 → 3
    });

    it('should display query textarea', () => {
      expect(
        screen.getByRole('textbox', { name: /What do you need/i })
      ).toBeInTheDocument();
    });

    it('should show character count when typing', async () => {
      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      await user.type(textarea, 'Test query');

      expect(screen.getByText(/10 \/ 1000/)).toBeInTheDocument();
    });

    it('should show optimization button when query is entered', async () => {
      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      await user.type(textarea, 'Analyze market trends');

      expect(
        screen.getByRole('button', { name: /optimize my query/i })
      ).toBeInTheDocument();
    });

    it('should optimize query when clicking optimization button', async () => {
      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      await user.type(textarea, 'Analyze market trends');
      await user.click(
        screen.getByRole('button', { name: /optimize my query/i })
      );

      // Should add context and suggestions
      expect(textarea).toHaveValue(
        expect.stringContaining('specific, detailed analysis')
      );
    });
  });

  describe('Model Selection (Step 3)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Navigate to step 3
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      await user.click(screen.getByRole('button', { name: /Go to step 3/i }));
    });

    it('should display model selection options', async () => {
      await waitFor(() => {
        expect(screen.getByText(/Premium Query/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Quick Query/i)).toBeInTheDocument();
      expect(screen.getByText(/Budget Query/i)).toBeInTheDocument();
    });

    it('should auto-select models when choosing Premium Query', async () => {
      await user.click(screen.getByText(/Premium Query/i).closest('div')!);

      await waitFor(() => {
        expect(
          screen.getByText(
            /Premium Query: gpt-4, claude-3-opus, gemini-1.5-pro/i
          )
        ).toBeInTheDocument();
      });
    });

    it('should show manual model selection when requested', async () => {
      await user.click(
        screen.getByRole('button', { name: /Show Available Models/i })
      );

      await waitFor(() => {
        expect(screen.getByText(/Select Models/i)).toBeInTheDocument();
      });

      expect(
        screen.getByRole('checkbox', { name: /gpt-4/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('checkbox', { name: /claude-3-opus/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('checkbox', { name: /gemini-1.5-pro/i })
      ).toBeInTheDocument();
    });
  });

  describe('Add-ons Selection (Step 4)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Navigate to step 4
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Select a goal
      const deepGoal1 = await screen.findByText(/Deep analysis/i);
      await user.click(deepGoal1);
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));

      // Enter query
      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      await user.type(textarea, 'Test query');
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));

      // Select models
      await user.click(screen.getByText(/Premium Query/i).closest('div')!);
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));
    });

    it('should display add-on options', () => {
      expect(screen.getByText(/Citations.*\$0\.05/)).toBeInTheDocument();
      expect(screen.getByText(/Summary.*\$0\.03/)).toBeInTheDocument();
    });

    it('should enable Initialize button after submitting add-ons', async () => {
      await user.click(screen.getByRole('button', { name: /Submit Add-ons/i }));

      expect(
        screen.getByRole('button', { name: /Initialize UltrAI/i })
      ).toBeInTheDocument();
    });

    it('should require at least 2 models before initialization', async () => {
      // Go back and deselect models
      await user.click(screen.getByRole('button', { name: /Go to step 3/i }));
      await user.click(
        screen.getByRole('button', { name: /Show Available Models/i })
      );

      // Select only one model
      await user.click(screen.getByRole('checkbox', { name: /gpt-4/i }));

      // Go forward and submit add-ons
      await user.click(screen.getByRole('button', { name: /Submit/i }));
      await user.click(screen.getByRole('button', { name: /Submit Add-ons/i }));

      expect(screen.getByText(/Select at least 2 models/i)).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /Select at least 2 models/i })
      ).toBeDisabled();
    });
  });

  describe('Orchestration Process', () => {
    beforeEach(async () => {
      render(<CyberWizard />);

      // Complete the wizard flow
      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      const deepGoal2 = await screen.findByText(/Deep analysis/i);
      await user.click(deepGoal2);
      await user.click(screen.getByRole('button', { name: /Go to step 2/i }));

      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      await user.type(textarea, 'Test query for orchestration');
      await user.click(screen.getByRole('button', { name: /Go to step 3/i }));

      await user.click(screen.getByText(/Premium Query/i).closest('div')!);
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));

      await user.click(screen.getByRole('button', { name: /Submit Add-ons/i }));
    });

    it('should start orchestration when Initialize button is clicked', async () => {
      const mockResult = mockOrchestratorResult();
      (
        orchestratorApi.processWithFeatherOrchestration as jest.Mock
      ).mockResolvedValueOnce(mockResult);

      await user.click(
        screen.getByRole('button', { name: /Initialize UltrAI/i })
      );

      expect(screen.getByText(/ULTRA SYNTHESIS™/i)).toBeInTheDocument();
      expect(screen.getByText(/PROCESSING STATUS/i)).toBeInTheDocument();

      await waitFor(() => {
        expect(
          orchestratorApi.processWithFeatherOrchestration
        ).toHaveBeenCalledWith({
          prompt: 'Test query for orchestration',
          models: expect.arrayContaining([
            'gpt-4',
            'claude-3-opus',
            'gemini-1.5-pro',
          ]),
          pattern: 'comparative',
          ultraModel: null,
          outputFormat: 'plain',
        });
      });
    });

    it('should display results after successful orchestration', async () => {
      const mockResult = mockOrchestratorResult({
        ultra_response:
          'This is the synthesized response from multiple models.',
      });
      (
        orchestratorApi.processWithFeatherOrchestration as jest.Mock
      ).mockResolvedValueOnce(mockResult);

      await user.click(
        screen.getByRole('button', { name: /Initialize UltrAI/i })
      );

      await waitFor(() => {
        expect(screen.getByText(/View Results/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Analysis Complete/i)).toBeInTheDocument();
    });

    it('should handle orchestration errors gracefully', async () => {
      (
        orchestratorApi.processWithFeatherOrchestration as jest.Mock
      ).mockRejectedValueOnce(new Error('Network error'));

      await user.click(
        screen.getByRole('button', { name: /Initialize UltrAI/i })
      );

      await waitFor(() => {
        expect(screen.getByText(/Error Occurred/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });

  describe('Demo Mode', () => {
    beforeEach(() => {
      // Set demo mode environment
      (global as any).import.meta.env.VITE_API_MODE = 'mock';
      (global as any).import.meta.env.VITE_DEMO_MODE = 'true';

      // Mock demo data fetch
      (global.fetch as jest.Mock).mockImplementation(url => {
        if (url === '/wizard_steps.json') {
          return Promise.resolve({
            ok: true,
            json: async () => mockWizardSteps,
          });
        }
        if (url === '/demo/ultrai_demo.json') {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              prompt: 'Demo query about sustainable urban transportation',
              models_used: ['gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'],
            }),
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
    });

    it('should auto-populate demo data in demo mode', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      await user.click(screen.getByRole('button', { name: /Go to step 2/i }));

      // Should have demo query pre-filled
      const textarea = screen.getByRole('textbox', {
        name: /What do you need/i,
      });
      expect(textarea).toHaveValue(
        'Demo query about sustainable urban transportation'
      );
    });

    it('should show demo mode indicator', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Move through steps to see demo indicator
      const deepGoal3 = await screen.findByText(/Deep analysis/i);
      await user.click(deepGoal3);
      await user.click(screen.getByRole('button', { name: /Go to step 2/i }));
      await user.click(screen.getByRole('button', { name: /Go to step 3/i }));
      await user.click(screen.getByText(/Premium Query/i).closest('div')!);
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));
      await user.click(screen.getByRole('button', { name: /Submit Add-ons/i }));
      await user.click(
        screen.getByRole('button', { name: /Initialize UltrAI/i })
      );

      expect(screen.getByText(/DEMO MODE/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for all interactive elements', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Check main button
      expect(
        screen.getByRole('button', {
          name: /Start using UltrAI analysis wizard/i,
        })
      ).toBeInTheDocument();

      // Move to step navigation
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Check step navigation
      expect(
        screen.getByRole('navigation', { name: /Wizard steps/i })
      ).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /Go to step 2/i })
      ).toBeInTheDocument();
    });

    it('should support keyboard navigation throughout the wizard', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Tab to Enter button and press Enter
      await user.tab();
      await user.keyboard('{Enter}');

      expect(screen.getByText(/Select your goals/i)).toBeInTheDocument();

      // Tab through checkboxes
      await user.tab();
      expect(
        await screen.findByRole('checkbox', { name: /Deep analysis/i })
      ).toHaveFocus();

      // Space to select
      await user.keyboard(' ');
      expect(
        await screen.findByRole('checkbox', { name: /Deep analysis/i })
      ).toBeChecked();
    });

    it('should announce important status changes to screen readers', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      await user.click(await screen.findByText(/Deep analysis/i));

      // Should have live region for announcements
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toBeInTheDocument();
    });
  });

  describe('Receipt Management', () => {
    it('should update receipt in real-time as selections are made', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));

      // Ensure step 1 content is rendered
      await waitFor(() => {
        expect(screen.getByText(/Select your goals/i)).toBeInTheDocument();
      });

      // Initially should show $0.00
      expect(screen.getByText(/Total: \$0\.00/)).toBeInTheDocument();

      // Add a goal
      await user.click(
        await screen.findByRole('checkbox', { name: /Deep analysis/i })
      );
      expect(screen.getByText(/Total: \$0\.08/)).toBeInTheDocument();

      // Add another goal
      await user.click(
        screen.getByRole('checkbox', { name: /Creative exploration/i })
      );
      expect(screen.getByText(/Total: \$0\.18/)).toBeInTheDocument();

      // Remove first goal
      await user.click(
        await screen.findByRole('checkbox', { name: /Deep analysis/i })
      );
      expect(screen.getByText(/Total: \$0\.10/)).toBeInTheDocument();
    });

    it('should organize receipt items by section', async () => {
      render(<CyberWizard />);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Enter UltrAI/i })
        ).toBeInTheDocument();
      });

      // Make selections across multiple steps
      await user.click(screen.getByRole('button', { name: /Enter UltrAI/i }));
      await screen.findByText(/1\. Select your goals/i);
      await user.click(await screen.findByText(/Deep analysis/i));
      await user.click(screen.getByRole('button', { name: /Go to step 2/i }));

      // Skip to add-ons
      await user.click(screen.getByRole('button', { name: /Go to step 4/i }));
      await user.click(await screen.findByText(/Source Citations|Citations/i));

      // Check receipt shows selected items from goals and add-ons
      const receipt = screen.getByText(/ITEMIZED RECEIPT/i).closest('div');
      expect(receipt).not.toBeNull();
      expect(
        within(receipt!).getByText(/Citations|Source Citations/i)
      ).toBeInTheDocument();
    });
  });
});
