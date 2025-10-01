import React from 'react';
import { ArrowRight, Sparkles, Zap, Target, Gem, Film } from 'lucide-react';

export interface IntroScreenProps {
  onEnter: () => void;
  isDemoMode?: boolean;
  showDemoButton?: boolean;
}

export default function IntroScreen({
  onEnter,
  isDemoMode = false,
  showDemoButton = false,
}: IntroScreenProps) {
  const features = [
    { icon: <Sparkles className="w-4 h-4" />, text: 'Multi-Model Orchestration' },
    { icon: <Zap className="w-4 h-4" />, text: 'Real-time Synthesis' },
    { icon: <Target className="w-4 h-4" />, text: 'Intelligent Optimization' },
    { icon: <Gem className="w-4 h-4" />, text: 'Premium Results' },
  ];

  const trustIndicators = [
    { icon: '✓', text: '20+ AI Models' },
    { icon: '✓', text: 'Enterprise Ready' },
    { icon: '✓', text: 'SOC2 Compliant' },
  ];

  return (
    <div className="flex items-center justify-center min-h-screen w-full p-6">
      <div className="relative z-10 w-full max-w-4xl mx-auto">
        <div className="text-center space-y-8">
          {/* Logo/Title */}
          <div className="mb-8">
            <h1
              className="text-7xl md:text-8xl font-black tracking-tight"
              style={{
                background: 'linear-gradient(135deg, #ff6600 0%, #00ff9f 33%, #00d4ff 66%, #bd00ff 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              UltrAI
            </h1>
          </div>

          {/* Main content card */}
          <div className="bg-gray-900/80 backdrop-blur-xl border-2 border-purple-500/30 rounded-3xl p-12 shadow-2xl">
            {/* Feature pills */}
            <div className="flex flex-wrap gap-3 justify-center mb-8">
              {features.map((feature, i) => (
                <span
                  key={i}
                  className="px-4 py-2 rounded-full text-sm font-semibold bg-purple-500/20 border border-purple-500/30 text-purple-300 flex items-center gap-2"
                >
                  {feature.icon}
                  {feature.text}
                </span>
              ))}
            </div>

            {/* Tagline */}
            <div className="max-w-2xl mx-auto mb-8">
              <p className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-4">
                Intelligence Multiplication Platform
              </p>
              <p className="text-lg text-gray-300 leading-relaxed">
                Query multiple premium AI models simultaneously. Get synthesized insights that no single
                model could provide. <span className="font-bold text-white">Pay only for what you use</span>.
              </p>
              <div className="flex justify-center gap-6 text-sm mt-6 text-gray-400">
                <span>Pay-as-you-go</span>
                <span>•</span>
                <span>No commitments</span>
                <span>•</span>
                <span>Enterprise-grade</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col items-center gap-4">
              <button
                onClick={onEnter}
                className="group relative px-12 py-5 text-xl font-bold rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-purple-500/50"
                aria-label="Start using UltrAI"
              >
                <span className="flex items-center gap-3">
                  <span>Enter UltrAI</span>
                  <ArrowRight className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" />
                </span>
              </button>

              {showDemoButton && (
                <button
                  onClick={onEnter}
                  className="px-8 py-3 text-sm font-semibold rounded-lg border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 transition-all duration-200"
                  aria-label="Try demo mode"
                >
                  <span className="flex items-center gap-2">
                    <Film className="w-4 h-4" />
                    <span>Try Demo</span>
                  </span>
                </button>
              )}
            </div>

            {/* Trust indicators */}
            <div className="flex justify-center gap-8 text-sm text-gray-400 mt-8">
              {trustIndicators.map((indicator, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-green-400">{indicator.icon}</span>
                  <span>{indicator.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
