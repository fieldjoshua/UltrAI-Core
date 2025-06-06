/**
 * UltraAI Suggestion Presenter
 *
 * This module transforms suggestion data into interactive UI components
 * with cyberpunk styling for presenting to users.
 */

/**
 * Component type constants
 */
const COMPONENT_TYPES = {
  CARD: 'card',
  INLINE: 'inline',
  TOOLTIP: 'tooltip',
  MODAL: 'modal',
  AMBIENT: 'ambient',
};

/**
 * Animation type constants
 */
const ANIMATION_TYPES = {
  ENTRY: 'entry',
  EXIT: 'exit',
  IDLE: 'idle',
  ATTENTION: 'attention',
  INTERACTION: 'interaction',
};

/**
 * Theme constants
 */
const THEMES = {
  STANDARD: 'standard',
  HIGH_CONTRAST: 'high-contrast',
  MINIMAL: 'minimal',
  INTENSE: 'intense',
};

/**
 * CSS styles for cyberpunk components
 */
const CYBERPUNK_STYLES = {
  // Base colors
  colors: {
    background: '#121212',
    backgroundAlt: '#1e1e1e',
    primary: '#0ff',
    secondary: '#f0f',
    accent: '#ff0',
    text: '#ffffff',
    textSecondary: '#cccccc',
    success: '#00ff66',
    warning: '#ffcc00',
    error: '#ff3366',
    border: '#333333',
  },

  // Neon glow definitions
  glows: {
    primary: '0 0 5px rgba(0, 255, 255, 0.5), 0 0 10px rgba(0, 255, 255, 0.3)',
    secondary:
      '0 0 5px rgba(255, 0, 255, 0.5), 0 0 10px rgba(255, 0, 255, 0.3)',
    accent: '0 0 5px rgba(255, 255, 0, 0.5), 0 0 10px rgba(255, 255, 0, 0.3)',
    success: '0 0 5px rgba(0, 255, 102, 0.5), 0 0 10px rgba(0, 255, 102, 0.3)',
    warning: '0 0 5px rgba(255, 204, 0, 0.5), 0 0 10px rgba(255, 204, 0, 0.3)',
    error: '0 0 5px rgba(255, 51, 102, 0.5), 0 0 10px rgba(255, 51, 102, 0.3)',
  },

  // Fonts
  fonts: {
    primary: "'Share Tech Mono', monospace, 'Courier New', monospace",
    secondary: "'Rajdhani', sans-serif, Arial, sans-serif",
  },

  // Base card styles
  card: {
    backgroundColor: 'rgba(18, 18, 18, 0.95)',
    border: '1px solid #333333',
    borderRadius: '4px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 255, 255, 0.3)',
    padding: '16px',
    maxWidth: '400px',
    fontFamily: "'Share Tech Mono', monospace, 'Courier New', monospace",
    color: '#ffffff',
    zIndex: 1000,
  },

  // Header styles
  header: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '12px',
    borderBottom: '1px solid #333333',
    paddingBottom: '8px',
    display: 'flex',
    alignItems: 'center',
  },

  // Content styles
  content: {
    fontSize: '14px',
    lineHeight: '1.4',
    marginBottom: '16px',
  },

  // Action button styles
  button: {
    backgroundColor: 'rgba(30, 30, 30, 0.8)',
    color: '#0ff',
    border: '1px solid #0ff',
    padding: '6px 14px',
    fontSize: '14px',
    fontFamily: "'Share Tech Mono', monospace",
    borderRadius: '2px',
    cursor: 'pointer',
    margin: '0 8px 0 0',
    boxShadow: '0 0 5px rgba(0, 255, 255, 0.3)',
    transition: 'all 0.2s ease',
  },

  buttonHover: {
    backgroundColor: 'rgba(0, 255, 255, 0.2)',
    boxShadow: '0 0 8px rgba(0, 255, 255, 0.5)',
  },

  secondaryButton: {
    backgroundColor: 'transparent',
    color: '#cccccc',
    border: '1px solid #333333',
    boxShadow: 'none',
  },

  secondaryButtonHover: {
    backgroundColor: 'rgba(51, 51, 51, 0.5)',
    color: '#ffffff',
  },

  // Icon styles
  icon: {
    width: '24px',
    height: '24px',
    marginRight: '8px',
    fill: '#0ff',
  },

  // Glitch animation
  glitchAnimation: `
    @keyframes glitch {
      0% { transform: translate(0); }
      20% { transform: translate(-2px, 2px); }
      40% { transform: translate(-2px, -2px); }
      60% { transform: translate(2px, 2px); }
      80% { transform: translate(2px, -2px); }
      100% { transform: translate(0); }
    }
  `,

  // Pulse animation
  pulseAnimation: `
    @keyframes pulse {
      0% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.5), 0 0 10px rgba(0, 255, 255, 0.3); }
      50% { box-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.5); }
      100% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.5), 0 0 10px rgba(0, 255, 255, 0.3); }
    }
  `,

  // Scan animation
  scanAnimation: `
    @keyframes scan {
      0% { background-position: 0% 0%; }
      100% { background-position: 0% 100%; }
    }
  `,
};

/**
 * Creates a style element with cyberpunk CSS definitions
 * @private
 */
function _createStyles() {
  // Check if styles are already added
  if (document.getElementById('ultra-suggestion-styles')) {
    return;
  }

  const styleElement = document.createElement('style');
  styleElement.id = 'ultra-suggestion-styles';

  styleElement.textContent = `
    ${CYBERPUNK_STYLES.glitchAnimation}
    ${CYBERPUNK_STYLES.pulseAnimation}
    ${CYBERPUNK_STYLES.scanAnimation}

    .ultra-suggestion-card {
      position: fixed;
      background-color: ${CYBERPUNK_STYLES.card.backgroundColor};
      border: ${CYBERPUNK_STYLES.card.border};
      border-radius: ${CYBERPUNK_STYLES.card.borderRadius};
      box-shadow: ${CYBERPUNK_STYLES.card.boxShadow};
      padding: ${CYBERPUNK_STYLES.card.padding};
      max-width: ${CYBERPUNK_STYLES.card.maxWidth};
      font-family: ${CYBERPUNK_STYLES.card.fontFamily};
      color: ${CYBERPUNK_STYLES.card.color};
      z-index: ${CYBERPUNK_STYLES.card.zIndex};
      transition: opacity 0.3s ease, transform 0.3s ease;
    }

    .ultra-suggestion-card.entry {
      animation: glitch 0.2s ease-in-out,
                 pulse 2s infinite;
    }

    .ultra-suggestion-card.exit {
      opacity: 0;
      transform: scale(0.9);
      animation: glitch 0.3s ease-in-out;
    }

    .ultra-suggestion-header {
      font-size: ${CYBERPUNK_STYLES.header.fontSize};
      font-weight: ${CYBERPUNK_STYLES.header.fontWeight};
      margin-bottom: ${CYBERPUNK_STYLES.header.marginBottom};
      border-bottom: ${CYBERPUNK_STYLES.header.borderBottom};
      padding-bottom: ${CYBERPUNK_STYLES.header.paddingBottom};
      display: ${CYBERPUNK_STYLES.header.display};
      align-items: ${CYBERPUNK_STYLES.header.alignItems};
    }

    .ultra-suggestion-content {
      font-size: ${CYBERPUNK_STYLES.content.fontSize};
      line-height: ${CYBERPUNK_STYLES.content.lineHeight};
      margin-bottom: ${CYBERPUNK_STYLES.content.marginBottom};
    }

    .ultra-suggestion-actions {
      display: flex;
      justify-content: flex-end;
    }

    .ultra-suggestion-button {
      background-color: ${CYBERPUNK_STYLES.button.backgroundColor};
      color: ${CYBERPUNK_STYLES.button.color};
      border: ${CYBERPUNK_STYLES.button.border};
      padding: ${CYBERPUNK_STYLES.button.padding};
      font-size: ${CYBERPUNK_STYLES.button.fontSize};
      font-family: ${CYBERPUNK_STYLES.button.fontFamily};
      border-radius: ${CYBERPUNK_STYLES.button.borderRadius};
      cursor: ${CYBERPUNK_STYLES.button.cursor};
      margin: ${CYBERPUNK_STYLES.button.margin};
      box-shadow: ${CYBERPUNK_STYLES.button.boxShadow};
      transition: ${CYBERPUNK_STYLES.button.transition};
    }

    .ultra-suggestion-button:hover {
      background-color: ${CYBERPUNK_STYLES.buttonHover.backgroundColor};
      box-shadow: ${CYBERPUNK_STYLES.buttonHover.boxShadow};
    }

    .ultra-suggestion-button.secondary {
      background-color: ${CYBERPUNK_STYLES.secondaryButton.backgroundColor};
      color: ${CYBERPUNK_STYLES.secondaryButton.color};
      border: ${CYBERPUNK_STYLES.secondaryButton.border};
      box-shadow: ${CYBERPUNK_STYLES.secondaryButton.boxShadow};
    }

    .ultra-suggestion-button.secondary:hover {
      background-color: ${CYBERPUNK_STYLES.secondaryButtonHover.backgroundColor};
      color: ${CYBERPUNK_STYLES.secondaryButtonHover.color};
    }

    .ultra-suggestion-icon {
      width: ${CYBERPUNK_STYLES.icon.width};
      height: ${CYBERPUNK_STYLES.icon.height};
      margin-right: ${CYBERPUNK_STYLES.icon.marginRight};
      fill: ${CYBERPUNK_STYLES.icon.fill};
    }

    /* Suggestion types */
    .ultra-suggestion-card.feature-discovery {
      border-color: ${CYBERPUNK_STYLES.colors.primary};
      box-shadow: ${CYBERPUNK_STYLES.glows.primary};
    }

    .ultra-suggestion-card.workflow-tip {
      border-color: ${CYBERPUNK_STYLES.colors.accent};
      box-shadow: ${CYBERPUNK_STYLES.glows.accent};
    }

    .ultra-suggestion-card.error-prevention {
      border-color: ${CYBERPUNK_STYLES.colors.warning};
      box-shadow: ${CYBERPUNK_STYLES.glows.warning};
    }

    .ultra-suggestion-card.performance-optimization {
      border-color: ${CYBERPUNK_STYLES.colors.success};
      box-shadow: ${CYBERPUNK_STYLES.glows.success};
    }

    /* Prominence levels */
    .ultra-suggestion-card.high {
      z-index: 1010;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 255, 255, 0.5);
    }

    .ultra-suggestion-card.low {
      opacity: 0.9;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 255, 255, 0.2);
    }
  `;

  document.head.appendChild(styleElement);
}

/**
 * Renders a suggestion card
 * @param {Object} suggestion The suggestion to render
 * @param {Function} onAction Callback when action is taken
 * @param {Function} onDismiss Callback when suggestion is dismissed
 * @param {Object} options Additional configuration options
 * @returns {HTMLElement} The created card element
 */
function renderSuggestionCard(suggestion, onAction, onDismiss, options = {}) {
  // Ensure styles are added
  _createStyles();

  // Create container
  const card = document.createElement('div');
  card.className = `ultra-suggestion-card ${suggestion.type} ${
    suggestion.style?.prominence || 'medium'
  }`;
  card.id = `ultra-suggestion-${suggestion.id}`;
  card.dataset.suggestionId = suggestion.id;

  // Add header
  const header = document.createElement('div');
  header.className = 'ultra-suggestion-header';

  // Add icon if available
  if (suggestion.style?.icon) {
    const icon = document.createElement('span');
    icon.className = 'ultra-suggestion-icon';
    icon.innerHTML = `<svg viewBox="0 0 24 24"><use href="#${suggestion.style.icon}"></use></svg>`;
    header.appendChild(icon);
  }

  // Add title
  const title = document.createTextNode(suggestion.title);
  header.appendChild(title);
  card.appendChild(header);

  // Add content
  const content = document.createElement('div');
  content.className = 'ultra-suggestion-content';
  content.textContent = suggestion.description;
  card.appendChild(content);

  // Add actions
  const actions = document.createElement('div');
  actions.className = 'ultra-suggestion-actions';

  // Primary action button
  if (suggestion.action) {
    const actionBtn = document.createElement('button');
    actionBtn.className = 'ultra-suggestion-button primary';
    actionBtn.textContent = getActionButtonText(suggestion.action);
    actionBtn.addEventListener('click', (e) => {
      e.preventDefault();
      onAction(suggestion);
      hideCard(card);
    });
    actions.appendChild(actionBtn);
  }

  // Dismiss button
  const dismissBtn = document.createElement('button');
  dismissBtn.className = 'ultra-suggestion-button secondary';
  dismissBtn.textContent = 'Dismiss';
  dismissBtn.addEventListener('click', (e) => {
    e.preventDefault();
    onDismiss(suggestion);
    hideCard(card);
  });
  actions.appendChild(dismissBtn);

  card.appendChild(actions);

  // Position the card
  positionCard(card, options.position || 'bottom-right');

  // Add to DOM
  document.body.appendChild(card);

  // Apply entry animation
  setTimeout(() => {
    card.classList.add('entry');
  }, 10);

  return card;
}

/**
 * Provides appropriate button text based on action type
 * @param {Object} action The action object
 * @returns {String} The button text
 * @private
 */
function getActionButtonText(action) {
  switch (action.type) {
    case 'showFeature':
      return 'Show Me';
    case 'showTutorial':
      return 'Learn How';
    case 'showTip':
      return 'Got It';
    case 'navigate':
      return 'Go There';
    default:
      return 'Take Action';
  }
}

/**
 * Positions a card on the screen
 * @param {HTMLElement} card The card element
 * @param {String} position Position identifier (top-left, top-right, bottom-left, bottom-right, center)
 * @private
 */
function positionCard(card, position) {
  const margin = 20;

  switch (position) {
    case 'top-left':
      card.style.top = `${margin}px`;
      card.style.left = `${margin}px`;
      break;
    case 'top-right':
      card.style.top = `${margin}px`;
      card.style.right = `${margin}px`;
      break;
    case 'bottom-left':
      card.style.bottom = `${margin}px`;
      card.style.left = `${margin}px`;
      break;
    case 'bottom-right':
      card.style.bottom = `${margin}px`;
      card.style.right = `${margin}px`;
      break;
    case 'center':
      card.style.top = '50%';
      card.style.left = '50%';
      card.style.transform = 'translate(-50%, -50%)';
      break;
    default:
      // Default to bottom-right
      card.style.bottom = `${margin}px`;
      card.style.right = `${margin}px`;
  }
}

/**
 * Hides a card with exit animation
 * @param {HTMLElement} card The card element
 * @private
 */
function hideCard(card) {
  card.classList.remove('entry');
  card.classList.add('exit');

  // Remove from DOM after animation completes
  setTimeout(() => {
    if (card.parentNode) {
      card.parentNode.removeChild(card);
    }
  }, 300);
}

/**
 * Suggestion Presenter class
 */
class SuggestionPresenter {
  constructor(options = {}) {
    this.options = {
      defaultPosition: options.position || 'bottom-right',
      theme: options.theme || THEMES.STANDARD,
      animationsEnabled: options.animationsEnabled !== false,
      maxVisibleSuggestions: options.maxVisibleSuggestions || 1,
      ...options,
    };

    this.visibleSuggestions = new Map();
    this.suggestionQueue = [];
    this.feedbackSystem = options.feedbackSystem;
  }

  /**
   * Present a suggestion to the user
   * @param {Object} suggestion The suggestion to present
   * @param {String} style The presentation style (card, inline, tooltip)
   * @returns {HTMLElement} The rendered suggestion element
   */
  presentSuggestion(suggestion, style = COMPONENT_TYPES.CARD) {
    // Check if we can show more suggestions
    if (this.visibleSuggestions.size >= this.options.maxVisibleSuggestions) {
      // Queue the suggestion for later
      this.suggestionQueue.push({ suggestion, style });
      return null;
    }

    let element;

    // Render the appropriate component
    switch (style) {
      case COMPONENT_TYPES.CARD:
        element = this._renderCard(suggestion);
        break;
      // Future component types
      default:
        element = this._renderCard(suggestion);
    }

    if (element) {
      this.visibleSuggestions.set(suggestion.id, {
        element,
        suggestion,
        timestamp: new Date(),
      });
    }

    return element;
  }

  /**
   * Dismiss a specific suggestion
   * @param {String} suggestionId ID of the suggestion to dismiss
   * @param {String} feedbackType Type of feedback for the dismissal
   */
  dismissSuggestion(suggestionId, feedbackType) {
    const suggestionData = this.visibleSuggestions.get(suggestionId);

    if (suggestionData) {
      hideCard(suggestionData.element);
      this.visibleSuggestions.delete(suggestionId);

      // Record feedback if available
      if (this.feedbackSystem && feedbackType) {
        this.feedbackSystem.recordFeedback(suggestionId, feedbackType);
      }

      // Show next queued suggestion if any
      this._showNextQueuedSuggestion();
    }
  }

  /**
   * Dismiss all visible suggestions
   * @param {String} feedbackType Type of feedback for the dismissal
   */
  dismissAllSuggestions(feedbackType) {
    for (const [suggestionId, suggestionData] of this.visibleSuggestions) {
      hideCard(suggestionData.element);

      // Record feedback if available
      if (this.feedbackSystem && feedbackType) {
        this.feedbackSystem.recordFeedback(suggestionId, feedbackType);
      }
    }

    this.visibleSuggestions.clear();
  }

  /**
   * Renders a suggestion card
   * @param {Object} suggestion The suggestion to render
   * @returns {HTMLElement} The created card element
   * @private
   */
  _renderCard(suggestion) {
    return renderSuggestionCard(
      suggestion,
      this._handleAction.bind(this),
      this._handleDismiss.bind(this),
      { position: this.options.defaultPosition }
    );
  }

  /**
   * Handles a suggestion action being taken
   * @param {Object} suggestion The suggestion that triggered the action
   * @private
   */
  _handleAction(suggestion) {
    this.visibleSuggestions.delete(suggestion.id);

    // Record feedback if available
    if (this.feedbackSystem) {
      this.feedbackSystem.recordAccepted(suggestion.id);
    }

    // Show next queued suggestion if any
    this._showNextQueuedSuggestion();

    // Execute the action
    this._executeSuggestionAction(suggestion);
  }

  /**
   * Handles a suggestion being dismissed
   * @param {Object} suggestion The suggestion that was dismissed
   * @private
   */
  _handleDismiss(suggestion) {
    this.visibleSuggestions.delete(suggestion.id);

    // Record feedback if available
    if (this.feedbackSystem) {
      this.feedbackSystem.recordDismissed(suggestion.id);
    }

    // Show next queued suggestion if any
    this._showNextQueuedSuggestion();
  }

  /**
   * Shows the next queued suggestion
   * @private
   */
  _showNextQueuedSuggestion() {
    if (
      this.suggestionQueue.length > 0 &&
      this.visibleSuggestions.size < this.options.maxVisibleSuggestions
    ) {
      const next = this.suggestionQueue.shift();
      this.presentSuggestion(next.suggestion, next.style);
    }
  }

  /**
   * Execute the action associated with a suggestion
   * @param {Object} suggestion The suggestion with the action to execute
   * @private
   */
  _executeSuggestionAction(suggestion) {
    // This would integrate with your application's action system
    // For now, we'll just log the action
    console.log('Executing suggestion action:', suggestion.action);

    // Example implementation could dispatch a custom event
    const actionEvent = new CustomEvent('suggestion-action', {
      detail: {
        suggestionId: suggestion.id,
        action: suggestion.action,
      },
    });

    window.dispatchEvent(actionEvent);
  }
}

/**
 * Exports
 */
module.exports = {
  SuggestionPresenter,
  renderSuggestionCard,
  COMPONENT_TYPES,
  ANIMATION_TYPES,
  THEMES,
};
