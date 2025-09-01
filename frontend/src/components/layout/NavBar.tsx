import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Zap,
  LayoutDashboard,
  ListChecks,
  HelpCircle,
  User,
  Palette,
  Menu,
  X,
  Paintbrush,
} from 'lucide-react';
import { Button } from '../ui/button';
import { DayNightToggle, useTheme, ThemePanel } from '../../theme';
import { useAuthStore } from '../../stores/authStore';
import { UserMenu } from '../auth/UserMenu';

export default function NavBar() {
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [isThemePanelOpen, setIsThemePanelOpen] = React.useState(false);
  const [isSkinMenuOpen, setIsSkinMenuOpen] = React.useState(false);
  const { isAuthenticated } = useAuthStore();
  
  // Get current skin from body class
  const [currentSkin, setCurrentSkin] = React.useState(() => {
    return Array.from(document.body.classList)
      .find(cls => cls.startsWith('skin-'))
      ?.replace('skin-', '') || 'night';
  });
  
  const skins = [
    { name: 'morning', icon: '🌅', color: '#FFD27A' },
    { name: 'afternoon', icon: '☀️', color: '#7AD1FF' },
    { name: 'sunset', icon: '🌇', color: '#FF7A7A' },
    { name: 'night', icon: '🌙', color: '#B88CFF' },
    { name: 'minimalist', icon: '◻️', color: '#6B7280' },
    { name: 'business', icon: '💼', color: '#2C3E50' },
  ];

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <>
      {/* Slim icon-only Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 w-16 bg-white/90 dark:bg-gray-900/90 border-r border-gray-200 dark:border-gray-800 backdrop-blur-md hidden md:flex flex-col items-center">
        {/* Brand */}
        <div className="flex items-center justify-center h-14 w-full border-b border-gray-200 dark:border-gray-800">
          <span className="text-blue-600 dark:text-blue-400">
            <Zap size={22} />
          </span>
        </div>

        {/* Nav items (icons only) */}
        <nav className="flex-1 py-3 space-y-2 w-full flex flex-col items-center">
          <Link
            to="/dashboard"
            title="Dashboard"
            className={`flex items-center justify-center h-10 w-10 rounded-md ${
              isActive('/dashboard')
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
            }`}
          >
            <LayoutDashboard size={18} />
          </Link>

          <Link
            to="/outputs"
            title="Outputs"
            className={`flex items-center justify-center h-10 w-10 rounded-md ${
              isActive('/outputs')
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
            }`}
          >
            <ListChecks size={18} />
          </Link>

          <Link
            to="/faq"
            title="FAQ"
            className={`flex items-center justify-center h-10 w-10 rounded-md ${
              isActive('/faq')
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
            }`}
          >
            <HelpCircle size={18} />
          </Link>

          <Link
            to="/profile"
            title="Profile"
            className={`flex items-center justify-center h-10 w-10 rounded-md ${
              isActive('/profile')
                ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
            }`}
          >
            <User size={18} />
          </Link>
          
          {/* Skin Switcher */}
          <div className="relative">
            <button
              onClick={() => setIsSkinMenuOpen(!isSkinMenuOpen)}
              title="Change Theme"
              className={`flex items-center justify-center h-10 w-10 rounded-md ${
                isSkinMenuOpen
                  ? 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              <Paintbrush size={18} />
            </button>
            
            {/* Skin menu */}
            {isSkinMenuOpen && (
              <div className="absolute left-full ml-2 top-0 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-2 min-w-[200px]">
                <div className="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2 px-2">
                  Themes
                </div>
                {skins.map((skin) => (
                  <button
                    key={skin.name}
                    onClick={() => {
                      // Update body class
                      document.body.className = document.body.className.replace(/skin-\w+/g, '');
                      document.body.classList.add(`skin-${skin.name}`);
                      setCurrentSkin(skin.name);
                      localStorage.setItem('selectedSkin', skin.name);
                      
                      // Load the skin CSS
                      import(`../../skins/${skin.name}.css`);
                      
                      setIsSkinMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-2 py-2 rounded text-sm hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${
                      currentSkin === skin.name ? 'bg-gray-100 dark:bg-gray-800' : ''
                    }`}
                  >
                    <span className="text-lg">{skin.icon}</span>
                    <span className="flex-1 text-left capitalize">{skin.name}</span>
                    {currentSkin === skin.name && (
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: skin.color }} />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* Controls */}
        <div className="p-2 border-t border-gray-200 dark:border-gray-800 w-full flex flex-col items-center gap-2">
          <DayNightToggle size="sm" />
          <button
            onClick={() => setIsThemePanelOpen(!isThemePanelOpen)}
            title="Customize Theme"
            className="text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md h-10 w-10 flex items-center justify-center"
          >
            <Palette size={16} />
          </button>
          <div className="pb-2">{isAuthenticated ? <UserMenu /> : null}</div>
        </div>
      </aside>

      {/* Mobile top bar with menu */}
      <header className="md:hidden bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-40">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400"><Zap size={22} /></span>
            <span className="text-lg font-bold text-gray-900 dark:text-white">UltrAI</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-gray-700 dark:text-gray-300">
            {isMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
        </div>
        {isMenuOpen && (
          <nav className="px-2 pb-3 space-y-1">
            <Link to="/dashboard" className="block px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
            <Link to="/outputs" className="block px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => setIsMenuOpen(false)}>Outputs</Link>
            <Link to="/faq" className="block px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => setIsMenuOpen(false)}>FAQ</Link>
            <Link to="/profile" className="block px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" onClick={() => setIsMenuOpen(false)}>Profile</Link>
          </nav>
        )}
      </header>

      {/* Theme Panel */}
      {isThemePanelOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-xl font-bold">Customize Theme</h2>
              <Button variant="ghost" size="sm" onClick={() => setIsThemePanelOpen(false)} className="text-gray-700 dark:text-gray-300">
                <X size={20} />
              </Button>
            </div>
            <div className="p-4">
              <ThemePanel onClose={() => setIsThemePanelOpen(false)} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
