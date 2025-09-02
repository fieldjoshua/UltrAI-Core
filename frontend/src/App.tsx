import { HashRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, lazy, Suspense } from "react";
import { useAuthStore } from "./stores/authStore";
import ErrorBoundary from "./components/ErrorBoundary";
import { AnimatePresence, motion } from "framer-motion";

import { config } from "./config";
import { useTheme } from "./theme/ThemeRegistry";

// Layout
import NavBar from "./components/layout/NavBar";
import DemoIndicator from "./components/DemoIndicator";

// Immediate load for critical pages
import WizardPage from "./pages/wizard";

// Lazy load others
const LoginPage = lazy(() => import("./pages/LoginPage").then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import("./pages/RegisterPage").then(m => ({ default: m.RegisterPage })));
const SimpleAnalysis = lazy(() => import("./pages/SimpleAnalysis"));
const UIPrototype = lazy(() => import("./pages/UIPrototype"));
const UniversalUI = lazy(() => import("./pages/UniversalUI"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Outputs = lazy(() => import("./pages/Outputs"));
const FAQ = lazy(() => import("./pages/FAQ"));
const DocumentsPage = lazy(() => import("./pages/DocumentsPage"));
const OrchestratorPage = lazy(() => import("./pages/OrchestratorPage"));
const ModelRunnerDemo = lazy(() => import("./pages/ModelRunnerDemo"));

// Loader
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[50vh]">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-gradient-to-r from-mint-400 to-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-white/80 text-sm">
        {config.apiMode === "mock" ? "Loading mock data…" : "Loading live data…"}
      </p>
    </div>
  </div>
);

// Mode banner
const ModeBanner = () => {
  if (config.appMode === "production") return null;
  const color =
    config.appMode === "playground"
      ? "bg-blue-600"
      : config.appMode === "staging"
      ? "bg-yellow-600"
      : "bg-gray-700";
  return (
    <div className={`${color} text-white text-center text-sm py-1`}>
      {config.appMode.toUpperCase()} MODE – features may be unstable
    </div>
  );
};

function Profile() {
  return (
    <div className="text-white">
      <h1 className="text-2xl font-bold mb-2">Profile</h1>
      <p className="opacity-80">Manage your user profile here.</p>
    </div>
  );
}

function App() {
  const { fetchCurrentUser } = useAuthStore();
  const { skin, setSkin } = useTheme();

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen flex flex-col" data-skin={skin}>
          <ModeBanner />
          <NavBar />
          <DemoIndicator />

          {/* Skin Switcher */}
          <div className="flex gap-2 p-2 bg-black/30 justify-center">
            {config.availableSkins.map(s => (
              <button
                key={s}
                onClick={() => setSkin(s)}
                className={`px-3 py-1 rounded ${
                  s === skin ? "bg-mint-500 text-black" : "bg-white/10 hover:bg-white/20"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <div className="flex-1 p-4">
            <Suspense fallback={<PageLoader />}>
              <AnimatePresence mode="wait">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route
                    path="/dashboard"
                    element={
                      <motion.div
                        key="dashboard"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Dashboard />
                      </motion.div>
                    }
                  />
                  <Route path="/wizard" element={<WizardPage />} />
                  <Route path="/analysis" element={<SimpleAnalysis />} />
                  <Route path="/prototype" element={<UIPrototype />} />
                  <Route path="/universal" element={<UniversalUI />} />
                  <Route path="/outputs" element={<Outputs />} />
                  <Route path="/faq" element={<FAQ />} />
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/orchestrator" element={<OrchestratorPage />} />
                  <Route path="/demo" element={<ModelRunnerDemo />} />
                  <Route path="/profile" element={<Profile />} />
                </Routes>
              </AnimatePresence>
            </Suspense>
          </div>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App; 
