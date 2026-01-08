/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Clean, Notion-like Palette
        background: "#ffffff",
        sidebar: "#fbfbfa", // Slightly warm/gray sidebar like Notion
        surface: "#ffffff",
        surfaceHover: "#f1f1ef",
        border: "#e5e5e5",
        
        primary: "#2563eb",     // Professional Blue (Tailwind Blue-600)
        primaryHover: "#1d4ed8",
        
        text: {
          main: "#37352f",      // Notion-like dark gray
          muted: "#787774",     // Medium gray
          light: "#9b9a97",     // Light gray
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        card: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
