/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'navy-blue': '#003366',
        'dark-bg': '#121212',
        'dark-surface': '#1e1e1e',
        'dark-border': '#333333',
        'dark-text': '#e0e0e0',
      },
      fontFamily: {
        'arial': ['Arial', 'Helvetica', 'sans-serif'],
        'times': ['"Times New Roman"', 'Times', 'serif'],
      },
      animation: {
        'theme-transition': 'themeTransition 2s ease-in-out',
      },
      keyframes: {
        themeTransition: {
          '0%': { opacity: '1' },
          '50%': { opacity: '0.7' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};