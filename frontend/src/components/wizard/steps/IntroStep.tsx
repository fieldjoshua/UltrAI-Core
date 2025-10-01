import React from 'react';

interface IntroStepProps {
  onEnter: () => void;
}

export default function IntroStep({ onEnter }: IntroStepProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center px-8">
      <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
        Welcome to UltrAI
      </h1>
      <p className="text-xl mb-8 text-gray-300 max-w-2xl">
        Intelligence Multiplication Platform
      </p>
      <p className="text-base mb-12 text-gray-400 max-w-xl">
        Get better AI answers by combining multiple AI models. Pay only for what you use—many queries cost under $1. No subscriptions. No commitments. Just smarter results.
      </p>
      <button
        onClick={onEnter}
        className="px-12 py-4 text-xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg transition-all transform hover:scale-105"
      >
        Enter UltrAI →
      </button>
    </div>
  );
}
