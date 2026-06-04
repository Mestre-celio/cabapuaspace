import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cabapua: {
          black: "#0A0A0A",
          dark: "#121212",
          red: "#DC2626",
          redHover: "#B91C1C",
          accent: "#F5F5F5",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
