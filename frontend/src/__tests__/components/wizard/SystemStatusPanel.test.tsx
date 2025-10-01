import React from 'react';
import { render, screen } from '@testing-library/react';
import SystemStatusPanel from '../../../components/wizard/SystemStatusPanel';

describe('SystemStatusPanel', () => {
  const defaultProps = {
    modelStatuses: {
      'gpt-4': 'ready' as const,
      'claude-3': 'ready' as const,
      'gemini-pro': 'ready' as const,
    },
  };

  describe('Rendering', () => {
    it('should render with all models ready', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('3/3')).toBeInTheDocument();
    });

    it('should render model count correctly', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label', 'System status: 3 of 3 models ready');
    });

    it('should render latency indicator', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByText('~250ms')).toBeInTheDocument();
    });

    it('should render API status', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByText('API')).toBeInTheDocument();
    });
  });

  describe('Connection status icons', () => {
    it('should show connected icon when all models ready', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByLabelText('Connected')).toBeInTheDocument();
    });

    it('should show partial connection icon when some models ready', () => {
      const partialStatuses = {
        'gpt-4': 'ready' as const,
        'claude-3': 'checking' as const,
        'gemini-pro': 'error' as const,
      };
      
      render(<SystemStatusPanel modelStatuses={partialStatuses} />);
      
      expect(screen.getByLabelText('Partial connection')).toBeInTheDocument();
      expect(screen.getByText('1/3')).toBeInTheDocument();
    });

    it('should show error icon when no models ready', () => {
      const errorStatuses = {
        'gpt-4': 'error' as const,
        'claude-3': 'checking' as const,
      };
      
      render(<SystemStatusPanel modelStatuses={errorStatuses} />);
      
      expect(screen.getByLabelText('Connection error')).toBeInTheDocument();
      expect(screen.getByText('0/2')).toBeInTheDocument();
    });

    it('should count only ready models', () => {
      const mixedStatuses = {
        'model-1': 'ready' as const,
        'model-2': 'ready' as const,
        'model-3': 'checking' as const,
        'model-4': 'error' as const,
      };
      
      render(<SystemStatusPanel modelStatuses={mixedStatuses} />);
      
      expect(screen.getByText('2/4')).toBeInTheDocument();
    });
  });

  describe('Environment badges', () => {
    it('should show DEMO badge when isDemoMode is true', () => {
      render(<SystemStatusPanel {...defaultProps} isDemoMode />);
      
      const demoBadge = screen.getByText('DEMO');
      expect(demoBadge).toBeInTheDocument();
      expect(demoBadge).toHaveAttribute('aria-label', 'Demo mode active');
    });

    it('should show STAGING badge when isStagingEnv is true', () => {
      render(<SystemStatusPanel {...defaultProps} isStagingEnv />);
      
      const stagingBadge = screen.getByText('STAGING');
      expect(stagingBadge).toBeInTheDocument();
      expect(stagingBadge).toHaveAttribute('aria-label', 'Staging environment');
    });

    it('should show both badges when both are true', () => {
      render(<SystemStatusPanel {...defaultProps} isDemoMode isStagingEnv />);
      
      expect(screen.getByText('DEMO')).toBeInTheDocument();
      expect(screen.getByText('STAGING')).toBeInTheDocument();
    });

    it('should not show badges when both are false', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.queryByText('DEMO')).not.toBeInTheDocument();
      expect(screen.queryByText('STAGING')).not.toBeInTheDocument();
    });
  });

  describe('Demo mode latency', () => {
    it('should show faster latency in demo mode', () => {
      render(<SystemStatusPanel {...defaultProps} isDemoMode />);
      
      expect(screen.getByText('~12ms')).toBeInTheDocument();
      expect(screen.queryByText('~250ms')).not.toBeInTheDocument();
    });

    it('should show normal latency when not in demo mode', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByText('~250ms')).toBeInTheDocument();
      expect(screen.queryByText('~12ms')).not.toBeInTheDocument();
    });
  });

  describe('Theme variants', () => {
    it('should apply dark theme by default', () => {
      const { container } = render(<SystemStatusPanel {...defaultProps} />);
      
      const panel = container.querySelector('[role="status"]');
      expect(panel).toHaveClass('bg-black/30', 'text-white/60');
    });

    it('should apply light theme when isNonTimeSkin is true', () => {
      const { container } = render(<SystemStatusPanel {...defaultProps} isNonTimeSkin />);
      
      const panel = container.querySelector('[role="status"]');
      expect(panel).toHaveClass('bg-gray-100/80', 'text-gray-600');
    });
  });

  describe('Accessibility', () => {
    it('should have role="status"', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should have aria-live="polite"', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-live', 'polite');
    });

    it('should have descriptive aria-label', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveAttribute('aria-label');
      expect(status.getAttribute('aria-label')).toContain('models ready');
    });

    it('should label connection status icon', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      expect(screen.getByLabelText('Connected')).toBeInTheDocument();
    });

    it('should label latency indicator', () => {
      render(<SystemStatusPanel {...defaultProps} />);
      
      const status = screen.getByRole('status');
      expect(status.textContent).toContain('~250ms');
    });
  });

  describe('Edge cases', () => {
    it('should handle empty model statuses', () => {
      render(<SystemStatusPanel modelStatuses={{}} />);
      
      expect(screen.getByText('0/0')).toBeInTheDocument();
      expect(screen.getByLabelText('Connection error')).toBeInTheDocument();
    });

    it('should handle single model', () => {
      const singleModel = { 'gpt-4': 'ready' as const };
      
      render(<SystemStatusPanel modelStatuses={singleModel} />);
      
      expect(screen.getByText('1/1')).toBeInTheDocument();
      expect(screen.getByLabelText('Connected')).toBeInTheDocument();
    });

    it('should handle all checking status', () => {
      const checkingStatuses = {
        'model-1': 'checking' as const,
        'model-2': 'checking' as const,
      };
      
      render(<SystemStatusPanel modelStatuses={checkingStatuses} />);
      
      expect(screen.getByText('0/2')).toBeInTheDocument();
      expect(screen.getByLabelText('Connection error')).toBeInTheDocument();
    });

    it('should handle all error status', () => {
      const errorStatuses = {
        'model-1': 'error' as const,
        'model-2': 'error' as const,
      };
      
      render(<SystemStatusPanel modelStatuses={errorStatuses} />);
      
      expect(screen.getByText('0/2')).toBeInTheDocument();
      expect(screen.getByLabelText('Connection error')).toBeInTheDocument();
    });
  });

  describe('Visual indicators', () => {
    it('should render pulse animation on API status dot', () => {
      const { container } = render(<SystemStatusPanel {...defaultProps} />);
      
      const pulseDot = container.querySelector('.animate-pulse');
      expect(pulseDot).toBeInTheDocument();
    });

    it('should position panel at bottom left', () => {
      const { container } = render(<SystemStatusPanel {...defaultProps} />);
      
      const panel = container.querySelector('[role="status"]');
      expect(panel).toHaveClass('bottom-6', 'left-6');
    });
  });
});
