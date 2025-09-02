import React from 'react';
import AnimatedLogoV3 from '@components/branding/AnimatedLogoV3'; // Adjust path if needed
import { Brain, Lightbulb, FileText } from 'lucide-react';

const IntroStep: React.FC = () => {
  return (
    <div className="space-y-6 py-6 fadeIn">
      <div className="text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500 mb-4">
          UltrAI
        </h1>
        <div className="w-16 h-1 bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500 mx-auto mb-6"></div>
      </div>

      <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
        <div className="relative z-10">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">
              1
            </div>
            <h2 className="text-2xl font-bold text-cyan-400">
              Welcome to UltrAI
            </h2>
          </div>
          <p className="text-lg text-cyan-100 mb-4">
            Ultra multiplies intelligence by analyzing your prompt with multiple
            AI models simultaneously, then synthesizing the insights into a
            comprehensive response.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
              <Brain className="w-8 h-8 text-blue-500 mb-2 mx-auto" />
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">
                Multiple Models
              </h3>
            </div>

            <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
              <Lightbulb className="w-8 h-8 text-purple-500 mb-2 mx-auto" />
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">
                Enhanced Analysis
              </h3>
            </div>

            <div className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
              <FileText className="w-8 h-8 text-green-500 mb-2 mx-auto" />
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-1">
                Document Context
              </h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntroStep;
