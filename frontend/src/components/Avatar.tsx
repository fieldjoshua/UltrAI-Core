import React from 'react';
import { screenReader } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface AvatarProps {
  src?: string;
  alt: string;
  size?: 'small' | 'medium' | 'large';
  fallback?: string;
  onClick?: () => void;
  status?: 'online' | 'offline' | 'away' | 'busy';
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  alt,
  size = 'medium',
  fallback,
  onClick,
  status,
}) => {
  const sizeClasses = {
    small: 'w-8 h-8 text-xs',
    medium: 'w-10 h-10 text-sm',
    large: 'w-12 h-12 text-base',
  };

  const statusClasses = {
    online: 'bg-green-400',
    offline: 'bg-gray-400',
    away: 'bg-yellow-400',
    busy: 'bg-red-400',
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    e.currentTarget.style.display = 'none';
    const fallbackElement = e.currentTarget.nextElementSibling;
    if (fallbackElement) {
      (fallbackElement as HTMLElement).style.display = 'flex';
    }
  };

  const avatarContent = (
    <>
      {src ? (
        <img
          src={src}
          alt={alt}
          className="w-full h-full object-cover rounded-full"
          onError={handleError}
        />
      ) : null}
      {(!src || fallback) && (
        <div
          className="hidden w-full h-full bg-gray-200 rounded-full items-center justify-center text-gray-600 font-medium"
          aria-hidden="true"
        >
          {fallback ? getInitials(fallback) : getInitials(alt)}
        </div>
      )}
      {status && (
        <span
          className={`absolute bottom-0 right-0 block w-2.5 h-2.5 rounded-full ring-2 ring-white ${statusClasses[status]}`}
          aria-label={`Status: ${status}`}
        />
      )}
    </>
  );

  if (onClick) {
    return (
      <button
        onClick={onClick}
        className={`relative inline-block ${sizeClasses[size]}`}
        aria-label={`View profile for ${alt}`}
      >
        {avatarContent}
      </button>
    );
  }

  return (
    <div
      role="img"
      aria-label={alt}
      className={`relative inline-block ${sizeClasses[size]}`}
    >
      {avatarContent}
    </div>
  );
};
