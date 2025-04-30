import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Progressive Disclosure Component
 *
 * Conditionally renders UI elements based on user experience level
 * Helps reduce complexity for new users while allowing advanced users to access all features
 */
const ProgressiveDisclosure = ({
  children,
  requiredLevel = 'beginner',
  currentLevel = 'beginner',
  discoveryMode = false,
  identifier,
  onDiscovery,
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

  // Apply cyberpunk styling for newly discovered features in discovery mode
  const isNewDiscovery = discoveryMode && !hasBeenDiscovered;
  const disclosureClass = `progressive-disclosure ${className} ${
    isNewDiscovery ? 'new-discovery' : ''
  }`;

  return (
    <div className={disclosureClass} data-feature-id={identifier}>
      {isNewDiscovery && (
        <div className="discovery-indicator">
          <span className="discovery-text">NEW FEATURE</span>
        </div>
      )}
      {children}
    </div>
  );
};

ProgressiveDisclosure.propTypes = {
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
  className: PropTypes.string,
};

export default ProgressiveDisclosure;
