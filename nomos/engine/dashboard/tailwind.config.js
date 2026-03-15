/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        quranic: {
          gold: '#D4AF37',
          dark: '#1a1a1a',
          light: '#f5f5f5',
        },
      },
    },
  },
  plugins: [],
};
