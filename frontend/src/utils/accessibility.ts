// Shim module to provide a stable accessibility import path
// Re-export ARIA constants and expose a simple screenReader announcer.

export { ARIA_ROLES, ARIA_STATES } from './aria';

type Politeness = 'polite' | 'assertive';

function getOrCreateLiveRegion(politeness: Politeness): HTMLElement {
  const id =
    politeness === 'assertive' ? 'sr-live-assertive' : 'sr-live-polite';
  let region = document.getElementById(id) as HTMLElement | null;
  if (!region) {
    region = document.createElement('div');
    region.id = id;
    region.setAttribute('role', 'status');
    region.setAttribute('aria-live', politeness);
    region.setAttribute('aria-atomic', 'true');
    Object.assign(region.style, {
      position: 'absolute',
      width: '1px',
      height: '1px',
      margin: '-1px',
      border: '0',
      padding: '0',
      overflow: 'hidden',
      clip: 'rect(0 0 0 0)',
      clipPath: 'inset(50%)',
      whiteSpace: 'nowrap',
    } as CSSStyleDeclaration);
    document.body.appendChild(region);
  }
  return region;
}

export const screenReader = {
  announce(message: string, politeness: Politeness = 'polite'): void {
    try {
      const region = getOrCreateLiveRegion(politeness);
      // Clear then set to ensure announcement
      region.textContent = '';
      // Slight delay to allow AT to detect change
      window.setTimeout(() => {
        region!.textContent = message;
      }, 30);
    } catch (_e) {
      // No-op in non-DOM environments
    }
  },
};

/**
 * Accessibility utilities for WCAG compliance
 */

export const a11yLabels = {
  // Navigation
  mainNavigation: 'Main navigation',
  skipToContent: 'Skip to main content',
  closeModal: 'Close modal',

  // Theme
  themeSelector: 'Select visual theme',
  selectTheme: (theme: string) => `Select ${theme} theme`,
  currentTheme: (theme: string) => `Current theme: ${theme}`,

  // Wizard steps
  wizardProgress: 'Analysis wizard progress',
  currentStep: (step: number, total: number) => `Step ${step} of ${total}`,
  goToStep: (step: number) => `Go to step ${step}`,
  nextStep: 'Continue to next step',
  previousStep: 'Go back to previous step',

  // Form elements
  selectGoal: (goal: string) => `Select goal: ${goal}`,
  selectedGoal: (goal: string) => `${goal} goal selected`,
  queryInput: 'Enter your analysis query',
  characterCount: (current: number, max: number) =>
    `${current} of ${max} characters`,

  // Model selection
  selectModel: (model: string) => `Select AI model: ${model}`,
  selectedModel: (model: string) => `${model} model selected`,
  modelStatus: (model: string, status: string) =>
    `${model} model status: ${status}`,
  autoModelSelection: 'Automatic model selection based on your preferences',
  manualModelSelection: 'Manually select AI models',

  // Receipt
  receiptTotal: (amount: string) => `Total cost: ${amount}`,
  receiptItem: (item: string, cost: string) => `${item}: ${cost}`,
  expandReceipt: 'Expand receipt details',
  collapseReceipt: 'Collapse receipt details',

  // Processing
  processingStatus: 'Analysis processing status',
  processingPhase: (phase: string) => `Processing phase: ${phase}`,
  processingComplete: 'Analysis complete',
  viewResults: 'View analysis results',
  startNewAnalysis: 'Start a new analysis',

  // Status indicators
  systemOnline: 'System status: Online',
  systemOffline: 'System status: Offline',
  modelsAvailable: (count: number, total: number) =>
    `${count} of ${total} models available`,
  latency: (time: string) => `Average latency: ${time}`,

  // Actions
  submit: 'Submit for analysis',
  cancel: 'Cancel',
  reset: 'Reset form',
  copy: 'Copy to clipboard',
  download: 'Download results',
  share: 'Share results',

  // Loading states
  loading: 'Loading...',
  loadingStep: (step: string) => `Loading ${step}...`,

  // Errors
  error: 'Error',
  errorMessage: (message: string) => `Error: ${message}`,
  retry: 'Retry',

  // Success
  success: 'Success',
  successMessage: (message: string) => `Success: ${message}`,
};

/**
 * Generate ARIA live region announcement
 */
export const announce = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Screen reader only class for Tailwind
 */
export const srOnly = 'sr-only';

/**
 * Focus management utilities
 */
export const focusManagement = {
  // Trap focus within a container
  trapFocus: (container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    container.addEventListener('keydown', e => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        } else if (!e.shiftKey && document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    });

    firstFocusable?.focus();
  },

  // Return focus to a specific element
  returnFocus: (element: HTMLElement) => {
    element.focus();
  },
};

/**
 * Keyboard navigation helpers
 */
export const keyboardNav = {
  isEnter: (e: KeyboardEvent) => e.key === 'Enter',
  isSpace: (e: KeyboardEvent) => e.key === ' ',
  isEscape: (e: KeyboardEvent) => e.key === 'Escape',
  isArrowUp: (e: KeyboardEvent) => e.key === 'ArrowUp',
  isArrowDown: (e: KeyboardEvent) => e.key === 'ArrowDown',
  isArrowLeft: (e: KeyboardEvent) => e.key === 'ArrowLeft',
  isArrowRight: (e: KeyboardEvent) => e.key === 'ArrowRight',
  isTab: (e: KeyboardEvent) => e.key === 'Tab',
};
