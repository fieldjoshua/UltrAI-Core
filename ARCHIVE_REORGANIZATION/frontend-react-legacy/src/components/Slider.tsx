import React, { useRef, useState } from 'react';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { cn } from '../utils/cn';

interface SliderProps {
  id: string;
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  ariaDescribedBy?: string;
}

export const Slider: React.FC<SliderProps> = ({
  id,
  label,
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  ariaDescribedBy,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef<HTMLDivElement>(null);
  const thumbRef = useRef<HTMLDivElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    const stepValue = step || 1;
    let newValue = value;

    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowUp':
        e.preventDefault();
        newValue = Math.min(value + stepValue, max);
        break;
      case 'ArrowLeft':
      case 'ArrowDown':
        e.preventDefault();
        newValue = Math.max(value - stepValue, min);
        break;
      case 'Home':
        e.preventDefault();
        newValue = min;
        break;
      case 'End':
        e.preventDefault();
        newValue = max;
        break;
    }

    if (newValue !== value) {
      onChange(newValue);
      screenReader.announce(`${label}: ${newValue}`, 'polite');
    }
  };

  useKeyboardNavigation({
    onArrowRight: () => {
      if (!disabled) {
        const newValue = Math.min(value + (step || 1), max);
        onChange(newValue);
        screenReader.announce(`${label}: ${newValue}`, 'polite');
      }
    },
    onArrowLeft: () => {
      if (!disabled) {
        const newValue = Math.max(value - (step || 1), min);
        onChange(newValue);
        screenReader.announce(`${label}: ${newValue}`, 'polite');
      }
    },
    onHome: () => {
      if (!disabled) {
        onChange(min);
        screenReader.announce(`${label}: ${min}`, 'polite');
      }
    },
    onEnd: () => {
      if (!disabled) {
        onChange(max);
        screenReader.announce(`${label}: ${max}`, 'polite');
      }
    },
  });

  const handleMouseDown = () => {
    if (disabled) return;
    setIsDragging(true);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !sliderRef.current) return;

    const rect = sliderRef.current.getBoundingClientRect();
    const percentage = (e.clientX - rect.left) / rect.width;
    const newValue = Math.round(min + percentage * (max - min));
    const steppedValue = Math.round(newValue / (step || 1)) * (step || 1);
    const clampedValue = Math.min(Math.max(steppedValue, min), max);

    if (clampedValue !== value) {
      onChange(clampedValue);
      screenReader.announce(`${label}: ${clampedValue}`, 'polite');
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  const handleTouchStart = () => {
    if (disabled) return;
    setIsDragging(true);
    document.addEventListener('touchmove', handleTouchMove);
    document.addEventListener('touchend', handleTouchEnd);
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!isDragging || !sliderRef.current) return;

    const rect = sliderRef.current.getBoundingClientRect();
    const touch = e.touches[0];
    const percentage = (touch.clientX - rect.left) / rect.width;
    const newValue = Math.round(min + percentage * (max - min));
    const steppedValue = Math.round(newValue / (step || 1)) * (step || 1);
    const clampedValue = Math.min(Math.max(steppedValue, min), max);

    if (clampedValue !== value) {
      onChange(clampedValue);
      screenReader.announce(`${label}: ${clampedValue}`, 'polite');
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    document.removeEventListener('touchmove', handleTouchMove);
    document.removeEventListener('touchend', handleTouchEnd);
  };

  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="w-full">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {label}
      </label>
      <div
        ref={sliderRef}
        role="slider"
        tabIndex={0}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={String(value)}
        aria-disabled={disabled ? 'true' : 'false'}
        aria-label={label}
        aria-describedby={ariaDescribedBy}
        onKeyDown={handleKeyDown}
        className={cn(
          'relative flex h-2 w-full touch-none select-none items-center',
          disabled && 'cursor-not-allowed opacity-50'
        )}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
      >
        <div
          className="absolute h-full bg-blue-600 rounded-full"
          style={{ width: `${percentage}%` }}
        />
        <div
          ref={thumbRef}
          className={`absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-sm border border-gray-300 ${
            disabled ? 'cursor-not-allowed' : 'cursor-grab'
          } ${isDragging ? 'cursor-grabbing' : ''}`}
          style={{ left: `${percentage}%`, transform: 'translate(-50%, -50%)' }}
        />
      </div>
      <div className="flex justify-between mt-1 text-sm text-gray-500">
        <span>{min}</span>
        <span>{value}</span>
        <span>{max}</span>
      </div>
    </div>
  );
};
