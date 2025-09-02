/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./public/**/*.html"
  ],
  theme: {
    extend:{
      colors: {
        bg: "var(--bg)",
        fg: "var(--fg)",
        border: "#2a2a2a",        // enables border-border
        background: "#0a0a0a",    // enables bg-background
        foreground: "#f5f5f5",    // enables text-foreground
        muted: "#1a1a1a",
        accent: "#00b8ff",
        destructive: "#ff0033",
        neon: {
          mint: "#00ff9f",
          blue: "#00b8ff",
          deepblue: "#001eff",
          purple: "#bd00ff",
          pink: "#d600ff",
        }
      },
      boxShadow: {
        'neon-mint': '0 0 20px #00ff9f',
        'neon-blue': '0 0 20px #00b8ff',
        'neon-deep': '0 0 20px #001eff',
        'neon-purple': '0 0 20px #bd00ff',
        'neon-pink': '0 0 20px #d600ff',
      },
      keyframes: {
        pulseNeon: {
          '0%, 100%': { boxShadow: '0 0 15px currentColor' },
          '50%': { boxShadow: '0 0 30px currentColor' },
        },
        flicker: {
          '0%, 19%, 21%, 23%, 25%, 54%, 56%, 100%': { opacity: '1' },
          '20%, 24%, 55%': { opacity: '0.3' }
        },
        bgPan: {
          '0%': { backgroundPosition: '0% 50%, 0% 50%' },
          '100%': { backgroundPosition: '100% 50%, 100% 50%' }
        },
        parallaxSlow: {
          '0%': { transform: 'scale(1.06) translateY(-1vh)' },
          '100%': { transform: 'scale(1) translateY(0)' }
        },
        parallaxFast: {
          '0%': { transform: 'scale(1.08) translateY(-1.2vh)' },
          '100%': { transform: 'scale(1) translateY(0)' }
        },
        linesGlow: {
          '0%, 100%': { opacity: 0.75, filter: 'drop-shadow(0 0 2px #00ff7f) saturate(140%)' },
          '50%': { opacity: 0.95, filter: 'drop-shadow(0 0 8px #00ff7f) saturate(180%)' }
        }
      },
      animation: {
        'pulse-neon': 'pulseNeon 1.5s infinite ease-in-out',
        'flicker': 'flicker 2s infinite',
        'bg-pan': 'bgPan 20s linear 1 alternate forwards',
        'parallax-slow': 'parallaxSlow 8s ease-out forwards',
        'parallax-fast': 'parallaxFast 6s ease-out forwards',
        'lines-glow': 'linesGlow 3.5s ease-in-out infinite'
      },
      fontFamily: {
        cyber: ['Orbitron','sans-serif'],
        mono: ['Share Tech Mono','monospace']
      },
      backgroundImage: {
        'cyber-gradient': 'linear-gradient(90deg, #00ff9f, #00b8ff, #bd00ff, #d600ff)',
      }
    },
  },
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.glass': {
          background: 'rgba(255,255,255,0.06)',
          backdropFilter: 'blur(18px) saturate(120%)',
          WebkitBackdropFilter: 'blur(18px) saturate(120%)',
          border: '1px solid rgba(255,255,255,0.18)',
          boxShadow: '0 10px 30px rgba(0,0,0,0.25)'
        },
        '.glass-strong': {
          background: 'rgba(255,255,255,0.12)',
          backdropFilter: 'blur(24px) saturate(140%)',
          WebkitBackdropFilter: 'blur(24px) saturate(140%)',
          border: '1px solid rgba(255,255,255,0.25)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.35)'
        },
        '.text-neon-mint': { textShadow: '0 0 8px #00ff9f, 0 0 16px #00ff9f' },
        '.text-neon-blue': { textShadow: '0 0 8px #00b8ff, 0 0 16px #00b8ff' },
        '.text-neon-deep': { textShadow: '0 0 8px #001eff, 0 0 16px #001eff' },
        '.text-neon-purple': { textShadow: '0 0 8px #bd00ff, 0 0 16px #bd00ff' },
        '.text-neon-pink': { textShadow: '0 0 8px #d600ff, 0 0 16px #d600ff' }
      });
    }
  ],
}
