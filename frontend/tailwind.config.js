/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          800: '#1e293b',
          900: '#0f172a',
          950: '#090d16',
        },
        gridblue: {
          500: '#2563eb',
          600: '#1d4ed8',
        },
        solargreen: {
          500: '#10b981',
          600: '#059669',
        }
      }
    },
  },
  plugins: [],
}
