import React, { useRef } from 'react';
import { Card } from './ui/card';
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation';
import { screenReader } from '../utils/accessibility';
import { focusManagement } from '../utils/accessibility';
import { ARIA_ROLES } from '../utils/accessibility';

interface Action {
  id: string;
  name: string;
  status: 'Not Started' | 'ActiveAction' | 'Completed' | 'Blocked' | 'On Hold';
  progress: number;
  description: string;
  lastUpdated: string;
}

interface ActionListProps {
  actions: Action[];
  onActionSelect?: (action: Action) => void;
  onActionStatusChange?: (
    actionId: string,
    newStatus: Action['status']
  ) => void;
}

export const ActionList: React.FC<ActionListProps> = ({
  actions,
  onActionSelect,
  onActionStatusChange,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [focusedIndex, setFocusedIndex] = React.useState<number>(-1);

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(Math.min(index + 1, actions.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(Math.max(index - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        onActionSelect?.(actions[index]);
        break;
    }
  };

  useKeyboardNavigation({
    onArrowDown: () => {
      if (focusedIndex < actions.length - 1) {
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
      setFocusedIndex(actions.length - 1);
    },
  });

  React.useEffect(() => {
    if (focusedIndex >= 0 && containerRef.current) {
      const focusableElements =
        containerRef.current.querySelectorAll('[role="listitem"]');
      const element = focusableElements[focusedIndex] as HTMLElement;
      if (element) {
        element.focus();
        screenReader.announce(
          `Action ${focusedIndex + 1} of ${actions.length}: ${
            actions[focusedIndex].name
          }`
        );
      }
    }
  }, [focusedIndex, actions]);

  const getStatusColor = (status: Action['status']) => {
    switch (status) {
      case 'ActiveAction':
        return 'bg-blue-100 text-blue-800';
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'Blocked':
        return 'bg-red-100 text-red-800';
      case 'On Hold':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="w-full p-4">
      <div
        ref={containerRef}
        role="region"
        aria-label="Action List"
        className="space-y-4"
      >
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div role="list" aria-label="List of actions" className="space-y-4">
          {actions.map((action, index) => (
            <div
              key={action.id}
              role="listitem"
              tabIndex={0}
              onKeyDown={e => handleKeyDown(e, index)}
              onClick={() => onActionSelect?.(action)}
              className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                focusedIndex === index
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
              aria-label={`Action: ${action.name}`}
              aria-describedby={`${action.id}-description`}
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-medium" id={`${action.id}-title`}>
                  {action.name}
                </h3>
                <span
                  className={`px-2 py-1 rounded text-sm ${getStatusColor(
                    action.status
                  )}`}
                  aria-label={`Status: ${action.status}`}
                >
                  {action.status}
                </span>
              </div>
              <p id={`${action.id}-description`} className="text-gray-700 mb-2">
                {action.description}
              </p>
              <div className="flex justify-between items-center">
                <div className="w-full bg-gray-200 rounded-full h-2.5 mr-4">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${action.progress}%` }}
                    role="progressbar"
                    aria-valuenow={action.progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Progress: ${action.progress}%`}
                  />
                </div>
                <time
                  dateTime={action.lastUpdated}
                  className="text-sm text-gray-500"
                >
                  {new Date(action.lastUpdated).toLocaleString()}
                </time>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};
