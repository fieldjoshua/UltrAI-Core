import React, { useState, useRef } from 'react';
import { Paperclip, ArrowRight, Settings } from 'lucide-react';
import UniversalContainer, { ContainerStyleConfig } from './UniversalContainer';
import { cn } from '../../lib/utils';
import { useTheme } from '../../theme/ThemeContext';
import { getContainerTheme } from '../../theme/containerThemes';

/**
 * Props for the PrimaryUIPanel component
 */
interface PrimaryUIPanelProps {
  className?: string;
  onSubmit?: (value: string, attachments: File[]) => void;
  onNext?: (autoConfig?: boolean) => void;
  placeholder?: string;
  styleConfig?: Partial<ContainerStyleConfig>;
  initialValue?: string;
  maxAttachments?: number;
  isFloating?: boolean;
  showNextButtons?: boolean;
  renderAdditionalControls?: () => React.ReactNode;
}

/**
 * Primary UI Panel (Functional Box) Component
 *
 * A semi-transparent, sleek UI panel that contains:
 * - Text entry for query input
 * - Attachments toggle section
 * - Next step buttons for guided workflow
 */
const PrimaryUIPanel: React.FC<PrimaryUIPanelProps> = ({
  className = '',
  onSubmit,
  onNext,
  placeholder = 'OK, what do you want to accomplish?',
  styleConfig = {},
  initialValue = '',
  maxAttachments = 5,
  isFloating = true,
  showNextButtons = true,
  renderAdditionalControls,
}) => {
  const [prompt, setPrompt] = useState(initialValue);
  const [isAttachmentsOpen, setIsAttachmentsOpen] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
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
    ...getContainerTheme(themeStyle, 'primary'),
    ...styleConfig,
  };

  // Handle submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit && prompt.trim()) {
      onSubmit(prompt, attachments);
    }
  };

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      // Limit to max attachments
      const totalFiles = [...attachments, ...newFiles];
      setAttachments(totalFiles.slice(0, maxAttachments));
    }
  };

  // Remove an attachment
  const removeAttachment = (index: number) => {
    setAttachments((current) => current.filter((_, i) => i !== index));
  };

  // Open file picker
  const openFilePicker = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <UniversalContainer
      variant="primary"
      size="lg"
      styleConfig={containerStyle}
      isFloating={isFloating}
      className={cn(
        'w-full max-w-2xl',
        isFloating && 'translate-y-0 hover:translate-y-[-5px]',
        className
      )}
    >
      <form onSubmit={handleSubmit} className="space-y-4 w-full">
        {/* Textarea for input */}
        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={placeholder}
            rows={4}
            className={cn(
              'w-full p-3 rounded-md bg-background/70 backdrop-blur-sm resize-none',
              'border border-border focus:border-primary focus:ring-1 focus:ring-primary',
              'text-foreground placeholder-muted-foreground',
              'transition-all duration-200 outline-none',
              theme.style === 'cyberpunk' && 'focus:shadow-glow-sm'
            )}
          />
        </div>

        {/* Attachments section */}
        <div className="space-y-2">
          <div
            className={cn(
              'flex items-center gap-2 text-sm cursor-pointer',
              'text-muted-foreground hover:text-foreground transition-colors'
            )}
            onClick={() => setIsAttachmentsOpen(!isAttachmentsOpen)}
          >
            <Paperclip size={16} />
            <span>
              Attachments {attachments.length > 0 && `(${attachments.length})`}
            </span>
          </div>

          {/* Hidden file input */}
          <input
            type="file"
            multiple
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />

          {/* Attachments area */}
          {isAttachmentsOpen && (
            <div
              className={cn(
                'border border-border rounded-md p-3 space-y-2',
                'bg-background/50 backdrop-blur-sm'
              )}
            >
              {attachments.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
                  <p className="mb-2">No attachments yet</p>
                  <button
                    type="button"
                    onClick={openFilePicker}
                    className={cn(
                      'px-4 py-2 rounded-md text-sm',
                      'bg-primary/10 hover:bg-primary/20',
                      'text-primary transition-colors'
                    )}
                  >
                    Select Files
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex flex-wrap gap-2">
                    {attachments.map((file, index) => (
                      <div
                        key={`${file.name}-${index}`}
                        className={cn(
                          'flex items-center gap-2 px-2 py-1 rounded-md',
                          'bg-background/70 text-xs text-foreground',
                          'border border-border'
                        )}
                      >
                        <span className="truncate max-w-[150px]">
                          {file.name}
                        </span>
                        <button
                          type="button"
                          onClick={() => removeAttachment(index)}
                          className="text-muted-foreground hover:text-destructive transition-colors"
                        >
                          &times;
                        </button>
                      </div>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={openFilePicker}
                    className={cn(
                      'px-2 py-1 rounded-md text-xs',
                      'bg-primary/10 hover:bg-primary/20',
                      'text-primary transition-colors'
                    )}
                  >
                    Add More
                  </button>
                </>
              )}
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex justify-between items-center">
          {/* Left side - additional controls */}
          <div>{renderAdditionalControls && renderAdditionalControls()}</div>

          {/* Right side - next buttons */}
          {showNextButtons && (
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => onNext && onNext(false)}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium',
                  'bg-primary hover:bg-primary/90 text-primary-foreground',
                  'transition-all duration-200',
                  'flex items-center gap-2',
                  theme.style === 'cyberpunk' && 'shadow-glow-sm'
                )}
              >
                <span>NEXT — Choose Models</span>
                <ArrowRight size={16} />
              </button>

              <button
                type="button"
                onClick={() => onNext && onNext(true)}
                className={cn(
                  'px-4 py-2 rounded-md text-sm font-medium',
                  'bg-secondary hover:bg-secondary/90 text-secondary-foreground',
                  'transition-all duration-200',
                  'flex items-center gap-2',
                  theme.style === 'cyberpunk' && 'shadow-glow-sm'
                )}
              >
                <span>NEXT — Auto-configure</span>
                <Settings size={16} />
              </button>
            </div>
          )}
        </div>
      </form>
    </UniversalContainer>
  );
};

export default PrimaryUIPanel;
