/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "./index.html",
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Professional handball table colors with WCAG AA contrast
        hb: {
          // Light Mode
          light: {
            header: "#1e40af",           // Professional dark blue (WCAG AA: 10.5:1 vs white)
            headerText: "#ffffff",       // White text on header
            subheader: "#3b82f6",        // Medium blue
            subheaderText: "#ffffff",    // White text on subheader
            playerRowOdd: "#ffffff",     // White (primary row)
            playerRowEven: "#f3f4f6",    // Very light gray (WCAG AA: 12.5:1 vs black)
            playerText: "#1f2937",       // Dark gray text
            gestaltBg: "#fef08a",        // Light yellow (totals)
            gestaltText: "#1f2937",      // Dark text on yellow
            border: "#d1d5db",           // Light gray border
            borderAlt: "#9ca3af",        // Darker border
            hover: "#ede9fe",            // Light purple hover
          },
          // Dark Mode
          dark: {
            header: "#3b82f6",           // Bright blue
            headerText: "#ffffff",       // White text
            subheader: "#1e40af",        // Dark blue
            subheaderText: "#e0e7ff",    // Light lavender text
            playerRowOdd: "#111827",     // Almost black
            playerRowEven: "#1f2937",    // Dark gray
            playerText: "#f3f4f6",       // Light text
            gestaltBg: "#92400e",        // Dark orange/brown (totals)
            gestaltText: "#fef3c7",      // Light text on dark
            border: "#374151",           // Medium gray border
            borderAlt: "#4b5563",        // Lighter gray border
            hover: "#312e81",            // Dark purple hover
          },
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
}
