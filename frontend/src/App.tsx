import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useEffect, lazy, Suspense } from "react";
import { useAuthStore } from "./stores/authStore";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import ErrorBoundary from "./components/ErrorBoundary";

// Layout
import NavBar from "./components/layout/NavBar";
import DemoIndicator from "./components/DemoIndicator";

// Immediate load for critical pages
import WizardPage from "./pages/wizard";

// Lazy load all other pages
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
const ModelMonitor = lazy(() => import("./pages/ModelMonitor"));
const Admin = lazy(() => import("./pages/Admin"));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[50vh]">
    <div className="text-center">
      <div className="w-12 h-12 border-4 border-mint-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p className="text-white/60 text-sm">Loading...</p>
    </div>
  </div>
);

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

  useEffect(() => {
    // Try to fetch current user on app load if token exists
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 md:pl-16">
          <NavBar />
          <main className="container mx-auto px-4 py-6">
            <Suspense fallback={<PageLoader />}>
              <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Navigate to="/wizard" replace />} />
            <Route path="/wizard" element={<WizardPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/analyze" element={<SimpleAnalysis />} />
            <Route path="/prototype" element={<UIPrototype />} />
            <Route path="/universal-ui" element={<UniversalUI />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/outputs" element={<Outputs />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/monitor" element={<ModelMonitor />} />
            <Route path="/admin" element={<Admin />} />

            {/* Protected Routes */}
            <Route 
              path="/documents" 
              element={
                <ProtectedRoute>
                  <DocumentsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/orchestrator" 
              element={
                <ProtectedRoute>
                  <OrchestratorPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/modelrunner" 
              element={
                <ProtectedRoute>
                  <ModelRunnerDemo />
                </ProtectedRoute>
              } 
            />

            {/* Catch all - redirect to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </main>
      </div>
    </Router>
    </ErrorBoundary>
  );
}

export default App;