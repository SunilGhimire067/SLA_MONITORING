import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export interface GlassSettings {
  blur: number;
  opacity: number;
  borderOpacity: number;
  saturation: number;
  backgroundPreset: string;
  darkMode: boolean;
  showBgImage: boolean;
  bgImageOpacity: number;
}

const DEFAULT_SETTINGS: GlassSettings = {
  blur: 20,
  opacity: 0.1,
  borderOpacity: 0.15,
  saturation: 1.8,
  backgroundPreset: 'devops',
  darkMode: true,
  showBgImage: true,
  bgImageOpacity: 0.15,
};

const BACKGROUND_PRESETS: Record<string, string> = {
  devops: 'linear-gradient(135deg, #0d0b2e 0%, #1a1154 30%, #2d1b69 60%, #1a1040 100%)',
  aurora: 'linear-gradient(135deg, #0f0c29 0%, #302b63 40%, #24243e 100%)',
  ocean: 'linear-gradient(135deg, #0c1445 0%, #152a5c 40%, #0d2137 100%)',
  midnight: 'linear-gradient(135deg, #080818 0%, #141428 40%, #1a1a3e 100%)',
  cosmic: 'linear-gradient(135deg, #12002e 0%, #3d0066 40%, #1a0033 100%)',
  emerald: 'linear-gradient(135deg, #021a0a 0%, #0a3a2e 40%, #062017 100%)',
  slate: 'linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #0f172a 100%)',
};

interface ThemeContextType {
  settings: GlassSettings;
  updateSettings: (partial: Partial<GlassSettings>) => void;
  resetSettings: () => void;
  backgroundPresets: Record<string, string>;
  getBackground: () => string;
}

const ThemeContext = createContext<ThemeContextType>({
  settings: DEFAULT_SETTINGS,
  updateSettings: () => {},
  resetSettings: () => {},
  backgroundPresets: BACKGROUND_PRESETS,
  getBackground: () => BACKGROUND_PRESETS.devops,
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<GlassSettings>(() => {
    const stored = localStorage.getItem('glass_settings');
    return stored ? { ...DEFAULT_SETTINGS, ...JSON.parse(stored) } : DEFAULT_SETTINGS;
  });

  const updateSettings = useCallback((partial: Partial<GlassSettings>) => {
    setSettings(prev => {
      const next = { ...prev, ...partial };
      localStorage.setItem('glass_settings', JSON.stringify(next));
      return next;
    });
  }, []);

  const resetSettings = useCallback(() => {
    localStorage.removeItem('glass_settings');
    setSettings(DEFAULT_SETTINGS);
  }, []);

  const getBackground = useCallback(() => {
    return BACKGROUND_PRESETS[settings.backgroundPreset] || BACKGROUND_PRESETS.devops;
  }, [settings.backgroundPreset]);

  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--glass-blur', `${settings.blur}px`);
    root.style.setProperty('--glass-opacity', `${settings.opacity}`);
    root.style.setProperty('--glass-border-opacity', `${settings.borderOpacity}`);
    root.style.setProperty('--glass-saturation', `${settings.saturation}`);
    root.style.setProperty('--glass-bg', `rgba(255, 255, 255, ${settings.opacity})`);
    root.style.setProperty('--glass-bg-hover', `rgba(255, 255, 255, ${Math.min(settings.opacity + 0.05, 0.4)})`);
    root.style.setProperty('--glass-border', `rgba(255, 255, 255, ${settings.borderOpacity})`);
    root.style.setProperty('--glass-shadow', `0 8px 32px rgba(0, 0, 0, 0.2)`);
    root.style.setProperty('--app-bg', getBackground());
  }, [settings, getBackground]);

  return (
    <ThemeContext.Provider value={{ settings, updateSettings, resetSettings, backgroundPresets: BACKGROUND_PRESETS, getBackground }}>
      {children}
    </ThemeContext.Provider>
  );
};
