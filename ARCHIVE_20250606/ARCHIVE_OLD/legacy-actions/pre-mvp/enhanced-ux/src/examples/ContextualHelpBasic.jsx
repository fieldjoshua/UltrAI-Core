const ContextualHelp = ({
  type = 'tooltip',
  position = 'top',
  content,
  children,
  title,
}) => {
  const [isVisible, setIsVisible] = React.useState(false);

  const helpContainerStyle = {
    position: 'relative',
    display: 'inline-block',
  };

  const tooltipStyle = {
    position: 'absolute',
    zIndex: 1000,
    backgroundColor: '#333',
    color: '#fff',
    padding: '8px 12px',
    borderRadius: '4px',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
    width: type === 'tooltip' ? '150px' : '220px',
    maxWidth: '250px',
    display: isVisible ? 'block' : 'none',
    ...getPositionStyle(position),
  };

  const titleStyle = {
    margin: '0 0 5px 0',
    fontSize: '16px',
    fontWeight: 'bold',
    borderBottom: '1px solid #555',
    paddingBottom: '5px',
  };

  function getPositionStyle(pos) {
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

  const handleClick = () => {
    if (type === 'popover') {
      setIsVisible(!isVisible);
    }
  };

  return (
    <div
      style={helpContainerStyle}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      {children}

      <div style={tooltipStyle}>
        {title && <div style={titleStyle}>{title}</div>}
        <div>{content}</div>
      </div>
    </div>
  );
};

// Export for use in other files
window.ContextualHelp = ContextualHelp;
