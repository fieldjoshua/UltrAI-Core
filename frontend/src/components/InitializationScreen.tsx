import React, { useEffect, useState } from 'react';
import { CheckCircle, Circle, AlertCircle, Loader2, Zap, Database, Key, Shield, Globe, Server, Brain, Cpu } from 'lucide-react';
import { useInitialization } from '../hooks/useInitialization';

interface InitializationScreenProps {
  onComplete: () => void;
}

export const InitializationScreen: React.FC<InitializationScreenProps> = ({ onComplete }) => {
  const { status, isComplete } = useInitialization();
  
  // Map step IDs to icons
  const stepIcons: Record<string, React.ReactNode> = {
    env: <Key className="w-5 h-5" />,
    models: <Brain className="w-5 h-5" />,
    cache: <Database className="w-5 h-5" />,
    auth: <Shield className="w-5 h-5" />,
    orchestrator: <Cpu className="w-5 h-5" />,
    health: <Server className="w-5 h-5" />
  };

  useEffect(() => {
    if (isComplete) {
      onComplete();
    }
  }, [isComplete, onComplete]);

  const getStatusIcon = (status: 'pending' | 'loading' | 'success' | 'error') => {
    switch (status) {
      case 'pending':
        return <Circle className="w-5 h-5 text-gray-400" />;
      case 'loading':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStepClasses = (status: InitStep['status'], index: number) => {
    const baseClasses = "flex items-start space-x-4 p-4 rounded-lg transition-all duration-300";
    
    if (status === 'loading') {
      return `${baseClasses} bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800`;
    }
    if (status === 'success') {
      return `${baseClasses} bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800`;
    }
    if (status === 'error') {
      return `${baseClasses} bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800`;
    }
    if (index === currentStep + 1) {
      return `${baseClasses} bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700`;
    }
    return `${baseClasses} opacity-60`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950 p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 blur-xl opacity-50 animate-pulse"></div>
              <Zap className="w-16 h-16 text-blue-600 dark:text-blue-400 relative z-10" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Initializing UltraAI Core
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Setting up AI models and system components...
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="text-center mt-2 text-sm text-gray-600 dark:text-gray-400">
            {Math.round(progress)}% Complete
          </div>
        </div>

        {/* Initialization Steps */}
        <div className="space-y-3 mb-8">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={getStepClasses(step.status, index)}
            >
              {/* Icon */}
              <div className="flex-shrink-0">
                <div className="relative">
                  <div className={`absolute inset-0 ${step.status === 'loading' ? 'animate-ping' : ''}`}>
                    {step.status === 'loading' && (
                      <div className="w-9 h-9 bg-blue-500 rounded-full opacity-30"></div>
                    )}
                  </div>
                  <div className="relative bg-white dark:bg-gray-800 rounded-full p-2 shadow-sm">
                    {step.icon}
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="flex-grow">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                    {step.name}
                  </h3>
                  {getStatusIcon(step.status)}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {step.description}
                </p>
                {step.error && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                    {step.error}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Status Message */}
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {currentStep < steps.length - 1 ? (
              <>Initializing <span className="font-semibold">{steps[currentStep]?.name}</span>...</>
            ) : (
              <span className="text-green-600 dark:text-green-400 font-semibold">
                All systems ready! Launching UltraAI...
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};