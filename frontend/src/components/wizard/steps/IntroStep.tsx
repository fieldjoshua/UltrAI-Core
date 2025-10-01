import React from 'react';
import { Button } from '../../ui/Button';

interface IntroStepProps {
  onEnter: () => void;
}

export function IntroStep({ onEnter }: IntroStepProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center space-y-8">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold text-white mb-4">
          Welcome to <span className="text-cyan-400">UltrAI</span>
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl">
          Experience the next evolution of AI-powered analysis. Our advanced orchestration
          system combines multiple AI models to deliver unparalleled insights and accuracy.
        </p>
      </div>

      <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700 max-w-lg">
        <h2 className="text-lg font-semibold text-white mb-3">What you'll get:</h2>
        <ul className="text-gray-300 space-y-2 text-left">
          <li>• Multi-model analysis for comprehensive results</li>
          <li>• Advanced reasoning and pattern recognition</li>
          <li>• Customizable analysis modes and add-ons</li>
          <li>• Real-time progress tracking and results</li>
        </ul>
      </div>

      <Button
        onClick={onEnter}
        className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-200 transform hover:scale-105"
      >
        Enter UltrAI
      </Button>
    </div>
  );
}