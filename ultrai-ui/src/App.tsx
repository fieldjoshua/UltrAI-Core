import UltrAIInteractiveBackground from './components/UltrAIInteractiveBackground';
import HUD from './components/HUD';

export default function App() {
  return (
    <UltrAIInteractiveBackground backgroundUrl="/ultrai-placeholder.svg">
      <div className="p-4 border-b border-white/10">
        <HUD />
      </div>

      {/* Demo content area */}
      <div className="flex items-center justify-center min-h-screen p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-pink-400 to-yellow-400 mb-8 animate-pulse">
            UltrAI
          </h1>
          <p className="text-xl text-cyan-100 mb-8 max-w-2xl mx-auto">
            Experience the power of Ultra Synthesis™ - where multiple AI models collaborate
            to deliver unprecedented intelligence multiplication.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="bg-black/30 backdrop-blur-sm border border-cyan-400/30 rounded-lg p-6">
              <h3 className="text-cyan-400 font-bold text-lg mb-2">Multi-Model</h3>
              <p className="text-cyan-100 text-sm">
                OpenAI, Anthropic, and Google models working in parallel
              </p>
            </div>
            <div className="bg-black/30 backdrop-blur-sm border border-pink-400/30 rounded-lg p-6">
              <h3 className="text-pink-400 font-bold text-lg mb-2">Synthesis</h3>
              <p className="text-cyan-100 text-sm">
                Advanced fusion algorithms for superior output quality
              </p>
            </div>
            <div className="bg-black/30 backdrop-blur-sm border border-yellow-400/30 rounded-lg p-6">
              <h3 className="text-yellow-400 font-bold text-lg mb-2">Real-time</h3>
              <p className="text-cyan-100 text-sm">
                Live orchestration with performance monitoring
              </p>
            </div>
          </div>
        </div>
      </div>
    </UltrAIInteractiveBackground>
  );
}