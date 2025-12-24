/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#FFD700',
          dark: '#FFA500',
          light: '#FFEB3B'
        },
        background: {
          light: '#FFFFFF',
          dark: '#0A0A0A',
        },
        surface: {
          light: '#F5F5F5',
          dark: '#1A1A1A',
        },
        text: {
          light: '#000000',
          dark: '#FFFFFF',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
