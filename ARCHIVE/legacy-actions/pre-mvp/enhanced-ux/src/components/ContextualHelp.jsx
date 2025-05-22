import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import './ContextualHelp.css';

/**
 * ContextualHelp Component
 *
 * Provides contextual help through tooltips, popovers, and hints with cyberpunk styling.
 * Can be triggered automatically based on user actions or displayed on-demand.
 */
const ContextualHelp = ({
  targetId,
  content,
  title,
  position = 'auto',
  trigger = 'hover',
  type = 'tooltip',
  isOpen = false,
  onClose,
  className = '',
  showIcon = true,
  allowHtml = false,
  image,
  imageAlt,
  delay = 300,
  duration = 0,
}) => {
  const [visible, setVisible] = useState(isOpen);
  const [coordinates, setCoordinates] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);
  const timerRef = useRef(null);
  const durationTimerRef = useRef(null);

  // Get best position for the tooltip
  const calculatePosition = () => {
    if (!targetId) return { top: 0, left: 0 };

    const targetElement =
      document.getElementById(targetId) || document.querySelector(targetId);
    if (!targetElement || !tooltipRef.current) return { top: 0, left: 0 };

    const targetRect = targetElement.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    const scrollX = window.scrollX || document.documentElement.scrollLeft;
    const scrollY = window.scrollY || document.documentElement.scrollTop;

    // Viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Calculate available space in each direction
    const spaceAbove = targetRect.top;
    const spaceBelow = viewportHeight - targetRect.bottom;
    const spaceLeft = targetRect.left;
    const spaceRight = viewportWidth - targetRect.right;

    // Choose position based on available space and preferred position
    let bestPosition = position;
    if (position === 'auto') {
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

    // Calculate coordinates based on the selected position
    let top, left;

    switch (bestPosition) {
      case 'top':
        top = targetRect.top + scrollY - tooltipRect.height - 10;
        left =
          targetRect.left +
          scrollX +
          targetRect.width / 2 -
          tooltipRect.width / 2;
        break;
      case 'bottom':
        top = targetRect.bottom + scrollY + 10;
        left =
          targetRect.left +
          scrollX +
          targetRect.width / 2 -
          tooltipRect.width / 2;
        break;
      case 'left':
        top =
          targetRect.top +
          scrollY +
          targetRect.height / 2 -
          tooltipRect.height / 2;
        left = targetRect.left + scrollX - tooltipRect.width - 10;
        break;
      case 'right':
        top =
          targetRect.top +
          scrollY +
          targetRect.height / 2 -
          tooltipRect.height / 2;
        left = targetRect.right + scrollX + 10;
        break;
      default:
        top = targetRect.bottom + scrollY + 10;
        left =
          targetRect.left +
          scrollX +
          targetRect.width / 2 -
          tooltipRect.width / 2;
    }

    // Ensure tooltip stays within viewport bounds
    if (left < 10) left = 10;
    if (left + tooltipRect.width > viewportWidth - 10) {
      left = viewportWidth - tooltipRect.width - 10;
    }

    if (top < 10) top = 10;
    if (top + tooltipRect.height > viewportHeight - 10) {
      top = viewportHeight - tooltipRect.height - 10;
    }

    return { top, left, position: bestPosition };
  };

  // Handle events for different trigger types
  useEffect(() => {
    if (!targetId || trigger === 'manual') return;

    const targetElement =
      document.getElementById(targetId) || document.querySelector(targetId);
    if (!targetElement) return;

    const handleMouseEnter = () => {
      if (trigger !== 'hover') return;
      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(() => {
        setVisible(true);

        // Set auto-hide timer if duration is specified
        if (duration > 0) {
          if (durationTimerRef.current) clearTimeout(durationTimerRef.current);
          durationTimerRef.current = setTimeout(() => {
            setVisible(false);
          }, duration);
        }
      }, delay);
    };

    const handleMouseLeave = () => {
      if (trigger !== 'hover') return;
      if (timerRef.current) clearTimeout(timerRef.current);

      timerRef.current = setTimeout(() => {
        setVisible(false);
      }, 200);
    };

    const handleClick = () => {
      if (trigger !== 'click') return;
      setVisible(!visible);

      // Set auto-hide timer if duration is specified
      if (duration > 0 && !visible) {
        if (durationTimerRef.current) clearTimeout(durationTimerRef.current);
        durationTimerRef.current = setTimeout(() => {
          setVisible(false);
        }, duration);
      }
    };

    // Add event listeners based on trigger type
    if (trigger === 'hover') {
      targetElement.addEventListener('mouseenter', handleMouseEnter);
      targetElement.addEventListener('mouseleave', handleMouseLeave);
    } else if (trigger === 'click') {
      targetElement.addEventListener('click', handleClick);
    }

    // Cleanup
    return () => {
      if (trigger === 'hover') {
        targetElement.removeEventListener('mouseenter', handleMouseEnter);
        targetElement.removeEventListener('mouseleave', handleMouseLeave);
      } else if (trigger === 'click') {
        targetElement.removeEventListener('click', handleClick);
      }

      if (timerRef.current) clearTimeout(timerRef.current);
      if (durationTimerRef.current) clearTimeout(durationTimerRef.current);
    };
  }, [targetId, trigger, visible, delay, duration]);

  // Update visibility when isOpen prop changes
  useEffect(() => {
    setVisible(isOpen);
  }, [isOpen]);

  // Update position when visibility changes
  useEffect(() => {
    if (visible && tooltipRef.current) {
      const newPosition = calculatePosition();
      setCoordinates(newPosition);

      // Add positioning class for arrows
      if (tooltipRef.current) {
        tooltipRef.current.setAttribute(
          'data-position',
          newPosition.position || 'bottom'
        );
      }
    }
  }, [visible, targetId]);

  // Handle click outside to close popover/hint
  useEffect(() => {
    if (!visible || type === 'tooltip') return;

    const handleClickOutside = (event) => {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target)) {
        const targetElement =
          document.getElementById(targetId) || document.querySelector(targetId);
        if (targetElement && !targetElement.contains(event.target)) {
          setVisible(false);
          if (onClose) onClose();
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [visible, targetId, type, onClose]);

  // Handle escape key to close
  useEffect(() => {
    if (!visible) return;

    const handleEscapeKey = (event) => {
      if (event.key === 'Escape') {
        setVisible(false);
        if (onClose) onClose();
      }
    };

    document.addEventListener('keydown', handleEscapeKey);
    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [visible, onClose]);

  if (!visible) return null;

  // Determine CSS classes based on type
  const tooltipClassName = `contextual-help ${type} ${className}`;

  return (
    <div
      ref={tooltipRef}
      className={tooltipClassName}
      style={{
        top: `${coordinates.top}px`,
        left: `${coordinates.left}px`,
      }}
      role={type === 'tooltip' ? 'tooltip' : 'dialog'}
      aria-labelledby={title ? 'help-title' : undefined}
      aria-describedby="help-content"
    >
      {/* Tooltip/Popover content */}
      {title && (
        <div className="help-header">
          <h3 id="help-title" className="help-title">
            {title}
          </h3>
          {(type === 'popover' || type === 'hint') && (
            <button
              className="help-close-btn"
              onClick={() => {
                setVisible(false);
                if (onClose) onClose();
              }}
              aria-label="Close"
            >
              ×
            </button>
          )}
        </div>
      )}

      <div className="help-body">
        {image && (
          <img
            src={image}
            alt={imageAlt || 'Help illustration'}
            className="help-image"
          />
        )}

        <div id="help-content" className="help-content">
          {allowHtml ? (
            <div dangerouslySetInnerHTML={{ __html: content }} />
          ) : (
            <p>{content}</p>
          )}
        </div>
      </div>

      {/* Tooltip arrow */}
      <div className="help-arrow"></div>
    </div>
  );
};

ContextualHelp.propTypes = {
  /** ID or selector of the target element */
  targetId: PropTypes.string.isRequired,
  /** Content to display in the tooltip/popover */
  content: PropTypes.string.isRequired,
  /** Optional title for the tooltip/popover */
  title: PropTypes.string,
  /** Position of the tooltip relative to the target (auto, top, right, bottom, left) */
  position: PropTypes.oneOf(['auto', 'top', 'right', 'bottom', 'left']),
  /** How the tooltip/popover is triggered (hover, click, manual) */
  trigger: PropTypes.oneOf(['hover', 'click', 'manual']),
  /** Type of contextual help (tooltip, popover, hint) */
  type: PropTypes.oneOf(['tooltip', 'popover', 'hint']),
  /** Whether the tooltip/popover is open (for manual control) */
  isOpen: PropTypes.bool,
  /** Callback when the tooltip/popover is closed */
  onClose: PropTypes.func,
  /** Additional CSS class name */
  className: PropTypes.string,
  /** Whether to show the help icon */
  showIcon: PropTypes.bool,
  /** Whether to allow HTML in the content */
  allowHtml: PropTypes.bool,
  /** Optional image URL */
  image: PropTypes.string,
  /** Alt text for the image */
  imageAlt: PropTypes.string,
  /** Delay before showing the tooltip (ms) */
  delay: PropTypes.number,
  /** Duration to show the tooltip (ms, 0 for indefinite) */
  duration: PropTypes.number,
};

export default ContextualHelp;
