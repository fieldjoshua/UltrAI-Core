import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import UltraWithDocuments from './components/UltraWithDocuments';
import { PerformanceMonitor } from './components/PerformanceMonitor';
import PerformanceDashboard from './components/PerformanceDashboard';
import { BarChart3, Home, LayoutDashboard } from 'lucide-react';
import './index.css';

// Main app component with metrics panel
const MainApp = () => {
  const [showMetrics, setShowMetrics] = useState(false);
  
  const toggleMetrics = () => {
    setShowMetrics(prev => !prev);
  };
  
  return (
    <div className="app">
      <UltraWithDocuments />
      
      {/* Navigation link to dashboard */}
      <div className="fixed top-4 right-4 z-50">
        <Link to="/dashboard" 
          className="bg-gray-900 border border-cyan-800 p-2 rounded-full shadow-lg hover:bg-gray-800 focus:outline-none transition-all duration-300 group flex items-center gap-2"
        >
          <LayoutDashboard className="w-5 h-5 text-cyan-500 group-hover:text-cyan-400" />
        </Link>
      </div>
      
      {/* Metrics panel toggle button */}
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={toggleMetrics}
          className="bg-gray-900 border border-cyan-800 p-2 rounded-full shadow-lg hover:bg-gray-800 focus:outline-none transition-all duration-300 group"
          aria-label="Toggle metrics panel"
        >
          <BarChart3 className="w-6 h-6 text-cyan-500 group-hover:text-cyan-400" />
        </button>
      </div>
      
      {/* Metrics panel */}
      <div 
        className={`
          fixed bottom-16 right-4 z-40 w-80 transform transition-all duration-300 ease-in-out
          ${showMetrics ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        `}
      >
        <PerformanceMonitor />
      </div>
    </div>
  );
};

// Dashboard wrapper with home button
const DashboardWrapper = () => {
  return (
    <>
      {/* Navigation back to main app */}
      <div className="fixed top-4 left-4 z-50">
        <Link to="/" 
          className="bg-gray-900 border border-cyan-800 p-2 rounded-full shadow-lg hover:bg-gray-800 focus:outline-none transition-all duration-300 group flex items-center gap-2"
        >
          <Home className="w-5 h-5 text-cyan-500 group-hover:text-cyan-400" />
        </Link>
      </div>
      <PerformanceDashboard />
    </>
  );
};

// Root App component with routing
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainApp />} />
        <Route path="/dashboard" element={<DashboardWrapper />} />
      </Routes>
    </Router>
  );
}

export default App; 