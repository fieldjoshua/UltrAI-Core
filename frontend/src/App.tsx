import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import WizardPage from "./pages/wizard";

function App() {
  return (
    <Router>
      <Routes>
        {/* Redirect root to wizard */}
        <Route path="/" element={<Navigate to="/wizard" replace />} />
        <Route path="/wizard" element={<WizardPage />} />
      </Routes>
    </Router>
  );
}

export default App;