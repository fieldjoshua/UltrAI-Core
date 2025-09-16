import React from 'react';
import { cn } from '../../lib/utils';
import { useTheme } from '../../theme/ThemeContext';
import UniversalContainer, { ContainerStyleConfig } from './UniversalContainer';
import { getContainerTheme } from '../../theme/containerThemes';

/**
 * Progress step interface
 */
interface ProgressStep {
  id: string | number;
  label: string;
  isCompleted?: boolean;
  isCurrent?: boolean;
}

/**
 * Props for the ProgressPanel component
 */
interface ProgressPanelProps {
  className?: string;
  steps: ProgressStep[];
  currentStep: string | number;
  summary?: {
    options?: { [key: string]: string | string[] };
    cost?: string | number;
  };
  onSubmit?: () => void;
  isSubmitting?: boolean;
  isSubmitEnabled?: boolean;
  styleConfig?: Partial<ContainerStyleConfig>;
}

/**
 * Secondary Floating Box (Progress Panel) Component
 *
 * A floating HUD-like panel that shows:
 * - Sequential numbered progress steps
 * - Selected options summary
 * - Estimated cost
 * - Submit button
 *
 * The panel is designed to appear detached with drone attachments for a futuristic look
 */
const ProgressPanel: React.FC<ProgressPanelProps> = ({
  className = '',
  steps,
  currentStep,
  summary = { options: {}, cost: '$0.00' },
  onSubmit,
  isSubmitting = false,
  isSubmitEnabled = true,
  styleConfig = {},
}) => {
  const { theme } = useTheme();

  // Determine the container theme based on current theme style
  const themeStyle =
    theme.style === 'corporate'
      ? 'corporate'
      : theme.style === 'classic'
        ? 'corporate' // Fallback for classic
        : 'cyberpunk';

  // Get the container theme and merge with custom styleConfig
  const containerStyle = {
    ...getContainerTheme(themeStyle, 'progress'),
    ...styleConfig,
    // Ensure drones are enabled for cyberpunk style
    decorativeElements: {
      ...getContainerTheme(themeStyle, 'progress').decorativeElements,
      ...(theme.style === 'cyberpunk' ? { drones: true } : {}),
      ...styleConfig.decorativeElements,
    },
  };

  return (
    <UniversalContainer
      variant="progress"
      size="sm"
      styleConfig={containerStyle}
      isFloating={true}
      animationLevel="moderate"
      className={cn('w-full max-w-xs', className)}
    >
      {/* Progress Steps */}
      <div className="w-full mb-4">
        <div className="relative">
          {/* Progress Bar Background */}
          <div className="h-1 bg-muted/40 rounded-full w-full absolute top-4" />

          {/* Progress Bar Fill */}
          <div
            className={cn(
              'h-1 bg-primary rounded-full absolute top-4 transition-all duration-500',
              theme.style === 'cyberpunk' && 'animate-pulse'
            )}
            style={{
              width: `${(steps.findIndex(s => s.id === currentStep) / (steps.length - 1)) * 100}%`,
            }}
          />

          {/* Step Indicators */}
          <div className="flex justify-between relative">
            {steps.map((step, index) => {
              const isCurrent = step.id === currentStep;
              const isCompleted =
                steps.findIndex(s => s.id === currentStep) > index;

              return (
                <div key={step.id} className="flex flex-col items-center">
                  <div
                    className={cn(
                      'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium z-10',
                      'border-2 transition-all duration-300',
                      isCurrent
                        ? 'border-primary bg-background text-primary'
                        : isCompleted
                          ? 'border-primary bg-primary text-primary-foreground'
                          : 'border-muted bg-muted/30 text-muted-foreground'
                    )}
                  >
                    {index + 1}
                  </div>
                  <span
                    className={cn(
                      'text-xs mt-1 text-center max-w-[60px] transition-colors',
                      isCurrent
                        ? 'text-primary font-medium'
                        : isCompleted
                          ? 'text-primary/70'
                          : 'text-muted-foreground'
                    )}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Summary */}
      {Object.keys(summary.options || {}).length > 0 && (
        <div className="bg-background/30 backdrop-blur-sm rounded-md p-3 mb-4 text-sm">
          <h4 className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
            Selected Options
          </h4>
          <dl className="space-y-1">
            {Object.entries(summary.options || {}).map(([key, value]) => (
              <div key={key} className="grid grid-cols-[1fr,2fr] gap-2">
                <dt className="text-muted-foreground">{key}:</dt>
                <dd className="text-foreground">
                  {Array.isArray(value) ? value.join(', ') : value.toString()}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Cost and Submit */}
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-xs uppercase tracking-wider text-muted-foreground">
            Estimated Cost
          </h4>
          <p
            className={cn(
              'text-lg font-medium',
              theme.style === 'cyberpunk' && 'text-primary'
            )}
          >
            {typeof summary.cost === 'number'
              ? `$${summary.cost.toFixed(2)}`
              : summary.cost}
          </p>
        </div>

        <button
          onClick={onSubmit}
          disabled={!isSubmitEnabled || isSubmitting}
          className={cn(
            'px-4 py-2 rounded-md font-medium',
            'transition-all duration-300',
            isSubmitEnabled && !isSubmitting
              ? 'bg-gradient-to-r from-primary to-primary-light text-primary-foreground'
              : 'bg-muted text-muted-foreground cursor-not-allowed opacity-70',
            theme.style === 'cyberpunk' &&
              isSubmitEnabled &&
              !isSubmitting &&
              'shadow-glow-md'
          )}
        >
          {isSubmitting ? 'Processing...' : 'Submit'}
        </button>
      </div>
    </UniversalContainer>
  );
};

export default ProgressPanel;
