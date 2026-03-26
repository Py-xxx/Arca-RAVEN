/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          900: "#0a0b0f",
          800: "#111318",
          700: "#1a1d24",
          600: "#22262f",
          500: "#2c3039",
        },
        accent: {
          500: "#f97316",
          400: "#fb923c",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
