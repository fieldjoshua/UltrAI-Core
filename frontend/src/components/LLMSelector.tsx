import React, { useRef } from 'react';
import { Card } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';

interface LLMOption {
  id: string;
  name: string;
  description: string;
}

interface LLMSelectorProps {
  options: LLMOption[];
  selectedModels: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  disabled?: boolean;
}

export const LLMSelector: React.FC<LLMSelectorProps> = ({
  options,
  selectedModels,
  onSelectionChange,
  disabled = false,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [focusedIndex, setFocusedIndex] = React.useState<number>(-1);

  const handleCheckboxChange = (modelId: string) => {
    const newSelection = selectedModels.includes(modelId)
      ? selectedModels.filter(id => id !== modelId)
      : [...selectedModels, modelId];
    onSelectionChange(newSelection);
    screenReader.announce(
      `${modelId} ${newSelection.includes(modelId) ? 'selected' : 'deselected'}`
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(Math.min(index + 1, options.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(Math.max(index - 1, 0));
        break;
      case ' ':
      case 'Enter':
        e.preventDefault();
        handleCheckboxChange(options[index].id);
        break;
    }
  };

  useKeyboardNavigation({
    onArrowDown: () => {
      if (focusedIndex < options.length - 1) {
        setFocusedIndex(focusedIndex + 1);
      }
    },
    onArrowUp: () => {
      if (focusedIndex > 0) {
        setFocusedIndex(focusedIndex - 1);
      }
    },
    onHome: () => {
      setFocusedIndex(0);
    },
    onEnd: () => {
      setFocusedIndex(options.length - 1);
    },
  });

  React.useEffect(() => {
    if (focusedIndex >= 0 && containerRef.current) {
      const focusableElements = containerRef.current.querySelectorAll(
        'input[type="checkbox"]'
      );
      const element = focusableElements[focusedIndex] as HTMLElement;
      if (element) {
        element.focus();
      }
    }
  }, [focusedIndex]);

  return (
    <Card className="w-full p-4">
      <div
        ref={containerRef}
        role="group"
        aria-label="Select LLMs for Analysis"
        className="space-y-4"
      >
        <h3 className="text-lg font-semibold mb-4">Select LLMs for Analysis</h3>
        <div className="space-y-4">
          {options.map((model, index) => (
            <div
              key={model.id}
              className="flex items-start space-x-3"
              role="presentation"
            >
              <Checkbox
                id={model.id}
                checked={selectedModels.includes(model.id)}
                onCheckedChange={() => handleCheckboxChange(model.id)}
                disabled={disabled}
                onKeyDown={e => handleKeyDown(e, index)}
                aria-label={`Select ${model.name}`}
                aria-describedby={`${model.id}-description`}
              />
              <div className="space-y-1">
                <Label
                  htmlFor={model.id}
                  className="font-medium"
                  id={`${model.id}-label`}
                >
                  {model.name}
                </Label>
                <p
                  id={`${model.id}-description`}
                  className="text-sm text-gray-500"
                >
                  {model.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};
