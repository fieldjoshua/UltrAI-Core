import React, { useEffect, useRef } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const sizeClasses = {
    small: 'max-w-sm',
    medium: 'max-w-md',
    large: 'max-w-lg',
  };

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      screenReader.announce(`${title} dialog opened`, 'polite');
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
      screenReader.announce('Dialog closed', 'polite');
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, title]);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const cleanup = focusManagement.trapFocus(modalRef.current);
      return cleanup;
    }
  }, [isOpen]);

  useKeyboardNavigation({
    onEscape: () => {
      if (isOpen) {
        onClose();
      }
    },
  });

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      className="fixed inset-0 z-50 overflow-y-auto"
    >
      <div className="flex min-h-screen items-center justify-center p-4">
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        <div
          ref={modalRef}
          className={`relative bg-white rounded-lg shadow-xl ${sizeClasses[size]} w-full`}
        >
          <div className="flex items-center justify-between p-4 border-b">
            <h2 id="modal-title" className="text-lg font-semibold">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              aria-label="Close dialog"
            >
              <span aria-hidden="true">×</span>
            </button>
          </div>
          <div className="p-4">{children}</div>
        </div>
      </div>
    </div>
  );
};
