import React, { useEffect, useMemo, useState } from 'react';
import { config, Skin } from '../config';
import { loadSkin } from '../skins';
import { AnimationToggle } from './AnimationToggle';

export default function SkinSwitcher() {
  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const paramSkin = params.get('skin') as Skin | null;

  // Check localStorage for saved skin preference
  const savedSkin = localStorage.getItem('selectedSkin') as Skin | null;

  const initialSkin: Skin =
    paramSkin && (config.availableSkins as string[]).includes(paramSkin)
      ? paramSkin
      : savedSkin && (config.availableSkins as string[]).includes(savedSkin)
        ? savedSkin
        : config.defaultSkin;

  const [skin, setSkin] = useState<Skin>(initialSkin);

  useEffect(() => {
    try {
      loadSkin(skin);
      // Update body class for skin-specific styles
      document.body.className = document.body.className.replace(
        /skin-\w+/g,
        ''
      );
      document.body.classList.add(`skin-${skin}`);
    } catch (e) {
      // Fallback to default skin if dynamic import fails
      loadSkin(config.defaultSkin);
      document.body.classList.add(`skin-${config.defaultSkin}`);
    }
  }, [skin]);

  const handleChange = (newSkin: Skin) => {
    if ((config.availableSkins as string[]).includes(newSkin)) {
      setSkin(newSkin);
      // Save the skin preference to localStorage
      localStorage.setItem('selectedSkin', newSkin);
    }
  };

  const getThemeIcon = (themeName: string) => {
    switch (themeName) {
      case 'morning':
        return '🌅';
      case 'afternoon':
        return '☀️';
      case 'sunset':
        return '🌇';
      case 'night':
        return '🌙';
      case 'minimalist':
        return '◻️';
      default:
        return '🎨';
    }
  };

  const getThemeColor = (themeName: string) => {
    switch (themeName) {
      case 'morning':
        return '#FFD27A';
      case 'afternoon':
        return '#7AD1FF';
      case 'sunset':
        return '#FF7A7A';
      case 'night':
        return '#B88CFF';
      case 'minimalist':
        return '#6B7280';
      default:
        return '#fff';
    }
  };

  return (
    <div
      className="skin-switcher"
      style={{
        position: 'fixed',
        top: 70,
        right: 10,
        background: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(10px)',
        color: '#fff',
        padding: '12px',
        borderRadius: 12,
        fontSize: 12,
        zIndex: 1000,
        border: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 'bold',
          marginBottom: 8,
          textTransform: 'uppercase',
          letterSpacing: 1,
          opacity: 0.8,
        }}
        id="theme-selector-label"
      >
        Theme
      </div>
      <div
        style={{ display: 'flex', gap: 4 }}
        role="radiogroup"
        aria-labelledby="theme-selector-label"
      >
        {config.availableSkins.map(s => {
          const isActive = skin === s;
          const themeColor = getThemeColor(s);
          return (
            <button
              key={s}
              onClick={() => handleChange(s as Skin)}
              title={s.charAt(0).toUpperCase() + s.slice(1)}
              role="radio"
              aria-checked={isActive}
              aria-label={`Select ${s} theme`}
              style={{
                background: isActive
                  ? `${themeColor}20`
                  : 'rgba(255, 255, 255, 0.05)',
                border: isActive
                  ? `2px solid ${themeColor}`
                  : '1px solid rgba(255, 255, 255, 0.2)',
                color: isActive ? themeColor : 'rgba(255, 255, 255, 0.7)',
                borderRadius: 8,
                padding: '8px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                fontSize: 16,
                minWidth: 45,
                transition: 'all 0.2s ease',
                transform: isActive ? 'scale(1.05)' : 'scale(1)',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  e.currentTarget.style.transform = 'scale(1.05)';
                  e.currentTarget.style.background = `${themeColor}10`;
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.background =
                    'rgba(255, 255, 255, 0.05)';
                }
              }}
            >
              <div>{getThemeIcon(s)}</div>
              <div
                style={{
                  fontSize: 9,
                  fontWeight: isActive ? 'bold' : 'normal',
                }}
              >
                {s === 'minimalist' ? 'Min' : s.slice(0, 3).toUpperCase()}
              </div>
            </button>
          );
        })}
      </div>
      <div className="mt-3 pt-3 border-t border-white/20">
        <AnimationToggle />
      </div>
    </div>
  );
}
