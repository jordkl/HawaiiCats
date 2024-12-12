/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./static/src/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'hawaii-blue': '#0077be',
        'hawaii-green': '#2d5a27',
        'hawaii-sand': '#f4d03f',
        'hawaii-coral': '#ff6b6b',
      },
      fontFamily: {
        sans: ['Inter var', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
