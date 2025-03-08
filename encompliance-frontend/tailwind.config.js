/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'navy-blue': '#003366',
      },
      fontFamily: {
        'arial': ['Arial', 'Helvetica', 'sans-serif'],
        'times': ['"Times New Roman"', 'Times', 'serif'],
      },
    },
  },
  plugins: [],
};