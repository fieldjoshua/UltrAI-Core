import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';

/**
 * A simplified version of ContextualHelp with minimal styling
 */
const ContextualHelpBasic = ({
  targetId,
  content,
  title,
  position = 'bottom',
  trigger = 'hover',
  isOpen = false,
  onClose = () => {},
}) => {
  const [showTooltip, setShowTooltip] = useState(
    trigger === 'manual' ? isOpen : false
  );
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef(null);

  // Basic styles using inline styling
  const tooltipStyles = {
    position: 'absolute',
    zIndex: 1000,
    width: '250px',
    backgroundColor: '#fff',
    color: '#333',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
    padding: '10px',
    ...tooltipPosition,
  };

  const titleStyles = {
    margin: '0 0 10px 0',
    padding: '0 0 5px 0',
    borderBottom: '1px solid #eee',
    fontSize: '16px',
    fontWeight: 'bold',
  };

  const contentStyles = {
    margin: '0',
    fontSize: '14px',
  };

  const buttonStyles = {
    padding: '5px 10px',
    backgroundColor: '#f5f5f5',
    border: '1px solid #ddd',
    borderRadius: '3px',
    cursor: 'pointer',
    marginTop: '10px',
    fontSize: '12px',
  };

  // Calculate position based on target element
  const updatePosition = () => {
    const targetElement = document.getElementById(targetId);
    const tooltipElement = tooltipRef.current;

    if (!targetElement || !tooltipElement) return;

    const targetRect = targetElement.getBoundingClientRect();
    const tooltipRect = tooltipElement.getBoundingClientRect();

    // Calculate position based on the specified position prop
    let top, left;

    switch (position) {
      case 'top':
        top = targetRect.top - tooltipRect.height - 10;
        left = targetRect.left + targetRect.width / 2 - tooltipRect.width / 2;
        break;
      case 'right':
        top = targetRect.top + targetRect.height / 2 - tooltipRect.height / 2;
        left = targetRect.right + 10;
        break;
      case 'left':
        top = targetRect.top + targetRect.height / 2 - tooltipRect.height / 2;
        left = targetRect.left - tooltipRect.width - 10;
        break;
      case 'bottom':
      default:
        top = targetRect.bottom + 10;
        left = targetRect.left + targetRect.width / 2 - tooltipRect.width / 2;
        break;
    }

    // Add window scroll offset
    top += window.scrollY;
    left += window.scrollX;

    // Boundary check to keep tooltip within viewport
    if (left < 0) left = 0;
    if (left + tooltipRect.width > window.innerWidth) {
      left = window.innerWidth - tooltipRect.width;
    }

    setTooltipPosition({ top, left });
  };

  // Event handlers for different trigger types
  useEffect(() => {
    const targetElement = document.getElementById(targetId);

    if (!targetElement) return;

    const handleMouseEnter = () => trigger === 'hover' && setShowTooltip(true);
    const handleMouseLeave = () => trigger === 'hover' && setShowTooltip(false);
    const handleClick = () =>
      trigger === 'click' && setShowTooltip((prev) => !prev);

    if (trigger === 'hover') {
      targetElement.addEventListener('mouseenter', handleMouseEnter);
      targetElement.addEventListener('mouseleave', handleMouseLeave);
    } else if (trigger === 'click') {
      targetElement.addEventListener('click', handleClick);
    }

    return () => {
      if (trigger === 'hover') {
        targetElement.removeEventListener('mouseenter', handleMouseEnter);
        targetElement.removeEventListener('mouseleave', handleMouseLeave);
      } else if (trigger === 'click') {
        targetElement.removeEventListener('click', handleClick);
      }
    };
  }, [targetId, trigger]);

  // Update position when tooltip is shown
  useEffect(() => {
    if (showTooltip) {
      updatePosition();
      window.addEventListener('resize', updatePosition);
      window.addEventListener('scroll', updatePosition);
    }

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [showTooltip]);

  // For manual control
  useEffect(() => {
    if (trigger === 'manual') {
      setShowTooltip(isOpen);
    }
  }, [isOpen, trigger]);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        tooltipRef.current &&
        !tooltipRef.current.contains(event.target) &&
        trigger === 'click' &&
        event.target.id !== targetId
      ) {
        setShowTooltip(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [targetId, trigger]);

  // If tooltip shouldn't be shown, don't render anything
  if (!showTooltip) return null;

  // Portal to render tooltip at body level to avoid positioning issues
  return ReactDOM.createPortal(
    <div ref={tooltipRef} style={tooltipStyles}>
      {title && <h3 style={titleStyles}>{title}</h3>}
      <p style={contentStyles}>{content}</p>
      {trigger !== 'hover' && (
        <button
          style={buttonStyles}
          onClick={() => {
            setShowTooltip(false);
            if (trigger === 'manual') onClose();
          }}
        >
          Close
        </button>
      )}
    </div>,
    document.body
  );
};

ContextualHelpBasic.propTypes = {
  targetId: PropTypes.string.isRequired,
  content: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  title: PropTypes.string,
  position: PropTypes.oneOf(['top', 'bottom', 'left', 'right', 'auto']),
  trigger: PropTypes.oneOf(['hover', 'click', 'manual']),
  isOpen: PropTypes.bool,
  onClose: PropTypes.func,
};

export default ContextualHelpBasic;
