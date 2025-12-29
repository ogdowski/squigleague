/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'squig-yellow': '#fbbf24',
        'squig-dark': '#1a1a1a',
      },
    },
  },
  plugins: [],
}
