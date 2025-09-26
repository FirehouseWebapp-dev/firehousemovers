/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'firehouse-red': '#ef4444',
        'firehouse-dark': '#1a1a1a',
        'firehouse-gray': '#262626',
      },
      fontFamily: {
        'serif': ['serif'],
      },
    },
  },
  plugins: [],
}
