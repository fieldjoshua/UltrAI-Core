import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Simplified Progressive Disclosure Component
 *
 * Uses inline styles instead of requiring CSS.
 * Shows/hides UI elements based on user experience level.
 */
const ProgressiveDisclosureBasic = ({
  children,
  requiredLevel = 'beginner',
  currentLevel = 'beginner',
  discoveryMode = false,
  identifier,
  onDiscovery,
  style = {},
  className = '',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasBeenDiscovered, setHasBeenDiscovered] = useState(false);

  // Experience levels ranked from beginner to expert
  const levels = ['beginner', 'intermediate', 'advanced', 'expert'];

  // Check if feature should be visible based on experience level
  useEffect(() => {
    const requiredLevelIndex = levels.indexOf(requiredLevel.toLowerCase());
    const currentLevelIndex = levels.indexOf(currentLevel.toLowerCase());

    // User's level is sufficient to see the feature
    const canSeeFeature = currentLevelIndex >= requiredLevelIndex;

    // In discovery mode, we might show features that are just above the user's level
    const showInDiscoveryMode =
      discoveryMode && currentLevelIndex + 1 === requiredLevelIndex;

    setIsVisible(canSeeFeature || showInDiscoveryMode);
  }, [requiredLevel, currentLevel, discoveryMode]);

  // Track discovery of feature when first displayed
  useEffect(() => {
    if (isVisible && !hasBeenDiscovered && identifier && onDiscovery) {
      setHasBeenDiscovered(true);
      onDiscovery(identifier, requiredLevel);
    }
  }, [isVisible, hasBeenDiscovered, identifier, onDiscovery, requiredLevel]);

  if (!isVisible) {
    return null;
  }

  // Styles for new discovery highlighting
  const isNewDiscovery = discoveryMode && !hasBeenDiscovered;
  const baseStyle = {
    position: 'relative',
    ...style,
  };

  const newDiscoveryStyle = isNewDiscovery
    ? {
        animation: 'highlight 0.5s ease-out',
        boxShadow: '0 0 8px rgba(255, 204, 0, 0.7)',
        transition: 'all 0.3s ease',
      }
    : {};

  return (
    <div
      className={className}
      style={{ ...baseStyle, ...newDiscoveryStyle }}
      data-feature-id={identifier}
    >
      {isNewDiscovery && (
        <div
          style={{
            position: 'absolute',
            top: '-8px',
            right: '-8px',
            backgroundColor: '#333',
            color: '#ffcc00',
            borderRadius: '3px',
            padding: '2px 5px',
            fontSize: '10px',
            fontWeight: 'bold',
            zIndex: 1,
          }}
        >
          NEW FEATURE
        </div>
      )}
      {children}

      {/* Add keyframes for highlight animation */}
      {isNewDiscovery && (
        <style>
          {`
            @keyframes highlight {
              0% { transform: scale(0.98); opacity: 0.8; }
              50% { transform: scale(1.02); opacity: 1; }
              100% { transform: scale(1); opacity: 1; }
            }
          `}
        </style>
      )}
    </div>
  );
};

ProgressiveDisclosureBasic.propTypes = {
  children: PropTypes.node.isRequired,
  requiredLevel: PropTypes.oneOf([
    'beginner',
    'intermediate',
    'advanced',
    'expert',
  ]),
  currentLevel: PropTypes.oneOf([
    'beginner',
    'intermediate',
    'advanced',
    'expert',
  ]),
  discoveryMode: PropTypes.bool,
  identifier: PropTypes.string,
  onDiscovery: PropTypes.func,
  style: PropTypes.object,
  className: PropTypes.string,
};

export default ProgressiveDisclosureBasic;
