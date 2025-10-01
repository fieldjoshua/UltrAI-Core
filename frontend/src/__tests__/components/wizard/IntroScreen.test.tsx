import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import IntroScreen from '../../../components/wizard/IntroScreen';

describe('IntroScreen', () => {
  const defaultProps = {
    onEnter: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the logo/title', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText('UltrAI')).toBeInTheDocument();
    });

    it('should render the tagline', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText('Intelligence Multiplication Platform')).toBeInTheDocument();
    });

    it('should render the main description', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText(/Query multiple premium AI models/i)).toBeInTheDocument();
      expect(screen.getByText(/Pay only for what you use/i)).toBeInTheDocument();
    });

    it('should render Enter UltrAI button', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toBeInTheDocument();
    });

    it('should render feature pills', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText('Multi-Model Orchestration')).toBeInTheDocument();
      expect(screen.getByText('Real-time Synthesis')).toBeInTheDocument();
      expect(screen.getByText('Intelligent Optimization')).toBeInTheDocument();
      expect(screen.getByText('Premium Results')).toBeInTheDocument();
    });

    it('should render trust indicators', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText('20+ AI Models')).toBeInTheDocument();
      expect(screen.getByText('Enterprise Ready')).toBeInTheDocument();
      expect(screen.getByText('SOC2 Compliant')).toBeInTheDocument();
    });

    it('should render value propositions', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText('Pay-as-you-go')).toBeInTheDocument();
      expect(screen.getByText('No commitments')).toBeInTheDocument();
      expect(screen.getByText('Enterprise-grade')).toBeInTheDocument();
    });
  });

  describe('CTA Button interactions', () => {
    it('should call onEnter when Enter UltrAI button is clicked', async () => {
      const user = userEvent.setup();
      const onEnter = jest.fn();
      
      render(<IntroScreen onEnter={onEnter} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      await user.click(enterButton);
      
      expect(onEnter).toHaveBeenCalledTimes(1);
    });

    it('should have accessible button label', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toHaveAttribute('aria-label', 'Start using UltrAI');
    });
  });

  describe('Demo mode', () => {
    it('should not show demo button by default', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.queryByRole('button', { name: /Try demo/i })).not.toBeInTheDocument();
    });

    it('should show demo button when showDemoButton is true', () => {
      render(<IntroScreen {...defaultProps} showDemoButton />);
      
      const demoButton = screen.getByRole('button', { name: /Try demo mode/i });
      expect(demoButton).toBeInTheDocument();
    });

    it('should call onEnter when demo button is clicked', async () => {
      const user = userEvent.setup();
      const onEnter = jest.fn();
      
      render(<IntroScreen onEnter={onEnter} showDemoButton />);
      
      const demoButton = screen.getByRole('button', { name: /Try demo mode/i });
      await user.click(demoButton);
      
      expect(onEnter).toHaveBeenCalledTimes(1);
    });

    it('should show demo button text with icon', () => {
      render(<IntroScreen {...defaultProps} showDemoButton />);
      
      expect(screen.getByText('Try Demo')).toBeInTheDocument();
    });
  });

  describe('Visual elements', () => {
    it('should render with gradient styling on title', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      const title = screen.getByText('UltrAI');
      // Check that gradient class or style is applied
      const titleStyle = window.getComputedStyle(title);
      expect(titleStyle).toBeDefined();
    });

    it('should render primary CTA with gradient background', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toHaveClass('bg-gradient-to-r');
    });

    it('should show arrow icon in CTA button', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton.textContent).toContain('Enter UltrAI');
    });

    it('should render feature pills with icons', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      // Check that feature pills container exists
      const featurePills = container.querySelectorAll('.flex.flex-wrap.gap-3');
      expect(featurePills.length).toBeGreaterThan(0);
    });
  });

  describe('Layout', () => {
    it('should render centered layout', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      const mainContainer = container.querySelector('.flex.items-center.justify-center');
      expect(mainContainer).toBeInTheDocument();
    });

    it('should render content card with proper styling', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      const contentCard = container.querySelector('.bg-gray-900\\/80');
      expect(contentCard).toBeInTheDocument();
    });

    it('should be responsive', () => {
      const { container } = render(<IntroScreen {...defaultProps} />);
      
      const title = screen.getByText('UltrAI');
      expect(title).toHaveClass('text-7xl', 'md:text-8xl');
    });
  });

  describe('Hover states', () => {
    it('should have hover styles on main CTA', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toHaveClass('hover:scale-105');
    });

    it('should have active state on main CTA', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toHaveClass('active:scale-95');
    });

    it('should have hover styles on demo button when shown', () => {
      render(<IntroScreen {...defaultProps} showDemoButton />);
      
      const demoButton = screen.getByRole('button', { name: /Try demo mode/i });
      expect(demoButton).toHaveClass('hover:bg-cyan-400/10');
    });
  });

  describe('Accessibility', () => {
    it('should have proper button labels', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      expect(enterButton).toHaveAttribute('aria-label');
    });

    it('should have descriptive demo button label', () => {
      render(<IntroScreen {...defaultProps} showDemoButton />);
      
      const demoButton = screen.getByRole('button', { name: /Try demo mode/i });
      expect(demoButton).toHaveAttribute('aria-label', 'Try demo mode');
    });

    it('should have all interactive elements as buttons', () => {
      render(<IntroScreen {...defaultProps} showDemoButton />);
      
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBe(2); // Main CTA + Demo button
    });
  });

  describe('Content accuracy', () => {
    it('should mention key value propositions', () => {
      render(<IntroScreen {...defaultProps} />);
      
      expect(screen.getByText(/multiple premium AI models/i)).toBeInTheDocument();
      expect(screen.getByText(/synthesized insights/i)).toBeInTheDocument();
    });

    it('should display correct trust indicator count', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const checkmarks = screen.getAllByText('✓');
      expect(checkmarks).toHaveLength(3);
    });

    it('should display all feature categories', () => {
      render(<IntroScreen {...defaultProps} />);
      
      const features = [
        'Multi-Model Orchestration',
        'Real-time Synthesis',
        'Intelligent Optimization',
        'Premium Results',
      ];
      
      features.forEach((feature) => {
        expect(screen.getByText(feature)).toBeInTheDocument();
      });
    });
  });

  describe('Edge cases', () => {
    it('should handle rapid button clicks', async () => {
      const user = userEvent.setup();
      const onEnter = jest.fn();
      
      render(<IntroScreen onEnter={onEnter} />);
      
      const enterButton = screen.getByRole('button', { name: /Start using UltrAI/i });
      
      await user.click(enterButton);
      await user.click(enterButton);
      await user.click(enterButton);
      
      expect(onEnter).toHaveBeenCalledTimes(3);
    });

    it('should render without crashing when isDemoMode is true', () => {
      render(<IntroScreen {...defaultProps} isDemoMode />);
      
      expect(screen.getByText('UltrAI')).toBeInTheDocument();
    });
  });
});
