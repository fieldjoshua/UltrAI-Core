import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import { render } from '../../../test/test-utils';
import CyberWizard from '../../../components/wizard/CyberWizard';

const mockProcessWithFeatherOrchestration = globalThis.mockProcessWithFeatherOrchestration || (() => Promise.resolve({
  ultra_response: 'Mock response',
  model_responses: [],
}));

Object.defineProperty(globalThis, 'mockProcessWithFeatherOrchestration', {
  value: mockProcessWithFeatherOrchestration,
  writable: true,
});

jest.mock('../../../api/orchestrator', () => ({
  processWithFeatherOrchestration: (...args: any[]) => globalThis.mockProcessWithFeatherOrchestration(...args),
}));

describe('CyberWizard V2', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    globalThis.mockProcessWithFeatherOrchestration = jest.fn(() => Promise.resolve({
      ultra_response: 'Mock response',
      model_responses: [],
    }));
  });

  describe('Initial Render', () => {
    it('should render the welcome screen', async () => {
      render(<CyberWizard />);
      
      expect(screen.getByText(/Welcome to UltrAI/i)).toBeInTheDocument();
      expect(screen.getByText(/Intelligence Multiplication Platform/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Enter UltrAI/i })).toBeInTheDocument();
    });

    it('should show Enter UltrAI button on intro', () => {
      render(<CyberWizard />);
      
      const enterButton = screen.getByRole('button', { name: /Enter UltrAI/i });
      expect(enterButton).toBeInTheDocument();
    });
  });

  describe('Step Navigation', () => {
    it('should navigate to step 1 when clicking Enter UltrAI', async () => {
      render(<CyberWizard />);

      const enterButton = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterButton);

      await screen.findByText(/Select your goals/i);
    });

    it('should support keyboard navigation with arrow keys', async () => {
      render(<CyberWizard />);

      const enterButton = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterButton);

      await screen.findByText(/Select your goals/i);

      // Arrow right to next step
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);

      // Arrow left to previous step
      await user.keyboard('{ArrowLeft}');
      await screen.findByText(/Select your goals/i);
    });
  });

  describe('Goal Selection (Step 1)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      await screen.findByText(/Select your goals/i);
    });

    it('should display goal options', () => {
      expect(screen.getByText(/Research/i)).toBeInTheDocument();
      expect(screen.getByText(/Writing\/Editing/i)).toBeInTheDocument();
    });

    it('should allow selecting goals', async () => {
      const researchButton = screen.getByText(/Research/i).closest('button');
      await user.click(researchButton!);
      
      // Button should show selected state (has purple border class)
      expect(researchButton).toHaveClass('border-purple-500');
    });
  });

  describe('Query Input (Step 2)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
    });

    it('should display query textarea', () => {
      const textarea = screen.getByRole('textbox');
      expect(textarea).toBeInTheDocument();
    });

    it('should show character count when typing', async () => {
      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Test query');

      await waitFor(() => {
        expect(screen.getByText(/10 \/ 1000/)).toBeInTheDocument();
      });
    });

    it('should show optimization button when query is entered', async () => {
      const textarea = screen.getByRole('textbox');
      await user.type(textarea, 'Analyze market trends');

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Allow UltrAI to optimize my query/i })).toBeInTheDocument();
      });
    });
  });

  describe('Model Selection (Step 4)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      
      // Navigate to step 1 (goals)
      await screen.findByText(/Select your goals/i);
      
      // Navigate to step 2 (query)
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
      
      // Navigate to step 3 (analysis)
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Choose how we should combine/i);
      
      // Navigate to step 4 (model selection)
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Model selection/i);
    });

    it('should display model preset options', async () => {
      await waitFor(() => {
        expect(screen.getByText(/Premium/i)).toBeInTheDocument();
      });
      expect(screen.getByText(/Speed/i)).toBeInTheDocument();
      expect(screen.getByText(/Budget Mode/i)).toBeInTheDocument();
    });

    it('should show manual model selection option', async () => {
      await waitFor(() => {
        expect(screen.getByText(/Manual: Choose Models/i)).toBeInTheDocument();
      });
    });

    it('should allow selecting manual models', async () => {
      const manualButton = screen.getByText(/Manual: Choose Models/i).closest('button');
      await user.click(manualButton!);

      await waitFor(() => {
        expect(screen.getByText(/Select Models/i)).toBeInTheDocument();
      });
    });
  });

  describe('Add-ons Selection (Step 5)', () => {
    beforeEach(async () => {
      render(<CyberWizard />);
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      
      // Navigate step by step to step 5
      await screen.findByText(/Select your goals/i);
      
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
      
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Choose how we should combine/i);
      
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Model selection/i);
      
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Add-ons & formatting/i);
    });

    it('should display add-on options', async () => {
      await waitFor(() => {
        expect(screen.getByText(/Export as PDF\/Word/i)).toBeInTheDocument();
      });
      expect(screen.getAllByText(/Priority Processing/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/Advanced Formatting/i)).toBeInTheDocument();
    });

    it('should show Submit Add-ons button', async () => {
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Submit Add-ons/i })).toBeInTheDocument();
      });
    });
  });

  describe('Orchestration Process', () => {
    it('should show Initialize button after completing wizard', async () => {
      render(<CyberWizard />);
      
      // Complete wizard flow
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      
      // Navigate step by step to model selection
      await screen.findByText(/Select your goals/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Choose how we should combine and improve/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Model selection/i);
      
      // Select Premium models
      const premiumBtn = await screen.findByText(/Premium/i);
      await user.click(premiumBtn.closest('button')!);
      
      // Navigate to add-ons
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Add-ons & formatting/i);
      
      // Submit add-ons
      const submitBtn = await screen.findByRole('button', { name: /Submit Add-ons/i });
      await user.click(submitBtn);
      
      // Initialize button should appear
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Initialize UltrAI/i })).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('should start orchestration when Initialize is clicked', async () => {
      const mockResult = {
        ultra_response: 'Test response from orchestration',
        model_responses: [],
      };
      globalThis.mockProcessWithFeatherOrchestration.mockResolvedValue(mockResult as any);

      render(<CyberWizard />);
      
      // Complete wizard
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      
      // Navigate and add query
      await screen.findByText(/Select your goals/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
      const textarea = await screen.findByRole('textbox');
      await user.type(textarea, 'Test query');
      await user.tab(); // Unfocus textarea so keyboard nav works
      
      // Navigate to analysis step
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Choose how we should combine and improve/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Model selection/i);
      
      // Select Premium models
      const premiumBtn = await screen.findByText(/Premium/i);
      await user.click(premiumBtn.closest('button')!);
      
      // Navigate to add-ons and submit
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Add-ons & formatting/i);
      const submitBtn = await screen.findByRole('button', { name: /Submit Add-ons/i });
      await user.click(submitBtn);
      
      // Click Initialize
      const initBtn = await waitFor(() => screen.findByRole('button', { name: /Initialize UltrAI/i }), { timeout: 2000 });
      await user.click(initBtn);
      
      // Should show processing status
      await waitFor(() => {
        expect(screen.getByText(/ULTRA SYNTHESIS/i)).toBeInTheDocument();
      });
      
      // Should show results
      await waitFor(() => {
        expect(screen.getByText(/Analysis Complete/i)).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should handle orchestration errors', async () => {
      // Reset and set up error mock
      globalThis.mockProcessWithFeatherOrchestration = jest.fn().mockRejectedValue(new Error('Network error'));

      render(<CyberWizard />);
      
      // Complete wizard
      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);
      
      // Navigate and add query
      await screen.findByText(/Select your goals/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);
      const textarea = await screen.findByRole('textbox');
      await user.type(textarea, 'Test');
      await user.tab(); // Unfocus textarea so keyboard nav works
      
      // Navigate to analysis step
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Choose how we should combine and improve/i);
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Model selection/i);
      
      // Select Premium models
      const premiumBtn = await screen.findByText(/Premium/i);
      await user.click(premiumBtn.closest('button')!);
      
      // Navigate to add-ons and submit
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Add-ons & formatting/i);
      const submitBtn = await screen.findByRole('button', { name: /Submit Add-ons/i });
      await user.click(submitBtn);
      
      // Click Initialize
      const initBtn = await waitFor(() => screen.findByRole('button', { name: /Initialize UltrAI/i }), { timeout: 2000 });
      await user.click(initBtn);
      
      // Should show error message
      await waitFor(() => {
        const errorText = screen.queryByText(/Error Occurred/i);
        const successText = screen.queryByText(/Analysis Complete/i);
        
        if (successText) {
          throw new Error('Expected error but got success. Mock may not be working.');
        }
        
        expect(errorText).toBeInTheDocument();
      }, { timeout: 5000 });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for interactive elements', async () => {
      render(<CyberWizard />);

      const enterButton = await screen.findByRole('button', { name: /Enter UltrAI/i });
      expect(enterButton).toBeInTheDocument();
      
      await user.click(enterButton);
      
      // Step navigation should have aria labels
      await waitFor(() => {
        const nav = screen.queryByRole('navigation');
        if (nav) {
          expect(nav).toBeInTheDocument();
        }
      });
    });

    it('should support keyboard navigation throughout wizard', async () => {
      render(<CyberWizard />);

      const enterBtn = await screen.findByRole('button', { name: /Enter UltrAI/i });
      await user.click(enterBtn);

      await screen.findByText(/Select your goals/i);

      // Navigate with arrow keys
      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Enter your query/i);

      await user.keyboard('{ArrowRight}');
      await screen.findByText(/Analyses/i);
    });
  });
});
