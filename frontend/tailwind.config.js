/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        kab: {
          yellow: "#FFD400",   // top bar gold
          blue: "#0B5FA5",     // nav bar blue
          "blue-dark": "#08477D",
          orange: "#F5871F",   // accent underline
          green: "#1B6E2E",    // heading green (serif titles)
          "green-light": "#4CAF50",
        },
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
      },
    },
  },
  plugins: [],
}
