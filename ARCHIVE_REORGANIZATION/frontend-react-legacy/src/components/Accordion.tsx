import React, { useState, useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface AccordionItem {
  id: string;
  title: string;
  content: React.ReactNode;
  disabled?: boolean;
}

interface AccordionProps {
  items: AccordionItem[];
  defaultOpen?: string[];
  onChange?: (openIds: string[]) => void;
}

export const Accordion: React.FC<AccordionProps> = ({
  items,
  defaultOpen = [],
  onChange,
}) => {
  const [openItems, setOpenItems] = useState<string[]>(defaultOpen);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const accordionRef = useRef<HTMLDivElement>(null);

  const handleToggle = (itemId: string) => {
    const newOpenItems = openItems.includes(itemId)
      ? openItems.filter(id => id !== itemId)
      : [...openItems, itemId];
    setOpenItems(newOpenItems);
    onChange?.(newOpenItems);
    screenReader.announce(
      `${items.find(item => item.id === itemId)?.title} ${
        newOpenItems.includes(itemId) ? 'expanded' : 'collapsed'
      }`,
      'polite'
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        const nextIndex = Math.min(index + 1, items.length - 1);
        if (!items[nextIndex].disabled) {
          setFocusedIndex(nextIndex);
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        const prevIndex = Math.max(index - 1, 0);
        if (!items[prevIndex].disabled) {
          setFocusedIndex(prevIndex);
        }
        break;
      case 'Home':
        e.preventDefault();
        if (!items[0].disabled) {
          setFocusedIndex(0);
        }
        break;
      case 'End':
        e.preventDefault();
        if (!items[items.length - 1].disabled) {
          setFocusedIndex(items.length - 1);
        }
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (!items[index].disabled) {
          handleToggle(items[index].id);
        }
        break;
    }
  };

  useKeyboardNavigation({
    onArrowDown: () => {
      if (focusedIndex < items.length - 1) {
        const nextIndex = focusedIndex + 1;
        if (!items[nextIndex].disabled) {
          setFocusedIndex(nextIndex);
        }
      }
    },
    onArrowUp: () => {
      if (focusedIndex > 0) {
        const prevIndex = focusedIndex - 1;
        if (!items[prevIndex].disabled) {
          setFocusedIndex(prevIndex);
        }
      }
    },
    onHome: () => {
      if (!items[0].disabled) {
        setFocusedIndex(0);
      }
    },
    onEnd: () => {
      if (!items[items.length - 1].disabled) {
        setFocusedIndex(items.length - 1);
      }
    },
  });

  return (
    <div
      ref={accordionRef}
      role="region"
      aria-label="Accordion"
      className="space-y-2"
    >
      {items.map((item, index) => (
        <div key={item.id} className="border border-gray-200 rounded-lg">
          <button
            role="button"
            tabIndex={0}
            onKeyDown={e => handleKeyDown(e, index)}
            onClick={() => {
              if (!item.disabled) {
                setFocusedIndex(index);
                handleToggle(item.id);
              }
            }}
            className={`w-full px-4 py-3 text-left flex justify-between items-center ${
              focusedIndex === index ? 'ring-2 ring-blue-500 ring-offset-2' : ''
            } ${
              item.disabled
                ? 'opacity-50 cursor-not-allowed'
                : 'cursor-pointer hover:bg-gray-50'
            }`}
            disabled={item.disabled}
            aria-expanded={openItems.includes(item.id)}
            aria-controls={`content-${item.id}`}
          >
            <span className="font-medium">{item.title}</span>
            <span
              className={`transform transition-transform ${
                openItems.includes(item.id) ? 'rotate-180' : ''
              }`}
              aria-hidden="true"
            >
              ▼
            </span>
          </button>
          <div
            id={`content-${item.id}`}
            role="region"
            aria-labelledby={`header-${item.id}`}
            className={`px-4 py-3 ${
              openItems.includes(item.id) ? 'block' : 'hidden'
            }`}
          >
            {item.content}
          </div>
        </div>
      ))}
    </div>
  );
};
