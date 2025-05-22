import React from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  ariaLabel?: string;
  ariaDescribedBy?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  ariaLabel = 'Pagination',
  ariaDescribedBy,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent, page: number) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onPageChange(page);
      screenReader.announce(`Page ${page}`, 'polite');
    }
  };

  useKeyboardNavigation({
    onArrowLeft: () => {
      if (currentPage > 1) {
        onPageChange(currentPage - 1);
        screenReader.announce(`Page ${currentPage - 1}`, 'polite');
      }
    },
    onArrowRight: () => {
      if (currentPage < totalPages) {
        onPageChange(currentPage + 1);
        screenReader.announce(`Page ${currentPage + 1}`, 'polite');
      }
    },
    onHome: () => {
      if (currentPage !== 1) {
        onPageChange(1);
        screenReader.announce('First page', 'polite');
      }
    },
    onEnd: () => {
      if (currentPage !== totalPages) {
        onPageChange(totalPages);
        screenReader.announce(`Last page: ${totalPages}`, 'polite');
      }
    },
  });

  const renderPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    const halfVisiblePages = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - halfVisiblePages);
    const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    if (startPage > 1) {
      pages.push(
        <li key="first">
          <button
            onClick={() => onPageChange(1)}
            onKeyDown={e => handleKeyDown(e, 1)}
            className="px-3 py-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="First page"
          >
            1
          </button>
        </li>
      );
      if (startPage > 2) {
        pages.push(
          <li key="start-ellipsis" className="px-2">
            ...
          </li>
        );
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <li key={i}>
          <button
            onClick={() => onPageChange(i)}
            onKeyDown={e => handleKeyDown(e, i)}
            className={`px-3 py-1 rounded-md ${
              i === currentPage
                ? 'bg-blue-600 text-white'
                : 'hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
            }`}
            aria-current={i === currentPage ? 'page' : undefined}
            aria-label={`Page ${i}`}
          >
            {i}
          </button>
        </li>
      );
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(
          <li key="end-ellipsis" className="px-2">
            ...
          </li>
        );
      }
      pages.push(
        <li key="last">
          <button
            onClick={() => onPageChange(totalPages)}
            onKeyDown={e => handleKeyDown(e, totalPages)}
            className="px-3 py-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label="Last page"
          >
            {totalPages}
          </button>
        </li>
      );
    }

    return pages;
  };

  return (
    <nav
      role="navigation"
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      className="flex items-center justify-center space-x-2"
    >
      <button
        onClick={() => onPageChange(currentPage - 1)}
        onKeyDown={e => handleKeyDown(e, currentPage - 1)}
        disabled={currentPage === 1}
        className="px-3 py-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Previous page"
      >
        ←
      </button>
      <ul role="list" className="flex items-center space-x-1">
        {renderPageNumbers()}
      </ul>
      <button
        onClick={() => onPageChange(currentPage + 1)}
        onKeyDown={e => handleKeyDown(e, currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-3 py-1 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Next page"
      >
        →
      </button>
    </nav>
  );
};
