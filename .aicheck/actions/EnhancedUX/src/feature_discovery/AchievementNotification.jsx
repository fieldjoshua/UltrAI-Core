import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import './AchievementNotification.css';

/**
 * AchievementNotification Component
 *
 * Displays a cyberpunk-styled notification when a user unlocks an achievement.
 * Features animations, sound effects, and visual flair to enhance the gamification experience.
 */
const AchievementNotification = ({
  achievement,
  onClose,
  autoHide = true,
  duration = 6000,
  position = 'bottom-right',
  className = '',
  playSoundEffect = true,
}) => {
  const [visible, setVisible] = useState(false);
  const [closing, setClosing] = useState(false);
  const notificationRef = useRef(null);
  const timerRef = useRef(null);

  // Display notification with entrance animation
  useEffect(() => {
    // Short delay to ensure DOM is ready for animation
    const animationDelay = setTimeout(() => {
      setVisible(true);
    }, 100);

    // Play sound effect if enabled
    if (playSoundEffect && achievement) {
      try {
        const audio = new Audio();
        // Use different sounds for different tiers
        switch (achievement.tier) {
          case 'GOLD':
          case 'PLATINUM':
          case 'DIAMOND':
            audio.src =
              'data:audio/mp3;base64,SUQzAwAAAAAfdlRJVDIAAAAZAAAATGV2ZWwgVXAgU291bmQgRWZmZWN0AAA=';
            break;
          default:
            audio.src =
              'data:audio/mp3;base64,SUQzAwAAAAAfdlRJVDIAAAAZAAAATGV2ZWwgVXAgU291bmQgRWZmZWN0AAA=';
        }
        audio.volume = 0.5;
        audio
          .play()
          .catch((e) => console.warn('Could not play sound effect', e));
      } catch (error) {
        console.warn('Error playing sound effect', error);
      }
    }

    // Auto-hide notification after duration
    if (autoHide) {
      timerRef.current = setTimeout(() => {
        handleClose();
      }, duration);
    }

    return () => {
      clearTimeout(animationDelay);
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [achievement, autoHide, duration, playSoundEffect]);

  // Handle notification close
  const handleClose = () => {
    setClosing(true);

    // Wait for close animation to finish
    setTimeout(() => {
      setVisible(false);
      if (onClose) {
        onClose();
      }
    }, 500); // Match with CSS animation duration
  };

  // If no achievement data, don't render
  if (!achievement) {
    return null;
  }

  // Get tier information
  const tierInfo = {
    BRONZE: { color: '#cd7f32', icon: '🔶' },
    SILVER: { color: '#c0c0c0', icon: '⬜' },
    GOLD: { color: '#ffd700', icon: '🔸' },
    PLATINUM: { color: '#e5e4e2', icon: '⬛' },
    DIAMOND: { color: '#b9f2ff', icon: '💎' },
  }[achievement.tier] || { color: '#cd7f32', icon: '🔶' };

  // Set position classes
  const positionClass = `achievement-notification-${position}`;

  // Set combined classes
  const notificationClasses = `
    achievement-notification
    ${visible ? 'visible' : ''}
    ${closing ? 'closing' : ''}
    ${positionClass}
    tier-${achievement.tier.toLowerCase()}
    ${className}
  `;

  return (
    <div
      ref={notificationRef}
      className={notificationClasses}
      role="alert"
      aria-live="polite"
    >
      <div className="achievement-content">
        <div className="achievement-glow-effect"></div>

        <div className="achievement-header">
          <span className="achievement-tier" style={{ color: tierInfo.color }}>
            {achievement.tier}
          </span>
          <button
            className="achievement-close-btn"
            onClick={handleClose}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>

        <div className="achievement-body">
          <div className="achievement-icon">
            <span>{achievement.icon || tierInfo.icon}</span>
          </div>

          <div className="achievement-info">
            <h3 className="achievement-title">{achievement.title}</h3>
            <p className="achievement-description">{achievement.description}</p>
          </div>
        </div>

        <div className="achievement-footer">
          <span className="achievement-status">ACHIEVEMENT UNLOCKED</span>
          {achievement.points && (
            <span className="achievement-points">+{achievement.points} XP</span>
          )}
        </div>

        <div className="achievement-circuit-decoration"></div>
      </div>
    </div>
  );
};

AchievementNotification.propTypes = {
  achievement: PropTypes.shape({
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    tier: PropTypes.string.isRequired,
    icon: PropTypes.string,
    points: PropTypes.number,
  }),
  onClose: PropTypes.func,
  autoHide: PropTypes.bool,
  duration: PropTypes.number,
  position: PropTypes.oneOf([
    'top-right',
    'top-left',
    'bottom-right',
    'bottom-left',
    'top-center',
    'bottom-center',
  ]),
  className: PropTypes.string,
  playSoundEffect: PropTypes.bool,
};

export default AchievementNotification;
