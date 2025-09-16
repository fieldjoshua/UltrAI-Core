/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./src/**/*.{js,ts,jsx,tsx}', './public/**/*.html'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border, 0 0% 16%))',
        background: 'hsl(var(--background, 0 0% 4%))',
        foreground: 'hsl(var(--foreground, 0 0% 96%))',
        muted: 'hsl(var(--muted, 0 0% 10%))',
        'muted-foreground': 'hsl(var(--muted-foreground, 0 0% 57%))',
        accent: 'hsl(var(--accent, 199 100% 50%))',
        'accent-foreground': 'hsl(var(--accent-foreground, 0 0% 98%))',
        destructive: 'hsl(var(--destructive, 348 100% 50%))',
        'destructive-foreground': 'hsl(var(--destructive-foreground, 0 0% 98%))',
        primary: {
          DEFAULT: 'hsl(var(--primary, 0 0% 98%))',
          foreground: 'hsl(var(--primary-foreground, 0 0% 11%))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary, 0 0% 17%))',
          foreground: 'hsl(var(--secondary-foreground, 0 0% 98%))',
        },
        neon: {
          mint: '#00ff9f',
          blue: '#00b8ff',
          deepblue: '#001eff',
          purple: '#bd00ff',
          pink: '#d600ff',
          cyan: '#00fff7',
          green: '#00ff00',
        },
      },
      boxShadow: {
        'neon-mint': '0 0 20px #00ff9f',
        'neon-blue': '0 0 20px #00b8ff',
        'neon-deep': '0 0 20px #001eff',
        'neon-purple': '0 0 20px #bd00ff',
        'neon-pink': '0 0 20px #d600ff',
        'neon-cyan': '0 0 32px 8px rgba(0, 255, 247, 0.4)',
        'neon-green': '0 0 32px 8px rgba(0, 255, 159, 0.4)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      keyframes: {
        // Existing animations
        pulseNeon: {
          '0%, 100%': { boxShadow: '0 0 15px currentColor' },
          '50%': { boxShadow: '0 0 30px currentColor' },
        },
        flicker: {
          '0%, 19%, 21%, 23%, 25%, 54%, 56%, 100%': { opacity: '1' },
          '20%, 24%, 55%': { opacity: '0.3' },
        },
        bgPan: {
          '0%': { backgroundPosition: '0% 50%, 0% 50%' },
          '100%': { backgroundPosition: '100% 50%, 100% 50%' },
        },
        parallaxSlow: {
          '0%': { transform: 'scale(1.06) translateY(-1vh)' },
          '100%': { transform: 'scale(1) translateY(0)' },
        },
        parallaxFast: {
          '0%': { transform: 'scale(1.08) translateY(-1.2vh)' },
          '100%': { transform: 'scale(1) translateY(0)' },
        },
        linesGlow: {
          '0%, 100%': {
            opacity: 0.75,
            filter: 'drop-shadow(0 0 2px #00ff7f) saturate(140%)',
          },
          '50%': {
            opacity: 0.95,
            filter: 'drop-shadow(0 0 8px #00ff7f) saturate(180%)',
          },
        },
        // New animations from index.css
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-top': {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-bottom': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'billboard-sweep': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glitch: {
          '0%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
          '100%': { transform: 'translate(0)' },
        },
        'blur-up': {
          '0%': { filter: 'blur(20px)', transform: 'scale(1.1)' },
          '100%': { filter: 'blur(0)', transform: 'scale(1)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        'hue-shift': {
          '0%': { filter: 'hue-rotate(0deg)' },
          '100%': { filter: 'hue-rotate(360deg)' },
        },
        'neon-glow': {
          '0%, 100%': {
            textShadow: '0 0 8px #00fff7, 0 0 24px #00fff7, 0 0 48px #00e0ff',
          },
          '50%': {
            textShadow: '0 0 16px #00fff7, 0 0 48px #00fff7, 0 0 96px #00e0ff',
          },
        },
        pulse: {
          '0%, 100%': {
            opacity: '1',
            boxShadow: '0 4px 20px rgba(0, 255, 159, 0.4), 0 0 60px rgba(0, 212, 255, 0.3)',
          },
          '50%': {
            opacity: '0.9',
            boxShadow: '0 4px 30px rgba(0, 255, 159, 0.6), 0 0 80px rgba(0, 212, 255, 0.5)',
          },
        },
      },
      animation: {
        'pulse-neon': 'pulseNeon 1.5s infinite ease-in-out',
        flicker: 'flicker 2s infinite',
        'bg-pan': 'bgPan 20s linear 1 alternate forwards',
        'parallax-slow': 'parallaxSlow 8s ease-out forwards',
        'parallax-fast': 'parallaxFast 6s ease-out forwards',
        'lines-glow': 'linesGlow 3.5s ease-in-out infinite',
        // New animations
        'fade-in': 'fade-in 0.5s ease-out',
        'fade-in-up': 'fade-in-up 0.6s ease-out',
        'slide-in-top': 'slide-in-top 0.6s ease-out',
        'slide-in-bottom': 'slide-in-bottom 0.6s ease-out',
        'scale-in': 'scale-in 0.5s ease-out',
        'pulse-subtle': 'pulse-subtle 3s ease-in-out infinite',
        'billboard-sweep': 'billboard-sweep 3s ease-in-out infinite',
        glitch: 'glitch 0.3s ease',
        'blur-up': 'blur-up 0.8s ease-out forwards',
        float: 'float 6s ease-in-out infinite',
        'hue-shift': 'hue-shift 18s linear infinite',
        'neon-glow': 'neon-glow 2.5s ease-in-out infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      fontFamily: {
        cyber: ['Orbitron', 'Exo 2', 'sans-serif'],
        mono: ['Share Tech Mono', 'Space Mono', 'monospace'],
      },
      backgroundImage: {
        'cyber-gradient':
          'linear-gradient(90deg, #00ff9f, #00b8ff, #bd00ff, #d600ff)',
        'gradient-neon':
          'linear-gradient(135deg, #00ff9f 0%, #00d4ff 50%, #bd00ff 100%)',
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      dropShadow: {
        'neon-cyan': '0 0 24px rgba(0, 255, 247, 0.8)',
        'neon-pink': '0 0 24px rgba(255, 0, 234, 0.8)',
        'neon-green': '0 0 24px rgba(0, 255, 159, 0.8)',
      },
      transitionDuration: {
        smooth: '300ms',
        slow: '500ms',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/forms'),
    function ({ addUtilities, addComponents }) {
      // Glass morphism utilities
      addUtilities({
        '.glass': {
          background: 'rgba(255,255,255,0.06)',
          backdropFilter: 'blur(18px) saturate(120%)',
          WebkitBackdropFilter: 'blur(18px) saturate(120%)',
          border: '1px solid rgba(255,255,255,0.18)',
          boxShadow: '0 10px 30px rgba(0,0,0,0.25)',
        },
        '.glass-strong': {
          background: 'rgba(255,255,255,0.12)',
          backdropFilter: 'blur(24px) saturate(140%)',
          WebkitBackdropFilter: 'blur(24px) saturate(140%)',
          border: '1px solid rgba(255,255,255,0.25)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.35)',
        },
        '.glass-panel': {
          backdropFilter: 'blur(16px)',
          WebkitBackdropFilter: 'blur(16px)',
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.2)',
        },
        '.glass-grain': {
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: '0',
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E")`,
            pointerEvents: 'none',
            opacity: '0.03',
          },
        },
        // Text shadow utilities
        '.text-shadow-sm': {
          textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)',
        },
        '.text-shadow': {
          textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
        },
        '.text-shadow-lg': {
          textShadow: '0 4px 8px rgba(0, 0, 0, 0.5)',
        },
        // Neon text shadows
        '.text-neon-mint': { textShadow: '0 0 8px #00ff9f, 0 0 16px #00ff9f' },
        '.text-neon-blue': { textShadow: '0 0 8px #00b8ff, 0 0 16px #00b8ff' },
        '.text-neon-deep': { textShadow: '0 0 8px #001eff, 0 0 16px #001eff' },
        '.text-neon-purple': {
          textShadow: '0 0 8px #bd00ff, 0 0 16px #bd00ff',
        },
        '.text-neon-pink': { textShadow: '0 0 8px #d600ff, 0 0 16px #d600ff' },
        '.text-neon-cyan': { textShadow: '0 0 8px #00fff7, 0 0 24px #00fff7, 0 0 48px #00e0ff' },
        // Gradient text utility
        '.gradient-text': {
          background: 'linear-gradient(90deg, #00ff9f, #00d4ff, #bd00ff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        },
        // Optimized background rendering
        '.bg-optimized': {
          imageRendering: '-webkit-optimize-contrast',
          imageRendering: 'crisp-edges',
          backfaceVisibility: 'hidden',
          transform: 'translateZ(0)',
          willChange: 'filter',
        },
        // Transition utilities
        '.transition-smooth': {
          transitionProperty: 'all',
          transitionTimingFunction: 'cubic-bezier(0.4, 0, 0.2, 1)',
          transitionDuration: '300ms',
        },
      });

      // Component classes
      addComponents({
        '.btn-neon': {
          '@apply relative overflow-hidden px-6 py-3 font-bold rounded-lg transition-all duration-300': {},
          background: 'linear-gradient(90deg, #00ffd0 0%, #00bfff 50%, #00ffd0 100%)',
          color: '#0a0a0a',
          boxShadow: '0 0 16px 4px #00ffd0, 0 0 32px 8px #00bfff',
          '&:hover': {
            boxShadow: '0 0 32px 8px #00ffd0, 0 0 64px 16px #00bfff',
          },
        },
        '.neon-title': {
          '@apply font-black tracking-wider': {},
          fontSize: '2.8rem',
          color: '#00fff7',
          textShadow: '0 0 8px #00fff7, 0 0 24px #00fff7, 0 0 48px #00e0ff',
          animation: 'neon-glow 2.5s ease-in-out infinite',
        },
        '.neon-panel': {
          background: 'rgba(20, 20, 40, 0.92)',
          borderRadius: '1.5rem',
          boxShadow: '0 0 32px 8px rgba(0, 255, 255, 0.12), 0 0 0 4px rgba(0, 255, 255, 0.08) inset',
          border: '2px solid #2ffcff',
          position: 'relative',
          overflow: 'hidden',
        },
        '.gradient-button': {
          background: 'linear-gradient(135deg, #00ff9f 0%, #00d4ff 50%, #bd00ff 100%)',
          boxShadow: '0 4px 20px rgba(0, 255, 159, 0.4), 0 0 60px rgba(0, 212, 255, 0.3)',
        },
      });
    },
  ],
};
