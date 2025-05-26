// ARIA role constants
export const ARIA_ROLES = {
  ALERT: 'alert',
  ALERTDIALOG: 'alertdialog',
  BUTTON: 'button',
  CHECKBOX: 'checkbox',
  DIALOG: 'dialog',
  GRID: 'grid',
  LINK: 'link',
  LISTBOX: 'listbox',
  MENU: 'menu',
  MENUITEM: 'menuitem',
  PROGRESSBAR: 'progressbar',
  RADIO: 'radio',
  RADIOGROUP: 'radiogroup',
  SCROLLBAR: 'scrollbar',
  SLIDER: 'slider',
  SPINBUTTON: 'spinbutton',
  STATUS: 'status',
  TAB: 'tab',
  TABLIST: 'tablist',
  TABPANEL: 'tabpanel',
  TEXTBOX: 'textbox',
  TIMER: 'timer',
  TOOLTIP: 'tooltip',
  TREE: 'tree',
  TREEGRID: 'treegrid',
  TREEGRIDITEM: 'treegriditem',
  TREEITEM: 'treeitem',
} as const;

// ARIA state constants
export const ARIA_STATES = {
  EXPANDED: 'aria-expanded',
  HIDDEN: 'aria-hidden',
  SELECTED: 'aria-selected',
  CHECKED: 'aria-checked',
  DISABLED: 'aria-disabled',
  INVALID: 'aria-invalid',
  PRESSED: 'aria-pressed',
  READONLY: 'aria-readonly',
  REQUIRED: 'aria-required',
} as const;

// Keyboard navigation constants
export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
} as const;

// Focus management utilities
export const focusManagement = {
  // Trap focus within an element
  trapFocus: (element: HTMLElement): (() => void) => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0] as HTMLElement;
    const lastFocusable = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key === KEYBOARD_KEYS.TAB) {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            e.preventDefault();
            lastFocusable.focus();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            e.preventDefault();
            firstFocusable.focus();
          }
        }
      }
    };

    element.addEventListener('keydown', handleTabKey);
    return () => element.removeEventListener('keydown', handleTabKey);
  },

  // Focus first focusable element
  focusFirstElement: (element: HTMLElement): void => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0] as HTMLElement;
    if (firstFocusable) {
      firstFocusable.focus();
    }
  },

  // Focus last focusable element
  focusLastElement: (element: HTMLElement): void => {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const lastFocusable = focusableElements[
      focusableElements.length - 1
    ] as HTMLElement;
    if (lastFocusable) {
      lastFocusable.focus();
    }
  },
};

// Screen reader utilities
export const screenReader = {
  // Announce message to screen readers
  announce: (
    message: string,
    politeness: 'polite' | 'assertive' = 'polite'
  ): void => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', politeness);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.padding = '0';
    announcement.style.margin = '-1px';
    announcement.style.overflow = 'hidden';
    announcement.style.clip = 'rect(0, 0, 0, 0)';
    announcement.style.whiteSpace = 'nowrap';
    announcement.style.border = '0';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  },
};

// Heading hierarchy utilities
export const headingHierarchy = {
  // Get next heading level
  getNextLevel: (currentLevel: number): number => {
    return Math.min(currentLevel + 1, 6);
  },

  // Get previous heading level
  getPreviousLevel: (currentLevel: number): number => {
    return Math.max(currentLevel - 1, 1);
  },

  // Validate heading hierarchy
  validateHierarchy: (headings: HTMLElement[]): boolean => {
    let currentLevel = 0;
    for (const heading of headings) {
      const level = parseInt(heading.tagName[1]);
      if (level > currentLevel + 1) {
        return false;
      }
      currentLevel = level;
    }
    return true;
  },
};
