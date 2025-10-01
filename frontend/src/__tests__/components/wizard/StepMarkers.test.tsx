import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import StepMarkers from '../../../components/wizard/StepMarkers';

describe('StepMarkers', () => {
  const defaultProps = {
    currentStep: 1,
    totalSteps: 5,
    onStepClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render correct number of step markers', () => {
      render(<StepMarkers {...defaultProps} />);
      
      const navigation = screen.getByRole('navigation', { name: 'Step progress' });
      const buttons = screen.getAllByRole('button');
      
      expect(navigation).toBeInTheDocument();
      expect(buttons).toHaveLength(5);
    });

    it('should render with custom labels', () => {
      const labels = ['Start', 'Configure', 'Review', 'Process', 'Complete'];
      render(<StepMarkers {...defaultProps} labels={labels} />);
      
      expect(screen.getByRole('button', { name: 'Start' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Configure' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Complete' })).toBeInTheDocument();
    });

    it('should use default labels when none provided', () => {
      render(<StepMarkers {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: 'Step 1' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Step 5' })).toBeInTheDocument();
    });
  });

  describe('Current step highlighting', () => {
    it('should mark current step with aria-current="step"', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const currentButton = screen.getByRole('button', { name: 'Step 3' });
      expect(currentButton).toHaveAttribute('aria-current', 'step');
    });

    it('should not mark other steps with aria-current', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const step1 = screen.getByRole('button', { name: 'Step 1' });
      const step5 = screen.getByRole('button', { name: 'Step 5' });
      
      expect(step1).not.toHaveAttribute('aria-current');
      expect(step5).not.toHaveAttribute('aria-current');
    });

    it('should highlight first step when currentStep is 0', () => {
      render(<StepMarkers {...defaultProps} currentStep={0} />);
      
      const firstStep = screen.getByRole('button', { name: 'Step 1' });
      expect(firstStep).toHaveAttribute('aria-current', 'step');
    });
  });

  describe('Click interactions', () => {
    it('should call onStepClick when clicking past step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} currentStep={3} onStepClick={onStepClick} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 2' });
      await user.click(pastStep);
      
      expect(onStepClick).toHaveBeenCalledWith(1);
      expect(onStepClick).toHaveBeenCalledTimes(1);
    });

    it('should call onStepClick when clicking current step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} currentStep={2} onStepClick={onStepClick} />);
      
      const currentStep = screen.getByRole('button', { name: 'Step 3' });
      await user.click(currentStep);
      
      expect(onStepClick).toHaveBeenCalledWith(2);
    });

    it('should not call onStepClick when clicking future step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} currentStep={1} onStepClick={onStepClick} />);
      
      const futureStep = screen.getByRole('button', { name: 'Step 5' });
      await user.click(futureStep);
      
      expect(onStepClick).not.toHaveBeenCalled();
    });

    it('should not call onStepClick when disabled', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} disabled onStepClick={onStepClick} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 1' });
      await user.click(pastStep);
      
      expect(onStepClick).not.toHaveBeenCalled();
    });
  });

  describe('Disabled state', () => {
    it('should disable all steps when disabled prop is true', () => {
      render(<StepMarkers {...defaultProps} disabled />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveAttribute('aria-disabled', 'true');
      });
    });

    it('should disable future steps', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const futureStep1 = screen.getByRole('button', { name: 'Step 4' });
      const futureStep2 = screen.getByRole('button', { name: 'Step 5' });
      
      expect(futureStep1).toHaveAttribute('aria-disabled', 'true');
      expect(futureStep2).toHaveAttribute('aria-disabled', 'true');
    });

    it('should not disable past or current steps', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 1' });
      const currentStep = screen.getByRole('button', { name: 'Step 3' });
      
      expect(pastStep).toHaveAttribute('aria-disabled', 'false');
      expect(currentStep).toHaveAttribute('aria-disabled', 'false');
    });
  });

  describe('Keyboard navigation', () => {
    it('should set tabIndex=0 for clickable steps', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 1' });
      const currentStep = screen.getByRole('button', { name: 'Step 3' });
      
      expect(pastStep).toHaveAttribute('tabIndex', '0');
      expect(currentStep).toHaveAttribute('tabIndex', '0');
    });

    it('should set tabIndex=-1 for future steps', () => {
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const futureStep = screen.getByRole('button', { name: 'Step 5' });
      expect(futureStep).toHaveAttribute('tabIndex', '-1');
    });

    it('should set tabIndex=-1 for all steps when disabled', () => {
      render(<StepMarkers {...defaultProps} disabled />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toHaveAttribute('tabIndex', '-1');
      });
    });

    it('should support Enter key to activate step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} currentStep={3} onStepClick={onStepClick} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 2' });
      pastStep.focus();
      await user.keyboard('{Enter}');
      
      expect(onStepClick).toHaveBeenCalledWith(1);
    });

    it('should support Space key to activate step', async () => {
      const user = userEvent.setup();
      const onStepClick = jest.fn();
      
      render(<StepMarkers {...defaultProps} currentStep={3} onStepClick={onStepClick} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 2' });
      pastStep.focus();
      await user.keyboard(' ');
      
      expect(onStepClick).toHaveBeenCalledWith(1);
    });
  });

  describe('Accessibility', () => {
    it('should have navigation landmark with label', () => {
      render(<StepMarkers {...defaultProps} />);
      
      const nav = screen.getByRole('navigation', { name: 'Step progress' });
      expect(nav).toBeInTheDocument();
    });

    it('should have descriptive aria-labels', () => {
      render(<StepMarkers {...defaultProps} currentStep={1} />);
      
      expect(screen.getByRole('button', { name: 'Step 1' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Step 2' })).toBeInTheDocument();
    });

    it('should show tooltips on hover for clickable steps', async () => {
      const user = userEvent.setup();
      render(<StepMarkers {...defaultProps} currentStep={2} />);
      
      const pastStep = screen.getByRole('button', { name: 'Step 1' });
      await user.hover(pastStep);
      
      const tooltip = screen.getByRole('tooltip', { name: 'Step 1' });
      expect(tooltip).toBeInTheDocument();
    });

    it('should not show tooltips for disabled steps', () => {
      render(<StepMarkers {...defaultProps} disabled />);
      
      const tooltips = screen.queryAllByRole('tooltip');
      expect(tooltips).toHaveLength(0);
    });
  });

  describe('Edge cases', () => {
    it('should handle single step', () => {
      render(<StepMarkers currentStep={0} totalSteps={1} onStepClick={jest.fn()} />);
      
      const buttons = screen.getAllByRole('button');
      expect(buttons).toHaveLength(1);
      expect(buttons[0]).toHaveAttribute('aria-current', 'step');
    });

    it('should handle last step as current', () => {
      render(<StepMarkers {...defaultProps} currentStep={4} />);
      
      const lastStep = screen.getByRole('button', { name: 'Step 5' });
      expect(lastStep).toHaveAttribute('aria-current', 'step');
      expect(lastStep).toHaveAttribute('aria-disabled', 'false');
    });

    it('should handle zero as currentStep', () => {
      render(<StepMarkers {...defaultProps} currentStep={0} />);
      
      const firstStep = screen.getByRole('button', { name: 'Step 1' });
      expect(firstStep).toHaveAttribute('aria-current', 'step');
    });
  });
});
