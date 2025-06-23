import React from 'react';
import CyberpunkWrapper from '../components/CyberpunkWrapper';
import UniversalContainer from '../components/universal/UniversalContainer';
import { useTheme } from '../theme/ThemeContext';

/**
 * Demo page to showcase the cyberpunk background implementation
 * Tests all features: multi-layer parallax, animations, interactivity
 */
const CyberpunkDemo: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <CyberpunkWrapper
      enableBackground={true}
      intensity="medium"
      performanceMode="balanced"
    >
      <div className="cyberpunk-demo-page min-h-screen p-8">
        
        {/* Header Section */}
        <UniversalContainer
          variant="primary"
          size="full"
          styleConfig={{
            decorativeElements: {
              drones: true,
              neonTrim: true,
              holographicDisplay: true
            }
          }}
          isFloating={true}
          animationLevel="moderate"
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-4">
            🏙️ Cyberpunk City Background Demo
          </h1>
          <p className="text-gray-300 text-lg mb-4">
            Interactive multi-layer cyberpunk cityscape with parallax depth, neon glow effects, and mouse tracking.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="text-center p-4 bg-gray-800/50 rounded">
              <h3 className="text-cyan-400 font-semibold">Purple Building</h3>
              <p className="text-sm text-gray-400">Background layer with building pulse animation</p>
            </div>
            <div className="text-center p-4 bg-gray-800/50 rounded">
              <h3 className="text-green-400 font-semibold">Circuit Building</h3>
              <p className="text-sm text-gray-400">Midground layer with data flow effects</p>
            </div>
            <div className="text-center p-4 bg-gray-800/50 rounded">
              <h3 className="text-blue-400 font-semibold">Bridge Structure</h3>
              <p className="text-sm text-gray-400">Foreground layer with connection pulses</p>
            </div>
          </div>
        </UniversalContainer>

        {/* Feature Testing Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Interactive Features */}
          <UniversalContainer
            variant="secondary"
            size="lg"
            styleConfig={{
              accentColor: 'cyan',
              decorativeElements: { neonTrim: true }
            }}
            animationLevel="subtle"
          >
            <h2 className="text-2xl font-bold text-cyan-400 mb-4">🎮 Interactive Features</h2>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-center">
                <span className="w-2 h-2 bg-cyan-400 rounded-full mr-3"></span>
                Move your mouse to see interactive glow effects
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-3"></span>
                Scroll to experience parallax depth layers
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-purple-400 rounded-full mr-3"></span>
                Watch animated data stream particles
              </li>
              <li className="flex items-center">
                <span className="w-2 h-2 bg-pink-400 rounded-full mr-3"></span>
                Use controls (top-right) to adjust settings
              </li>
            </ul>
          </UniversalContainer>

          {/* Performance Info */}
          <UniversalContainer
            variant="secondary"
            size="lg"
            styleConfig={{
              accentColor: 'purple',
              decorativeElements: { holographicDisplay: true }
            }}
            animationLevel="subtle"
          >
            <h2 className="text-2xl font-bold text-purple-400 mb-4">⚡ Performance Modes</h2>
            <div className="space-y-3 text-gray-300">
              <div className="p-3 bg-gray-800/30 rounded">
                <strong className="text-green-400">High:</strong> Full effects, 60fps animations
              </div>
              <div className="p-3 bg-gray-800/30 rounded">
                <strong className="text-blue-400">Balanced:</strong> Moderate effects, good performance
              </div>
              <div className="p-3 bg-gray-800/30 rounded">
                <strong className="text-orange-400">Battery:</strong> Minimal effects, optimized for mobile
              </div>
            </div>
          </UniversalContainer>

        </div>

        {/* Theme Controls */}
        <UniversalContainer
          variant="primary"
          size="full"
          styleConfig={{
            accentColor: 'pink',
            decorativeElements: {
              drones: true,
              neonTrim: true
            }
          }}
          isFloating={true}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-pink-400 mb-4">🎨 Theme Controls</h2>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => setTheme({ ...theme, style: 'cyberpunk', accentColor: 'cyan' })}
              className="px-4 py-2 bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 rounded hover:bg-cyan-500/30 transition-colors"
            >
              Cyberpunk Cyan
            </button>
            <button
              onClick={() => setTheme({ ...theme, style: 'cyberpunk', accentColor: 'purple' })}
              className="px-4 py-2 bg-purple-500/20 border border-purple-500/40 text-purple-300 rounded hover:bg-purple-500/30 transition-colors"
            >
              Cyberpunk Purple
            </button>
            <button
              onClick={() => setTheme({ ...theme, style: 'cyberpunk', accentColor: 'pink' })}
              className="px-4 py-2 bg-pink-500/20 border border-pink-500/40 text-pink-300 rounded hover:bg-pink-500/30 transition-colors"
            >
              Cyberpunk Pink
            </button>
            <button
              onClick={() => setTheme({ ...theme, style: 'corporate' })}
              className="px-4 py-2 bg-gray-500/20 border border-gray-500/40 text-gray-300 rounded hover:bg-gray-500/30 transition-colors"
            >
              Corporate
            </button>
          </div>
        </UniversalContainer>

        {/* Technical Details */}
        <UniversalContainer
          variant="card"
          size="full"
          styleConfig={{
            accentColor: 'cyan'
          }}
        >
          <h2 className="text-2xl font-bold text-cyan-400 mb-4">🔧 Technical Implementation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-sm text-gray-300">
            
            <div>
              <h3 className="text-green-400 font-semibold mb-2">SVG Assets</h3>
              <ul className="space-y-1">
                <li>• aquaAsset2.svg (Bridge)</li>
                <li>• aquaAsset3.svg (Purple Building)</li>
                <li>• aquaAsset8.svg (Circuit Building)</li>
                <li>• Optimized with SVGR</li>
              </ul>
            </div>

            <div>
              <h3 className="text-purple-400 font-semibold mb-2">Animations</h3>
              <ul className="space-y-1">
                <li>• CSS3 keyframe animations</li>
                <li>• GPU-accelerated transforms</li>
                <li>• Parallax scroll effects</li>
                <li>• Mouse tracking interactions</li>
              </ul>
            </div>

            <div>
              <h3 className="text-blue-400 font-semibold mb-2">Accessibility</h3>
              <ul className="space-y-1">
                <li>• Reduced motion support</li>
                <li>• High contrast mode</li>
                <li>• Keyboard navigation</li>
                <li>• Performance auto-detection</li>
              </ul>
            </div>

          </div>
        </UniversalContainer>

        {/* Footer Spacer for Scroll Testing */}
        <div className="h-screen flex items-center justify-center">
          <UniversalContainer
            variant="alert"
            size="md"
            styleConfig={{
              accentColor: 'cyan',
              decorativeElements: { neonTrim: true }
            }}
          >
            <p className="text-center text-cyan-400 text-lg">
              🚀 Scroll up and down to test parallax effects!
            </p>
          </UniversalContainer>
        </div>

      </div>
    </CyberpunkWrapper>
  );
};

export default CyberpunkDemo;