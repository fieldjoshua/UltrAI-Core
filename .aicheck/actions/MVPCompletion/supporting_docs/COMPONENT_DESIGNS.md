# MVP Component Designs

This document outlines the key UI components needed for the Ultra MVP, focusing on the core functionality of comparing responses from different LLMs.

## 1. AnalysisResults Component

The `AnalysisResults` component displays the responses from each LLM in a clear, comparable format. It supports side-by-side comparison and highlights differences between models.

```jsx
// frontend/src/components/AnalysisResults.jsx
import React, { useState } from 'react';
import { Card } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Button } from './ui/button';
import { CopyIcon, MaximizeIcon, MinimizeIcon } from 'lucide-react';

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
};

const ModelResponse = ({ modelName, response, isExpanded, onToggleExpand }) => {
  const displayName = modelName.charAt(0).toUpperCase() + modelName.slice(1);

  return (
    <Card className="p-4 mb-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-semibold">{displayName}</h3>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => copyToClipboard(response.content)}
            aria-label={`Copy ${modelName} response`}
          >
            <CopyIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleExpand}
            aria-label={isExpanded ? 'Minimize' : 'Maximize'}
          >
            {isExpanded ? (
              <MinimizeIcon className="h-4 w-4" />
            ) : (
              <MaximizeIcon className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      <div className={`prose max-w-none ${isExpanded ? '' : 'max-h-64 overflow-y-auto'}`}>
        {response.error ? (
          <div className="text-red-500">Error: {response.error}</div>
        ) : (
          <div>{response.content}</div>
        )}
      </div>

      {response.processing_time && (
        <div className="mt-2 text-sm text-gray-500">
          Processing time: {response.processing_time.toFixed(2)}s
        </div>
      )}
    </Card>
  );
};

export const AnalysisResults = ({ results }) => {
  const [viewMode, setViewMode] = useState('tabs');
  const [expandedModels, setExpandedModels] = useState([]);

  const toggleExpand = (modelName) => {
    if (expandedModels.includes(modelName)) {
      setExpandedModels(expandedModels.filter(m => m !== modelName));
    } else {
      setExpandedModels([...expandedModels, modelName]);
    }
  };

  const modelResponses = results?.model_responses || {};
  const ultraResponse = results?.ultra_response || null;
  const modelNames = Object.keys(modelResponses);

  if (!results || modelNames.length === 0) {
    return (
      <div className="text-center p-4">
        No results to display
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Analysis Results</h2>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'tabs' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('tabs')}
          >
            Tabs
          </Button>
          <Button
            variant={viewMode === 'sideBySide' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('sideBySide')}
          >
            Side by Side
          </Button>
        </div>
      </div>

      {viewMode === 'tabs' ? (
        <Tabs defaultValue={modelNames[0]}>
          <TabsList className="mb-4">
            {modelNames.map(model => (
              <TabsTrigger key={model} value={model}>
                {model.charAt(0).toUpperCase() + model.slice(1)}
              </TabsTrigger>
            ))}
            {ultraResponse && (
              <TabsTrigger value="ultra">Ultra Synthesis</TabsTrigger>
            )}
          </TabsList>

          {modelNames.map(model => (
            <TabsContent key={model} value={model}>
              <ModelResponse
                modelName={model}
                response={modelResponses[model]}
                isExpanded={expandedModels.includes(model)}
                onToggleExpand={() => toggleExpand(model)}
              />
            </TabsContent>
          ))}

          {ultraResponse && (
            <TabsContent value="ultra">
              <ModelResponse
                modelName="Ultra Synthesis"
                response={ultraResponse}
                isExpanded={expandedModels.includes('ultra')}
                onToggleExpand={() => toggleExpand('ultra')}
              />
            </TabsContent>
          )}
        </Tabs>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {modelNames.map(model => (
            <ModelResponse
              key={model}
              modelName={model}
              response={modelResponses[model]}
              isExpanded={expandedModels.includes(model)}
              onToggleExpand={() => toggleExpand(model)}
            />
          ))}

          {ultraResponse && (
            <div className="md:col-span-2">
              <ModelResponse
                modelName="Ultra Synthesis"
                response={ultraResponse}
                isExpanded={expandedModels.includes('ultra')}
                onToggleExpand={() => toggleExpand('ultra')}
              />
            </div>
          )}
        </div>
      )}

      {results.total_time && (
        <div className="text-sm text-gray-500 mt-4">
          Total processing time: {results.total_time.toFixed(2)}s
        </div>
      )}
    </div>
  );
};
```

## 2. PromptInput Component

The `PromptInput` component provides a text input area for users to enter their prompts, with basic validation and submission handling.

```jsx
// frontend/src/components/PromptInput.jsx
import React from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';

export const PromptInput = ({
  value,
  onChange,
  onSubmit,
  disabled = false,
  placeholder = "Enter your prompt here...",
  minLength = 3,
  maxLength = 2000,
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim().length >= minLength) {
      onSubmit();
    }
  };

  const characterCount = value.length;
  const isValid = characterCount >= minLength && characterCount <= maxLength;
  const showWarning = characterCount > 0 && !isValid;

  return (
    <Card className="p-4">
      <form onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label
            htmlFor="prompt-input"
            className="text-lg font-medium block"
          >
            Your Prompt
          </label>

          <Textarea
            id="prompt-input"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="min-h-[100px] w-full"
            disabled={disabled}
          />

          <div className="flex justify-between items-center">
            <div className="text-sm">
              {showWarning && (
                <span className="text-red-500">
                  {characterCount < minLength
                    ? `Minimum ${minLength} characters required`
                    : `Maximum ${maxLength} characters allowed`}
                </span>
              )}
              {!showWarning && (
                <span className="text-gray-500">
                  {characterCount}/{maxLength} characters
                </span>
              )}
            </div>

            <Button
              type="submit"
              disabled={disabled || !isValid}
            >
              {disabled ? 'Analyzing...' : 'Analyze'}
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
};
```

## 3. LLMSelector Component

This component allows users to select which LLM models to use for comparison and designate an "Ultra" model for synthesis.

```jsx
// frontend/src/components/LLMSelector.jsx
import React from 'react';
import { Label } from './ui/label';
import { Checkbox } from './ui/checkbox';
import { Card } from './ui/card';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';

export const LLMSelector = ({
  models,
  selectedModels,
  ultraModel,
  onModelChange,
  onUltraChange,
  disabled = false,
}) => {
  return (
    <Card className="p-4">
      <div className="space-y-4">
        <div>
          <Label className="text-lg font-medium block mb-2">
            Select LLM Models to Compare
          </Label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {models.map(model => {
              const isSelected = selectedModels.includes(model.id);

              return (
                <div
                  key={model.id}
                  className={`
                    p-3 rounded-md border cursor-pointer transition-all
                    ${isSelected ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200'}
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                  onClick={() => !disabled && onModelChange(model.id)}
                >
                  <div className="flex items-center gap-2">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={() => !disabled && onModelChange(model.id)}
                      disabled={disabled}
                      id={`model-${model.id}`}
                    />
                    <Label
                      htmlFor={`model-${model.id}`}
                      className="font-medium cursor-pointer"
                    >
                      {model.name}
                    </Label>
                  </div>
                  {model.description && (
                    <p className="text-sm text-gray-500 mt-1 ml-6">
                      {model.description}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {selectedModels.length > 0 && (
          <div>
            <Label className="text-lg font-medium block mb-2">
              Select Ultra Model (for Synthesis)
            </Label>
            <RadioGroup
              value={ultraModel}
              onValueChange={value => !disabled && onUltraChange(value)}
              className="grid grid-cols-1 md:grid-cols-2 gap-2"
            >
              {selectedModels.map(modelId => {
                const model = models.find(m => m.id === modelId);
                if (!model) return null;

                return (
                  <div
                    key={`ultra-${modelId}`}
                    className={`
                      p-3 rounded-md border flex items-center space-x-2
                      ${ultraModel === modelId ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' : 'border-gray-200'}
                      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                    onClick={() => !disabled && onUltraChange(modelId)}
                  >
                    <RadioGroupItem
                      value={modelId}
                      id={`ultra-${modelId}`}
                      disabled={disabled}
                    />
                    <Label
                      htmlFor={`ultra-${modelId}`}
                      className="font-medium cursor-pointer"
                    >
                      {model.name}
                    </Label>
                  </div>
                );
              })}
            </RadioGroup>
          </div>
        )}
      </div>
    </Card>
  );
};
```

## 4. LoadingIndicator Component

A simple loading indicator component to display when requests are in progress.

```jsx
// frontend/src/components/LoadingIndicator.jsx
import React from 'react';

export const LoadingIndicator = ({ message = "Loading..." }) => {
  return (
    <div className="text-center p-6">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent"></div>
      <p className="mt-2 text-gray-700 dark:text-gray-300">{message}</p>
    </div>
  );
};
```

## 5. ErrorDisplay Component

A component to display error messages to users.

```jsx
// frontend/src/components/ErrorDisplay.jsx
import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';

export const ErrorDisplay = ({
  title = "An error occurred",
  message,
  onRetry = null,
}) => {
  return (
    <Alert variant="destructive" className="my-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>
        <div className="mt-2">
          {message}
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 px-3 py-1 bg-red-100 text-red-800 rounded-md hover:bg-red-200 transition-colors"
          >
            Try Again
          </button>
        )}
      </AlertDescription>
    </Alert>
  );
};
```

## 6. MainLayout Component

A layout component to provide consistent structure across pages.

```jsx
// frontend/src/components/MainLayout.jsx
import React from 'react';
import { ThemeToggle } from './ThemeToggle';

export const MainLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Ultra</h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500 dark:text-gray-400">
          Ultra MVP - Multi-LLM Analysis Platform
        </div>
      </footer>
    </div>
  );
};
```

## Component Integration

These components work together to form a complete user interface:

1. The `MainLayout` provides the page structure
2. The `LLMSelector` allows users to select models for comparison
3. The `PromptInput` lets users enter their prompt
4. The `LoadingIndicator` shows while the analysis is in progress
5. The `ErrorDisplay` shows any errors that occur
6. The `AnalysisResults` displays the comparison between model responses

This implementation follows a component-based architecture with clear separation of concerns, making it maintainable and extendable.

## UI Flow

1. User selects models using the `LLMSelector`
2. User enters a prompt in the `PromptInput` and submits
3. `LoadingIndicator` displays while waiting for results
4. `AnalysisResults` shows the comparison when results are received
5. Users can toggle between tab view and side-by-side view
6. Users can expand/collapse individual model responses
7. Users can copy response text to clipboard
