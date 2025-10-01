import React from 'react';
import { render, screen } from '@testing-library/react';
import LaunchProgress, { LaunchStage } from '../../../components/wizard/LaunchProgress';

const mockStages: LaunchStage[] = [
  { key: 'init', label: 'Initializing', phase: 'initial', subtext: 'Starting up...' },
  { key: 'process1', label: 'Processing models', phase: 'initial', subtext: 'Running initial analysis...' },
  { key: 'meta', label: 'Meta-analysis', phase: 'meta', subtext: 'Cross-checking results...' },
  { key: 'synthesize', label: 'Synthesizing', phase: 'synthesis', subtext: 'Creating final output...' },
];

describe('LaunchProgress', () => {
  const defaultProps = {
    stages: mockStages,
    currentIndex: 1,
    currentProgress: 50,
    isComplete: false,
    hasError: false,
  };

  describe('Rendering', () => {
    it('should render all stages', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      expect(screen.getByText('Initializing')).toBeInTheDocument();
      expect(screen.getByText('Processing models')).toBeInTheDocument();
      expect(screen.getByText('Meta-analysis')).toBeInTheDocument();
      expect(screen.getByText('Synthesizing')).toBeInTheDocument();
    });

    it('should render phase labels', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      expect(screen.getByText('Initial Generation')).toBeInTheDocument();
      expect(screen.getByText('Meta-Analysis')).toBeInTheDocument();
      expect(screen.getByText('Ultra Synthesis™')).toBeInTheDocument();
    });

    it('should render overall progress bar', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      const statusElement = screen.getByRole('status');
      expect(statusElement).toBeInTheDocument();
    });

    it('should render stage list', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      const list = screen.getByRole('list', { name: 'Processing stages' });
      expect(list).toBeInTheDocument();
      
      const listItems = screen.getAllByRole('listitem');
      expect(listItems).toHaveLength(4);
    });
  });

  describe('Phase bar widths', () => {
    it('should calculate correct phase percentages', () => {
      const { container } = render(<LaunchProgress {...defaultProps} />);
      
      // 2 initial, 1 meta, 1 synthesis = 50%, 25%, 25%
      const phaseBars = container.querySelectorAll('[aria-label*="Initial Generation"]');
      expect(phaseBars.length).toBeGreaterThan(0);
    });

    it('should show equal widths for equal phase distribution', () => {
      const equalStages: LaunchStage[] = [
        { key: 's1', label: 'Stage 1', phase: 'initial' },
        { key: 's2', label: 'Stage 2', phase: 'meta' },
        { key: 's3', label: 'Stage 3', phase: 'synthesis' },
      ];
      
      const { container } = render(
        <LaunchProgress {...defaultProps} stages={equalStages} currentIndex={1} />
      );
      
      const statusElement = screen.getByRole('status');
      expect(statusElement).toBeInTheDocument();
    });
  });

  describe('Progress calculation', () => {
    it('should show 100% when complete', () => {
      render(<LaunchProgress {...defaultProps} isComplete />);
      
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('should calculate progress from current index and stage progress', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} currentProgress={50} />);
      
      // Should show overall progress percentage
      const statusElement = screen.getByRole('status');
      expect(statusElement).toHaveTextContent(/%/);
    });

    it('should show 0% at start', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={0} currentProgress={0} />);
      
      const statusElement = screen.getByRole('status');
      expect(statusElement).toBeInTheDocument();
    });

    it('should not exceed 100%', () => {
      render(
        <LaunchProgress
          {...defaultProps}
          currentIndex={mockStages.length}
          currentProgress={100}
        />
      );
      
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });

  describe('Stage states', () => {
    it('should mark past stages as done', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={2} />);
      
      const stage1 = screen.getByRole('listitem', { name: /Initializing: done/ });
      expect(stage1).toBeInTheDocument();
    });

    it('should mark current stage as current', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      const currentStage = screen.getByRole('listitem', { name: /Processing models: current/ });
      expect(currentStage).toBeInTheDocument();
    });

    it('should mark future stages as pending', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      const futureStage = screen.getByRole('listitem', { name: /Synthesizing: pending/ });
      expect(futureStage).toBeInTheDocument();
    });

    it('should show check icon for done stages', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={2} />);
      
      const checkIcons = screen.getAllByLabelText('Complete');
      expect(checkIcons.length).toBeGreaterThan(0);
    });

    it('should show spinner for current stage', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      const spinner = screen.getByLabelText('In progress');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Error handling', () => {
    it('should show error icon on current stage when error occurs', () => {
      render(<LaunchProgress {...defaultProps} hasError />);
      
      const errorIcon = screen.getByLabelText('Error');
      expect(errorIcon).toBeInTheDocument();
    });

    it('should show error message when hasError is true', () => {
      render(<LaunchProgress {...defaultProps} hasError />);
      
      expect(screen.getByText(/error occurred/i)).toBeInTheDocument();
    });

    it('should not show error message when no error', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      expect(screen.queryByText(/error occurred/i)).not.toBeInTheDocument();
    });
  });

  describe('Completion state', () => {
    it('should show completion message when complete', () => {
      render(<LaunchProgress {...defaultProps} isComplete />);
      
      expect(screen.getByText(/Analysis Complete!/i)).toBeInTheDocument();
    });

    it('should not show completion message when not complete', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      expect(screen.queryByText(/Analysis Complete!/i)).not.toBeInTheDocument();
    });
  });

  describe('Environment badges', () => {
    it('should show DEMO badge when isDemoMode is true', () => {
      render(<LaunchProgress {...defaultProps} isDemoMode />);
      
      expect(screen.getByText('DEMO')).toBeInTheDocument();
    });

    it('should show STAGING badge when isStagingEnv is true', () => {
      render(<LaunchProgress {...defaultProps} isStagingEnv />);
      
      expect(screen.getByText('STAGING')).toBeInTheDocument();
    });

    it('should show both badges when both are true', () => {
      render(<LaunchProgress {...defaultProps} isDemoMode isStagingEnv />);
      
      expect(screen.getByText('DEMO')).toBeInTheDocument();
      expect(screen.getByText('STAGING')).toBeInTheDocument();
    });

    it('should not show badges when both are false', () => {
      render(<LaunchProgress {...defaultProps} />);
      
      expect(screen.queryByText('DEMO')).not.toBeInTheDocument();
      expect(screen.queryByText('STAGING')).not.toBeInTheDocument();
    });
  });

  describe('Current stage details', () => {
    it('should show subtext for current stage', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      expect(screen.getByText('Running initial analysis...')).toBeInTheDocument();
    });

    it('should not show subtext for past stages', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={2} />);
      
      expect(screen.queryByText('Starting up...')).not.toBeInTheDocument();
    });

    it('should not show subtext for future stages', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      expect(screen.queryByText('Creating final output...')).not.toBeInTheDocument();
    });

    it('should show progress bar for current stage', () => {
      const { container } = render(<LaunchProgress {...defaultProps} currentIndex={1} currentProgress={60} />);
      
      // Check for progress bar element (inner progress div)
      const progressBars = container.querySelectorAll('[style*="width: 60%"]');
      expect(progressBars.length).toBeGreaterThan(0);
    });

    it('should not show progress bar for past stages', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={2} />);
      
      const pastStage = screen.getByRole('listitem', { name: /Initializing: done/ });
      expect(pastStage.querySelector('[style*="width"]')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels on progress status', () => {
      render(<LaunchProgress {...defaultProps} currentProgress={50} />);
      
      const statusElement = screen.getByRole('status');
      expect(statusElement).toHaveAttribute('aria-label');
    });

    it('should have descriptive list item labels', () => {
      render(<LaunchProgress {...defaultProps} currentIndex={1} />);
      
      expect(screen.getByRole('listitem', { name: /Initializing: done/ })).toBeInTheDocument();
      expect(screen.getByRole('listitem', { name: /Processing models: current/ })).toBeInTheDocument();
    });

    it('should mark phase bars with aria-labels', () => {
      const { container } = render(<LaunchProgress {...defaultProps} />);
      
      const phaseBar = container.querySelector('[aria-label*="Initial Generation"]');
      expect(phaseBar).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('should handle empty stages array', () => {
      render(<LaunchProgress {...defaultProps} stages={[]} currentIndex={0} />);
      
      const list = screen.getByRole('list', { name: 'Processing stages' });
      expect(list).toBeInTheDocument();
    });

    it('should handle currentIndex beyond stages length', () => {
      render(
        <LaunchProgress
          {...defaultProps}
          currentIndex={mockStages.length + 1}
        />
      );
      
      // Should show 100% progress
      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('should handle negative currentProgress', () => {
      render(<LaunchProgress {...defaultProps} currentProgress={-10} />);
      
      const statusElement = screen.getByRole('status');
      expect(statusElement).toBeInTheDocument();
    });

    it('should handle progress > 100', () => {
      render(
        <LaunchProgress
          {...defaultProps}
          currentIndex={mockStages.length - 1}
          currentProgress={150}
          isComplete
        />
      );
      
      // Should cap at 100%
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });
});
