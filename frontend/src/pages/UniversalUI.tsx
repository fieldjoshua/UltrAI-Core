import React, { useState } from 'react';
import { useTheme } from '../theme/ThemeContext';
import {
  ThemeStylerProvider,
  ThemeStylerPanel,
  useThemeStyler,
} from '../theme/ThemeStyler';
import UniversalContainer from '../components/universal/UniversalContainer';
import PrimaryUIPanel from '../components/universal/PrimaryUIPanel';
import ProgressPanel from '../components/universal/ProgressPanel';
import GuidedChat from '../components/steps/GuidedChat';
import ReceiptPanel from '../components/steps/ReceiptPanel';
import { Settings, Eye } from 'lucide-react';

/**
 * Demo progress steps
 */
const DEMO_STEPS = [
  { id: 'input', label: 'Input' },
  { id: 'models', label: 'Models' },
  { id: 'analyze', label: 'Analyze' },
  { id: 'review', label: 'Review' },
  { id: 'refine', label: 'Refine' },
  { id: 'export', label: 'Export' },
  { id: 'share', label: 'Share' },
];

/**
 * Demo options
 */
const DEMO_OPTIONS = {
  Models: 'gpt-4o, claude-3-opus',
  Pattern: 'Comprehensive Analysis',
  Format: 'Technical Report',
};

/**
 * ThemePreview component
 */
const ThemePreview: React.FC = () => {
  const [activeStep, setActiveStep] = useState<string>('input');
  const [customizing, setCustomizing] = useState<string | null>(null);
  const { theme } = useTheme();
  const { getStyleConfig } = useThemeStyler();

  // Handler for next step
  const handleNext = (autoConfig: boolean = false) => {
    if (activeStep === 'input') {
      setActiveStep('models');
    }
  };

  return (
    <div className="relative min-h-screen">
      {/* Background based on theme */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background:
            theme.style === 'cyberpunk'
              ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
              : theme.style === 'corporate'
                ? 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
                : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        }}
      >
        {/* Cyberpunk theme visual elements */}
        {theme.style === 'cyberpunk' && (
          <>
            {/* Grid lines */}
            <div
              className="absolute inset-0 opacity-10"
              style={{
                backgroundImage:
                  'linear-gradient(rgba(0, 255, 255, 0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.5) 1px, transparent 1px)',
                backgroundSize: '50px 50px',
              }}
            />

            {/* Horizontal light beam */}
            <div className="absolute left-0 right-0 h-32 top-1/3 transform -translate-y-1/2 bg-gradient-to-r from-cyan-500/0 via-cyan-500/30 to-cyan-500/0 blur-xl opacity-30" />

            {/* Building silhouette */}
            <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-black opacity-70" />
          </>
        )}
      </div>

      {/* Main content */}
      <div className="relative z-10 container mx-auto py-12 px-4">
        <div className="flex justify-between items-start mb-12">
          <div>
            <h1 className="text-4xl font-bold mb-4">Universal UI System</h1>
            <p className="text-xl text-muted-foreground max-w-xl">
              Rapidly customizable UI containers with consistent functional
              elements and varied visual styling.
            </p>
          </div>

          {/* Theme preview options */}
          <div className="flex flex-col space-y-4">
            <h2 className="text-lg font-semibold">Customize Containers</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setCustomizing('primary')}
                className="px-3 py-2 bg-primary/10 hover:bg-primary/20 rounded-md flex items-center space-x-2 text-sm"
              >
                <Settings size={16} />
                <span>Primary Panel</span>
              </button>

              <button
                onClick={() => setCustomizing('progress')}
                className="px-3 py-2 bg-primary/10 hover:bg-primary/20 rounded-md flex items-center space-x-2 text-sm"
              >
                <Settings size={16} />
                <span>Progress Panel</span>
              </button>
            </div>
          </div>
        </div>

        {/* Two-box guided UI */}
        <div className="flex flex-col md:flex-row gap-8 items-start mb-24">
          <div className="w-full md:w-2/3">
            <GuidedChat
              onChangeReceipt={(items, cost) => {
                // store to preview panel (below)
              }}
              onLaunch={payload => {
                console.log('Launch UltrAI with:', payload);
              }}
            />
          </div>
          <div className="w-full md:w-1/3">
            <ReceiptPanel items={[{ key: 'Goals', value: '' }]} costCents={0} />
          </div>
        </div>

        {/* Additional Containers Showcase */}
        <h2 className="text-2xl font-bold mb-6">Additional Container Types</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-24">
          {/* Alert Container */}
          <UniversalContainer
            variant="alert"
            size="md"
            styleConfig={getStyleConfig('alert')}
          >
            <div className="flex items-center p-2 space-x-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-yellow-500 flex items-center justify-center text-white">
                !
              </div>
              <div>
                <h3 className="font-medium">Data Processing Complete</h3>
                <p className="text-sm text-muted-foreground">
                  Your analysis is ready to review.
                </p>
              </div>
            </div>
          </UniversalContainer>

          {/* Modal Container */}
          <UniversalContainer
            variant="modal"
            size="md"
            styleConfig={getStyleConfig('modal')}
          >
            <div className="p-2">
              <h3 className="text-lg font-bold mb-2">Confirm Analysis</h3>
              <p className="text-sm text-muted-foreground mb-4">
                You're about to run analysis with the selected models.
              </p>
              <div className="flex justify-end space-x-2">
                <button className="px-3 py-1 text-sm bg-muted rounded-md">
                  Cancel
                </button>
                <button className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md">
                  Confirm
                </button>
              </div>
            </div>
          </UniversalContainer>

          {/* Card Container */}
          <UniversalContainer
            variant="card"
            size="md"
            styleConfig={getStyleConfig('card')}
          >
            <div className="p-2">
              <h3 className="font-medium mb-2">Analysis Result</h3>
              <p className="text-sm text-muted-foreground">
                The analysis found 3 key insights and 2 recommended actions.
              </p>
              <button className="mt-4 flex items-center text-sm text-primary">
                <Eye size={14} className="mr-1" />
                View Details
              </button>
            </div>
          </UniversalContainer>
        </div>

        {/* Customization Panel */}
        {customizing && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-background rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
              <ThemeStylerPanel
                containerType={customizing as any}
                onClose={() => setCustomizing(null)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Universal UI Demo Page
 */
const UniversalUI: React.FC = () => {
  return (
    <ThemeStylerProvider>
      <ThemePreview />
    </ThemeStylerProvider>
  );
};

export default UniversalUI;
