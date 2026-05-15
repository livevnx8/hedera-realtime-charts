/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'vnx-green': '#00bfa5',
        'vnx-red': '#ff6b6b',
        'vnx-gold': '#ffd93d',
        'vnx-purple': '#9c27b0',
        'vnx-bg': '#0f172a',
        'vnx-card': '#1e293b',
      },
    },
  },
  plugins: [],
}
