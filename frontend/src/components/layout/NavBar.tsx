import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, Zap, Box, Settings, ChevronRight, Menu, X, Layers, LayoutTemplate } from 'lucide-react';
import { Button } from '../ui/button';

export default function NavBar() {
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <span className="text-blue-600 dark:text-blue-400 mr-2">
                <Zap size={24} />
              </span>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                UltrAI
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            <Link
              to="/documents"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/documents')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center">
                <FileText size={16} className="mr-2" />
                Documents
              </div>
            </Link>

            <Link
              to="/analyze"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/analyze')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center">
                <Zap size={16} className="mr-2" />
                Simple Analysis
              </div>
            </Link>

            <Link
              to="/modelrunner"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/modelrunner')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center">
                <Box size={16} className="mr-2" />
                Model Runner
              </div>
            </Link>

            <Link
              to="/orchestrator"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/orchestrator')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center">
                <Layers size={16} className="mr-2" />
                Orchestrator
              </div>
            </Link>

            <Link
              to="/prototype"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/prototype')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center">
                <LayoutTemplate size={16} className="mr-2" />
                UI Prototype
              </div>
            </Link>
          </nav>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 dark:text-gray-300"
            >
              {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-2 pt-2 pb-3 space-y-1 border-t border-gray-200 dark:border-gray-800">
            <Link
              to="/documents"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/documents')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              <div className="flex items-center">
                <FileText size={16} className="mr-2" />
                Documents
              </div>
            </Link>

            <Link
              to="/analyze"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/analyze')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              <div className="flex items-center">
                <Zap size={16} className="mr-2" />
                Simple Analysis
              </div>
            </Link>

            <Link
              to="/modelrunner"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/modelrunner')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              <div className="flex items-center">
                <Box size={16} className="mr-2" />
                Model Runner
              </div>
            </Link>

            <Link
              to="/orchestrator"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/orchestrator')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              <div className="flex items-center">
                <Layers size={16} className="mr-2" />
                Orchestrator
              </div>
            </Link>

            <Link
              to="/prototype"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive('/prototype')
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              <div className="flex items-center">
                <LayoutTemplate size={16} className="mr-2" />
                UI Prototype
              </div>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
