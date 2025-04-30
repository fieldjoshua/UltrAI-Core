import React, { useState, useEffect } from 'react';

const ContextualHelp = ({
  children,
  type = 'tooltip',
  position = 'top',
  content,
  title,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  const tooltipStyle = {
    position: 'absolute',
    backgroundColor: 'white',
    padding: '8px 12px',
    borderRadius: '4px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
    zIndex: 1000,
    maxWidth: '250px',
    fontSize: '14px',
    color: '#333',
    ...getPosition(position),
  };

  const titleStyle = {
    fontWeight: 'bold',
    marginBottom: '5px',
    borderBottom: '1px solid #eee',
    paddingBottom: '5px',
  };

  const containerStyle = {
    position: 'relative',
    display: 'inline-block',
  };

  function getPosition(pos) {
    switch (pos) {
      case 'top':
        return {
          bottom: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginBottom: '8px',
        };
      case 'bottom':
        return {
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginTop: '8px',
        };
      case 'left':
        return {
          right: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginRight: '8px',
        };
      case 'right':
        return {
          left: '100%',
          top: '50%',
          transform: 'translateY(-50%)',
          marginLeft: '8px',
        };
      default:
        return {
          top: '100%',
          left: '50%',
          transform: 'translateX(-50%)',
          marginTop: '8px',
        };
    }
  }

  // Event handlers
  const handleMouseEnter = () => {
    if (type === 'tooltip' || type === 'hint') {
      setIsVisible(true);
    }
  };

  const handleMouseLeave = () => {
    if (type === 'tooltip' || type === 'hint') {
      setIsVisible(false);
    }
  };

  const handleClick = (e) => {
    if (type === 'popover') {
      e.stopPropagation();
      setIsVisible(!isVisible);
    }
  };

  // Close popover when clicking outside
  useEffect(() => {
    if (type === 'popover' && isVisible) {
      const handleOutsideClick = (e) => {
        setIsVisible(false);
      };

      document.addEventListener('click', handleOutsideClick);
      return () => {
        document.removeEventListener('click', handleOutsideClick);
      };
    }
  }, [isVisible, type]);

  return (
    <div
      style={containerStyle}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      {children}

      {isVisible && (
        <div style={tooltipStyle}>
          {title && <div style={titleStyle}>{title}</div>}
          <div>{content}</div>
        </div>
      )}
    </div>
  );
};

export default ContextualHelp;
