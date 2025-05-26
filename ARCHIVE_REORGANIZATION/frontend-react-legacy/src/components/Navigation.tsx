import React, { useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface NavigationItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href: string;
  isActive?: boolean;
}

interface NavigationProps {
  items: NavigationItem[];
  onItemSelect?: (item: NavigationItem) => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  items,
  onItemSelect,
}) => {
  const containerRef = useRef<HTMLElement>(null);
  const [focusedIndex, setFocusedIndex] = React.useState<number>(-1);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        setFocusedIndex(Math.min(index + 1, items.length - 1));
        break;
      case 'ArrowLeft':
        e.preventDefault();
        setFocusedIndex(Math.max(index - 1, 0));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        onItemSelect?.(items[index]);
        break;
    }
  };

  useKeyboardNavigation({
    onArrowRight: () => {
      if (focusedIndex < items.length - 1) {
        setFocusedIndex(focusedIndex + 1);
      }
    },
    onArrowLeft: () => {
      if (focusedIndex > 0) {
        setFocusedIndex(focusedIndex - 1);
      }
    },
    onHome: () => {
      setFocusedIndex(0);
    },
    onEnd: () => {
      setFocusedIndex(items.length - 1);
    },
  });

  React.useEffect(() => {
    if (focusedIndex >= 0 && containerRef.current) {
      const focusableElements =
        containerRef.current.querySelectorAll('[role="menuitem"]');
      const element = focusableElements[focusedIndex] as HTMLElement;
      if (element) {
        element.focus();
        screenReader.announce(
          `Navigation item ${focusedIndex + 1} of ${items.length}: ${
            items[focusedIndex].label
          }`
        );
      }
    }
  }, [focusedIndex, items]);

  return (
    <nav
      ref={containerRef}
      role="navigation"
      aria-label="Main navigation"
      className="bg-white shadow-sm"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-xl font-bold">Ultra</span>
            </div>
            <div
              role="menubar"
              aria-label="Navigation menu"
              className="hidden sm:ml-6 sm:flex sm:space-x-8"
            >
              {items.map((item, index) => (
                <a
                  key={item.id}
                  href={item.href}
                  role="menuitem"
                  tabIndex={0}
                  onKeyDown={e => handleKeyDown(e, index)}
                  onClick={e => {
                    e.preventDefault();
                    onItemSelect?.(item);
                  }}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    item.isActive
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } ${
                    focusedIndex === index
                      ? 'ring-2 ring-blue-500 ring-offset-2'
                      : ''
                  }`}
                  aria-current={item.isActive ? 'page' : undefined}
                >
                  {item.icon && (
                    <span className="mr-2" aria-hidden="true">
                      {item.icon}
                    </span>
                  )}
                  {item.label}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};
