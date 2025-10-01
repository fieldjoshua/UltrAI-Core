import React from 'react';
import { Button } from '../../Button';

interface IntroStepProps {
  onNext: () => void;
}

export function IntroStep({ onNext }: IntroStepProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center space-y-6">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-cyber-green mb-4">
          Welcome to CyberWizard
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl leading-relaxed">
          Experience the next generation of AI-powered analysis with our advanced multimodal
          orchestration system. Let's configure your perfect analysis workflow.
        </p>
        <div className="flex justify-center space-x-8 text-sm text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-green rounded-full"></div>
            <span>Multi-Model Analysis</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-blue rounded-full"></div>
            <span>Smart Orchestration</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-cyber-purple rounded-full"></div>
            <span>Real-time Processing</span>
          </div>
        </div>
      </div>

      <div className="pt-8">
        <Button
          onClick={onNext}
          className="px-8 py-4 text-lg font-semibold bg-cyber-green hover:bg-cyber-green/80 text-black transition-all duration-300 transform hover:scale-105"
        >
          Enter CyberWizard
        </Button>
      </div>

      <div className="text-xs text-gray-500 mt-8">
        Press Enter or click the button to continue
      </div>
    </div>
  );
}