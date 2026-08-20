/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      typography: {
        DEFAULT: { css: { maxWidth: 'none', 'code::before': false, 'code::after': false } },
        invert: { css: { maxWidth: 'none', 'code::before': false, 'code::after': false } },
      },
    },
  },
  plugins: [],
}
