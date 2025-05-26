import React, { useState, useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
  disabled?: boolean;
}

interface TabsProps {
  items: TabItem[];
  defaultTab?: string;
  onChange?: (tabId: string) => void;
}

export const Tabs: React.FC<TabsProps> = ({ items, defaultTab, onChange }) => {
  const [activeTab, setActiveTab] = useState(defaultTab || items[0]?.id);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const tabsRef = useRef<HTMLDivElement>(null);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    onChange?.(tabId);
    screenReader.announce(
      `Switched to ${items.find(item => item.id === tabId)?.label} tab`,
      'polite'
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowRight':
        e.preventDefault();
        const nextIndex = Math.min(index + 1, items.length - 1);
        if (!items[nextIndex].disabled) {
          setFocusedIndex(nextIndex);
          handleTabChange(items[nextIndex].id);
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        const prevIndex = Math.max(index - 1, 0);
        if (!items[prevIndex].disabled) {
          setFocusedIndex(prevIndex);
          handleTabChange(items[prevIndex].id);
        }
        break;
      case 'Home':
        e.preventDefault();
        if (!items[0].disabled) {
          setFocusedIndex(0);
          handleTabChange(items[0].id);
        }
        break;
      case 'End':
        e.preventDefault();
        if (!items[items.length - 1].disabled) {
          setFocusedIndex(items.length - 1);
          handleTabChange(items[items.length - 1].id);
        }
        break;
    }
  };

  useKeyboardNavigation({
    onArrowRight: () => {
      if (focusedIndex < items.length - 1) {
        const nextIndex = focusedIndex + 1;
        if (!items[nextIndex].disabled) {
          setFocusedIndex(nextIndex);
          handleTabChange(items[nextIndex].id);
        }
      }
    },
    onArrowLeft: () => {
      if (focusedIndex > 0) {
        const prevIndex = focusedIndex - 1;
        if (!items[prevIndex].disabled) {
          setFocusedIndex(prevIndex);
          handleTabChange(items[prevIndex].id);
        }
      }
    },
    onHome: () => {
      if (!items[0].disabled) {
        setFocusedIndex(0);
        handleTabChange(items[0].id);
      }
    },
    onEnd: () => {
      if (!items[items.length - 1].disabled) {
        setFocusedIndex(items.length - 1);
        handleTabChange(items[items.length - 1].id);
      }
    },
  });

  return (
    <div className="w-full">
      <div
        ref={tabsRef}
        role="tablist"
        aria-label="Tabs"
        className="flex border-b border-gray-200"
      >
        {items.map((item, index) => (
          <button
            key={item.id}
            role="tab"
            tabIndex={activeTab === item.id ? 0 : -1}
            aria-selected={activeTab === item.id}
            aria-controls={`panel-${item.id}`}
            onKeyDown={e => handleKeyDown(e, index)}
            onClick={() => {
              if (!item.disabled) {
                setFocusedIndex(index);
                handleTabChange(item.id);
              }
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 ${
              activeTab === item.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } ${
              item.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
            } ${
              focusedIndex === index ? 'ring-2 ring-blue-500 ring-offset-2' : ''
            }`}
            disabled={item.disabled}
          >
            {item.label}
          </button>
        ))}
      </div>
      {items.map(item => (
        <div
          key={item.id}
          role="tabpanel"
          id={`panel-${item.id}`}
          aria-labelledby={`tab-${item.id}`}
          hidden={activeTab !== item.id}
          className="p-4"
        >
          {item.content}
        </div>
      ))}
    </div>
  );
};
