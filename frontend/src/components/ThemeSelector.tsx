"use client";

import { useState, useRef, useEffect } from "react";
import { Palette, Check } from "lucide-react";
import { useTheme, Theme, availableThemes } from "@/context/ThemeContext";

export default function ThemeSelector() {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Theme Settings"
        className="p-2 hover:bg-bg-tertiary rounded-lg transition-all border border-transparent hover:border-border-primary text-accent-1 hover:text-text-primary hover:shadow-[0_0_15px_color-mix(in_srgb,var(--accent-1),transparent_70%)] active:scale-95"
      >
        <Palette size={24} />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-12 z-50 w-64 bg-bg-secondary border border-border-primary rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-3 border-b border-border-primary bg-bg-tertiary/50 backdrop-blur-sm">
                <h3 className="text-sm font-orbitron text-accent-1 tracking-wider uppercase">Interface Theme</h3>
            </div>
            <div className="p-2 space-y-1 max-h-[300px] overflow-y-auto">
                {availableThemes.map((t) => (
                    <button
                        key={t.id}
                        onClick={() => {
                            setTheme(t.id as Theme);
                            setIsOpen(false);
                        }}
                        className={`w-full flex items-center justify-between p-2 rounded-lg text-sm transition-colors ${
                            theme === t.id
                            ? "bg-accent-1/10 text-accent-1 border border-accent-1/20"
                            : "hover:bg-bg-tertiary text-text-secondary hover:text-text-primary"
                        }`}
                    >
                        <span className="flex items-center gap-2">
                            <span className={`w-3 h-3 rounded-full border border-border-primary ${
                                t.type === 'dark' ? 'bg-gray-900' : 'bg-white'
                            }`}></span>
                            {t.name}
                        </span>
                        {theme === t.id && <Check size={14} />}
                    </button>
                ))}
            </div>
        </div>
      )}
    </div>
  );
}
