import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)" /* 0.75rem */,
        md: "calc(var(--radius) - 0.125rem)" /* 0.625rem */,
        sm: "calc(var(--radius) - 0.25rem)" /* 0.5rem */,
        xl: "calc(var(--radius) + 0.25rem)" /* 1rem */,
        "2xl": "calc(var(--radius) + 0.5rem)" /* 1.25rem */,
      },

      boxShadow: {
        /* Warm-tinted shadows — no cold gray */
        "warm-xs": "0 1px 2px 0 hsl(30 20% 55% / 0.08)",
        "warm-sm":
          "0 1px 3px 0 hsl(30 20% 50% / 0.10), 0 1px 2px -1px hsl(30 20% 50% / 0.08)",
        "warm-md":
          "0 4px 12px -2px hsl(30 20% 45% / 0.12), 0 2px 4px -2px hsl(30 20% 45% / 0.08)",
        "warm-lg":
          "0 10px 24px -4px hsl(30 20% 40% / 0.14), 0 4px 8px -4px hsl(30 20% 40% / 0.08)",
        "warm-xl":
          "0 20px 40px -8px hsl(30 20% 35% / 0.16), 0 8px 16px -6px hsl(30 20% 35% / 0.08)",

        /* Honey glow — use sparingly on primary CTAs */
        "honey-glow": "0 0 0 3px hsl(33 65% 50% / 0.18)",
      },

      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.18s ease-out",
      },
    },
  },
  plugins: [tailwindcssAnimate],
};

export default config;
