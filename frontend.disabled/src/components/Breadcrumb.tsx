import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface BreadcrumbItem {
  label: string;
  href?: string;
  onClick?: () => void;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  ariaLabel?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = '/',
  ariaLabel = 'Breadcrumb navigation',
}) => {
  React.useEffect(() => {
    const path = items.map(item => item.label).join(' > ');
    screenReader.announce(`Current location: ${path}`, 'polite');
  }, [items]);

  return (
    <nav
      role="navigation"
      aria-label={ariaLabel}
      className="flex items-center space-x-2 text-sm"
    >
      <ol role="list" className="flex items-center space-x-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-center">
            {index > 0 && (
              <span className="mx-2 text-gray-400" aria-hidden="true">
                {separator}
              </span>
            )}
            {index === items.length - 1 ? (
              <span className="text-gray-500" aria-current="page">
                {item.label}
              </span>
            ) : item.href ? (
              <a
                href={item.href}
                className="text-blue-600 hover:text-blue-800"
                aria-label={`Go to ${item.label}`}
              >
                {item.label}
              </a>
            ) : item.onClick ? (
              <button
                onClick={item.onClick}
                className="text-blue-600 hover:text-blue-800"
                aria-label={`Go to ${item.label}`}
              >
                {item.label}
              </button>
            ) : (
              <span className="text-gray-500">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};
