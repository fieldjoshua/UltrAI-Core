import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import './GuidedTour.css';

/**
 * Guided Tour Component
 *
 * Provides an interactive tour experience with a cyberpunk theme
 * to help users discover features of the application.
 */
const GuidedTour = ({
  steps,
  onComplete,
  onSkip,
  onStepChange,
  isOpen = false,
  startAt = 0,
  className = '',
}) => {
  const [currentStep, setCurrentStep] = useState(startAt);
  const [isVisible, setIsVisible] = useState(isOpen);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tourRef = useRef(null);
  const highlightRef = useRef(null);

  // Handle step changes
  useEffect(() => {
    if (!steps || steps.length === 0 || !isVisible) return;

    const step = steps[currentStep];
    if (!step) return;

    // Position the tour element
    if (step.element) {
      try {
        const targetElement = document.querySelector(step.element);
        if (targetElement) {
          positionTourElement(targetElement, step.position || 'bottom');
          highlightElement(targetElement);
        }
      } catch (error) {
        console.error('Error positioning tour element:', error);
      }
    }

    // Call the onStepChange callback if provided
    if (onStepChange) {
      onStepChange(currentStep, step);
    }
  }, [currentStep, steps, isVisible, onStepChange]);

  // Update visibility when isOpen prop changes
  useEffect(() => {
    setIsVisible(isOpen);
  }, [isOpen]);

  // Position the tour tooltip relative to the target element
  const positionTourElement = (targetElement, preferredPosition = 'bottom') => {
    if (!tourRef.current || !targetElement) return;

    const targetRect = targetElement.getBoundingClientRect();
    const tourRect = tourRef.current.getBoundingClientRect();

    // Calculate available space in different directions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Space available on each side
    const spaceAbove = targetRect.top;
    const spaceBelow = viewportHeight - targetRect.bottom;
    const spaceLeft = targetRect.left;
    const spaceRight = viewportWidth - targetRect.right;

    // Determine best position based on available space and preferred position
    let bestPosition = preferredPosition;

    if (preferredPosition === 'auto') {
      // Find the direction with most space
      const spaces = [
        { position: 'top', space: spaceAbove },
        { position: 'bottom', space: spaceBelow },
        { position: 'left', space: spaceLeft },
        { position: 'right', space: spaceRight },
      ];

      spaces.sort((a, b) => b.space - a.space);
      bestPosition = spaces[0].position;
    }

    // Calculate position based on the chosen direction
    let top, left;

    switch (bestPosition) {
      case 'top':
        top = targetRect.top - tourRect.height - 10;
        left = targetRect.left + targetRect.width / 2 - tourRect.width / 2;
        break;
      case 'bottom':
        top = targetRect.bottom + 10;
        left = targetRect.left + targetRect.width / 2 - tourRect.width / 2;
        break;
      case 'left':
        top = targetRect.top + targetRect.height / 2 - tourRect.height / 2;
        left = targetRect.left - tourRect.width - 10;
        break;
      case 'right':
        top = targetRect.top + targetRect.height / 2 - tourRect.height / 2;
        left = targetRect.right + 10;
        break;
      default:
        top = targetRect.bottom + 10;
        left = targetRect.left + targetRect.width / 2 - tourRect.width / 2;
    }

    // Ensure the tour stays within viewport bounds
    if (left < 10) left = 10;
    if (left + tourRect.width > viewportWidth - 10) {
      left = viewportWidth - tourRect.width - 10;
    }

    if (top < 10) top = 10;
    if (top + tourRect.height > viewportHeight - 10) {
      top = viewportHeight - tourRect.height - 10;
    }

    // Update position state
    setPosition({ top, left });
  };

  // Create a highlight effect around the target element
  const highlightElement = (targetElement) => {
    if (!highlightRef.current || !targetElement) return;

    const targetRect = targetElement.getBoundingClientRect();

    // Position and size the highlight element
    highlightRef.current.style.top = `${targetRect.top - 5}px`;
    highlightRef.current.style.left = `${targetRect.left - 5}px`;
    highlightRef.current.style.width = `${targetRect.width + 10}px`;
    highlightRef.current.style.height = `${targetRect.height + 10}px`;
    highlightRef.current.style.display = 'block';
  };

  // Handle moving to the next step
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // This is the last step
      handleComplete();
    }
  };

  // Handle moving to the previous step
  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Handle tour completion
  const handleComplete = () => {
    setIsVisible(false);
    if (onComplete) {
      onComplete();
    }
  };

  // Handle tour skip
  const handleSkip = () => {
    setIsVisible(false);
    if (onSkip) {
      onSkip(currentStep);
    }
  };

  if (!isVisible || !steps || steps.length === 0) {
    return null;
  }

  const currentStepData = steps[currentStep];
  if (!currentStepData) {
    return null;
  }

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;

  return (
    <>
      {/* Highlight overlay for the target element */}
      <div
        ref={highlightRef}
        className="guided-tour-highlight"
        aria-hidden="true"
      />

      {/* Tour tooltip */}
      <div
        ref={tourRef}
        className={`guided-tour-tooltip ${className}`}
        style={{
          top: `${position.top}px`,
          left: `${position.left}px`,
        }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="tour-step-title"
      >
        {/* Tooltip content */}
        <div className="guided-tour-header">
          <h3 id="tour-step-title" className="guided-tour-title">
            {currentStepData.title}
          </h3>
          <span className="guided-tour-step-indicator">
            {currentStep + 1}/{steps.length}
          </span>
        </div>

        <div className="guided-tour-content">
          <p>{currentStepData.content}</p>

          {currentStepData.image && (
            <img
              src={currentStepData.image}
              alt={currentStepData.imageAlt || 'Tour step illustration'}
              className="guided-tour-image"
            />
          )}

          {currentStepData.extraContent && (
            <div className="guided-tour-extra-content">
              {currentStepData.extraContent}
            </div>
          )}
        </div>

        <div className="guided-tour-actions">
          <button
            className="guided-tour-skip-btn"
            onClick={handleSkip}
            aria-label="Skip tour"
          >
            SKIP
          </button>

          <div className="guided-tour-navigation">
            {!isFirstStep && (
              <button
                className="guided-tour-prev-btn"
                onClick={handlePrev}
                aria-label="Previous step"
              >
                PREV
              </button>
            )}

            <button
              className="guided-tour-next-btn"
              onClick={isLastStep ? handleComplete : handleNext}
              aria-label={isLastStep ? 'Complete tour' : 'Next step'}
            >
              {isLastStep ? 'FINISH' : 'NEXT'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

GuidedTour.propTypes = {
  /** Array of tour step objects */
  steps: PropTypes.arrayOf(
    PropTypes.shape({
      /** Step title */
      title: PropTypes.string.isRequired,
      /** Main step content */
      content: PropTypes.string.isRequired,
      /** Optional image URL */
      image: PropTypes.string,
      /** Alt text for image */
      imageAlt: PropTypes.string,
      /** CSS selector for the target element */
      element: PropTypes.string,
      /** Preferred position (top, right, bottom, left, auto) */
      position: PropTypes.oneOf(['top', 'right', 'bottom', 'left', 'auto']),
      /** Optional additional content (can be a React element) */
      extraContent: PropTypes.node,
    })
  ).isRequired,
  /** Callback when tour is completed */
  onComplete: PropTypes.func,
  /** Callback when tour is skipped */
  onSkip: PropTypes.func,
  /** Callback when step changes */
  onStepChange: PropTypes.func,
  /** Whether the tour is visible */
  isOpen: PropTypes.bool,
  /** Index of the starting step */
  startAt: PropTypes.number,
  /** Additional CSS class name */
  className: PropTypes.string,
};

export default GuidedTour;
