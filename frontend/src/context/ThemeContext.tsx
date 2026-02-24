"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type Theme =
  | "cyberpunk"
  | "dark-cool"
  | "forest"
  | "light-corporate"
  | "light-warm"
  | "light-lavender";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  availableThemes: { id: Theme; name: string; type: "dark" | "light" }[];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const availableThemes: { id: Theme; name: string; type: "dark" | "light" }[] = [
  { id: "cyberpunk", name: "Cyberpunk (Default)", type: "dark" },
  { id: "dark-cool", name: "Dark Cool", type: "dark" },
  { id: "forest", name: "Forest", type: "dark" },
  { id: "light-corporate", name: "Corporate Light", type: "light" },
  { id: "light-warm", name: "Warm Light", type: "light" },
  { id: "light-lavender", name: "Lavender Light", type: "light" },
];

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("cyberpunk");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Load from local storage
    const savedTheme = localStorage.getItem("opencore-theme") as Theme;
    if (savedTheme && availableThemes.some((t) => t.id === savedTheme)) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setThemeState(savedTheme);
    }
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    // Apply theme to document
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("opencore-theme", theme);
  }, [theme, mounted]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  // Prevent hydration mismatch by rendering nothing until mounted (or just render children with default but avoid flashing)
  // Actually, for themes, it's better to render immediately to avoid layout shift,
  // but we might get a flash of default theme.
  // Let's just return children. The useEffect will kick in on client.

  return (
    <ThemeContext.Provider value={{ theme, setTheme, availableThemes }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
