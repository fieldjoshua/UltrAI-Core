import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useEffect } from "react";
import { useAuthStore } from "./stores/authStore";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";

// Layout
import NavBar from "./components/layout/NavBar";

// Auth Pages
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";

// Public Pages
import WizardPage from "./pages/wizard";
import SimpleAnalysis from "./pages/SimpleAnalysis";
import UIPrototype from "./pages/UIPrototype";
import UniversalUI from "./pages/UniversalUI";
import Dashboard from "./pages/Dashboard";
import Outputs from "./pages/Outputs";
import FAQ from "./pages/FAQ";

// Protected Pages
import DocumentsPage from "./pages/DocumentsPage";
import OrchestratorPage from "./pages/OrchestratorPage";
import ModelRunnerDemo from "./pages/ModelRunnerDemo";

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
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 md:pl-16">
        <NavBar />
        <main className="container mx-auto px-4 py-6">
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
        </main>
      </div>
    </Router>
  );
}

export default App;