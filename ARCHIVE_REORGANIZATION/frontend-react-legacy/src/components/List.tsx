import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface ListItem {
  id: string;
  content: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}

interface ListProps {
  items: ListItem[];
  type?: 'ordered' | 'unordered';
  ariaLabel?: string;
  ariaDescribedBy?: string;
}

export const List: React.FC<ListProps> = ({
  items,
  type = 'unordered',
  ariaLabel,
  ariaDescribedBy,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent, item: ListItem) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!item.disabled) {
        item.onClick?.();
      }
    }
  };

  const ListComponent = type === 'ordered' ? 'ol' : 'ul';
  const listRole = type === 'ordered' ? 'list' : 'list';

  return (
    <ListComponent
      role={listRole}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      className={`space-y-2 ${
        type === 'ordered' ? 'list-decimal pl-5' : 'list-disc pl-5'
      }`}
    >
      {items.map(item => (
        <li
          key={item.id}
          role="listitem"
          tabIndex={item.onClick ? 0 : undefined}
          onKeyDown={e => handleKeyDown(e, item)}
          onClick={() => {
            if (!item.disabled) {
              item.onClick?.();
            }
          }}
          className={`${
            item.onClick
              ? 'cursor-pointer hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
              : ''
          } ${item.disabled ? 'cursor-not-allowed opacity-50' : ''}`}
        >
          {item.content}
        </li>
      ))}
    </ListComponent>
  );
};
