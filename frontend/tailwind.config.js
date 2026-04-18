/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        base: "#0F0F10",
        card: "#1A1A1D",
        elevated: "#26262A",
        primary: "#4F7CFF",
        "primary-deep": "#1E3A8A",
        "primary-bright": "#3B5FD9",
        positive: "#10B981",
        "text-muted": "#9CA3AF",
      },
    },
  },
  plugins: [],
}
