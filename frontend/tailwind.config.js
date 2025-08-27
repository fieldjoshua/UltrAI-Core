/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./public/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
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
        }
      },
      animation: {
        'pulse-neon': 'pulseNeon 1.5s infinite ease-in-out',
        'flicker': 'flicker 2s infinite'
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
          background: 'rgba(255,255,255,0.08)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255,255,255,0.2)',
        },
      });
    }
  ],
}
