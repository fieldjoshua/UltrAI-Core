import React from 'react';
import { Film } from 'lucide-react';

interface IntroScreenProps {
  isNonTimeSkin: boolean;
  themeBgUrl: string;
  themeBgUrl2x: string;
  glassBackground: string;
  mapColorRGBA: (color: string, alpha: number) => string;
  mapColorHex: (color: string) => string;
  isDemoMode?: boolean;
  onEnter: () => void;
}

export default function IntroScreen({
  isNonTimeSkin,
  themeBgUrl,
  themeBgUrl2x,
  glassBackground,
  mapColorRGBA,
  mapColorHex,
  isDemoMode = false,
  onEnter,
}: IntroScreenProps) {
  return (
    <div className="pointer-events-auto relative flex items-center justify-center min-h-screen w-full">
      {/* Background layer */}
      {!isNonTimeSkin && (
        <div
          className="pointer-events-none fixed inset-0"
          style={{
            backgroundImage: `image-set(url('${themeBgUrl}') 1x, url('${themeBgUrl2x}') 2x)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
      )}

      {/* Main content */}
      <div className="relative z-10 w-full max-w-6xl mx-auto px-6 lg:px-8 animate-fade-in">
        <div className="text-center space-y-8">
          {/* Animated billboard */}
          <div className="mb-12 animate-slide-in-top">
            <div
              className="relative inline-block"
              style={{ animationDelay: '0.2s' }}
            >
              <div
                className="relative px-12 py-6 rounded-lg overflow-hidden animate-pulse-subtle"
                style={{
                  background:
                    'linear-gradient(45deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6))',
                  border: '3px solid transparent',
                  borderImage:
                    'linear-gradient(45deg, #ff6600, #00ff9f, #00d4ff, #bd00ff) 1',
                  boxShadow:
                    '0 0 80px rgba(255,102,0,0.4), inset 0 0 60px rgba(0,255,159,0.1)',
                  animation:
                    'ultrai-billboard-sweep 3s ease-in-out infinite',
                  backgroundSize: '200% 200%',
                }}
              >
                <div className="absolute inset-0 opacity-30">
                  <div
                    className="absolute inset-0"
                    style={{
                      background: `repeating-linear-gradient(
                        90deg,
                        transparent,
                        transparent 10px,
                        rgba(255,255,255,0.03) 10px,
                        rgba(255,255,255,0.03) 20px
                      )`,
                    }}
                  />
                </div>
                <h1
                  className="text-7xl lg:text-8xl font-black tracking-[0.02em] relative z-10"
                  style={{
                    background:
                      'linear-gradient(135deg, #ff6600 0%, #00ff9f 33%, #00d4ff 66%, #bd00ff 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    textShadow: '0 0 80px rgba(255,102,0,0.6)',
                    filter: 'drop-shadow(0 0 30px rgba(0,255,159,0.5))',
                  }}
                >
                  UltrAI
                </h1>
              </div>
              {/* Billboard legs */}
              <div className="absolute -bottom-4 left-4 w-1 h-4 bg-gray-600"></div>
              <div className="absolute -bottom-4 right-4 w-1 h-4 bg-gray-600"></div>
            </div>
          </div>

          {/* Main professional card */}
          <div
            className="glass-panel glass-grain relative p-12 rounded-3xl overflow-hidden animate-scale-in transition-smooth"
            style={{
              background: glassBackground,
              backdropFilter: 'blur(40px)',
              WebkitBackdropFilter: 'blur(40px)',
              border: '2px solid #ff6600',
              boxShadow:
                '0 0 60px rgba(255,102,0,0.3), inset 0 0 40px rgba(255,102,0,0.05)',
              animationDelay: '0.3s',
            }}
          >
            <div className="relative space-y-8">
              {/* Feature pills */}
              <div className="flex flex-wrap gap-3 justify-center">
                {[
                  {
                    icon: '🚀',
                    text: 'Multi-Model Orchestration',
                    color: 'mint',
                  },
                  { icon: '⚡', text: 'Real-time Synthesis', color: 'blue' },
                  {
                    icon: '🎯',
                    text: 'Intelligent Optimization',
                    color: 'purple',
                  },
                  { icon: '💎', text: 'Premium Results', color: 'pink' },
                ].map((feature, i) => (
                  <span
                    key={i}
                    className={`px-6 py-2 rounded-full text-sm font-semibold border backdrop-blur animate-slide-in-bottom hover:scale-105 transition-smooth cursor-pointer`}
                    style={{
                      background: `${mapColorRGBA(feature.color, 0.2)}`,
                      borderColor: `${mapColorHex(feature.color)}50`,
                      color: mapColorHex(feature.color),
                      animationDelay: '0.3s',
                    }}
                  >
                    {feature.icon} {feature.text}
                  </span>
                ))}
              </div>

              {/* Main narrative */}
              <div className="max-w-3xl mx-auto mt-8">
                <p className="text-lg leading-relaxed text-center text-white/90">
                  <span
                    className="text-2xl font-bold block mb-4"
                    style={{
                      background:
                        'linear-gradient(90deg, #00ff9f, #00d4ff, #bd00ff)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text',
                      textShadow: 'none',
                    }}
                  >
                    Intelligence Multiplication Platform
                  </span>
                  Query multiple premium AI models simultaneously. Get
                  synthesized insights that no single model could provide.
                  <span className="font-bold text-white">
                    {' '}Pay only for what you use
                  </span>
                  .
                </p>
                <div className="flex justify-center gap-6 text-sm mt-6 text-white/90">
                  <span
                    className="text-white"
                    style={{
                      textShadow: '0 0 5px rgba(255,255,255,0.3)',
                    }}
                  >
                    Pay-as-you-go
                  </span>
                  <span className="text-white/70">•</span>
                  <span
                    className="text-white"
                    style={{
                      textShadow: '0 0 5px rgba(255,255,255,0.3)',
                    }}
                  >
                    No commitments
                  </span>
                  <span className="text-white/70">•</span>
                  <span
                    className="text-white"
                    style={{
                      textShadow: '0 0 5px rgba(255,255,255,0.3)',
                    }}
                  >
                    Enterprise-grade
                  </span>
                </div>
              </div>

              {/* CTA Button */}
              <div className="text-center space-y-3">
                <button
                  onClick={onEnter}
                  className="relative overflow-hidden px-12 py-5 text-xl font-bold rounded-lg transition-all duration-300 transform hover:scale-105 active:scale-95 group"
                  style={{
                    background:
                      'linear-gradient(135deg, #00ff9f 0%, #00d4ff 50%, #bd00ff 100%)',
                    boxShadow:
                      '0 4px 20px rgba(0, 255, 159, 0.4), 0 0 60px rgba(0, 212, 255, 0.3)',
                    animation:
                      'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                  }}
                  aria-label="Start using UltrAI analysis wizard"
                >
                  <span className="relative z-10 flex items-center gap-3 justify-center text-black font-extrabold">
                    <span>Enter UltrAI</span>
                    <span className="transform group-hover:translate-x-1 transition-transform">
                      →
                    </span>
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/30 to-white/0 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                </button>
                {isDemoMode && (
                  <button
                    onClick={onEnter}
                    className="px-8 py-3 text-sm font-semibold rounded-lg border-2 border-cyan-400/50 text-cyan-400 hover:bg-cyan-400/10 transition-all duration-200"
                  >
                    <span className="flex items-center gap-2 justify-center">
                      <Film className="w-4 h-4" />
                      <span>Try Demo</span>
                    </span>
                  </button>
                )}
              </div>

              {/* Trust indicators */}
              <div className="flex justify-center gap-8 text-sm text-white/80">
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>20+ AI Models</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>Enterprise Ready</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <span>SOC2 Compliant</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}