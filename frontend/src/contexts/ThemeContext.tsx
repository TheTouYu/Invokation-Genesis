// contexts/ThemeContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { ThemeType, lightTheme, darkTheme, eyeCareTheme, ThemeColors } from '../types/theme';

interface ThemeContextType {
  theme: ThemeType;
  themeColors: ThemeColors;
  toggleTheme: (theme: ThemeType) => void;
}

const getThemeColors = (theme: ThemeType): ThemeColors => {
  switch (theme) {
    case 'light':
      return lightTheme;
    case 'dark':
      return darkTheme;
    case 'eye-care':
      return eyeCareTheme;
    default:
      return darkTheme;
  }
};

const getInitialTheme = (): ThemeType => {
  const savedTheme = localStorage.getItem('theme') as ThemeType | null;
  if (savedTheme && ['light', 'dark', 'eye-care'].includes(savedTheme)) {
    return savedTheme;
  }
  return 'dark'; // 默认主题
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<ThemeType>(getInitialTheme());
  const [themeColors, setThemeColors] = useState<ThemeColors>(getThemeColors(theme));

  useEffect(() => {
    const colors = getThemeColors(theme);
    setThemeColors(colors);
    localStorage.setItem('theme', theme);
    
    // 更新根元素的自定义属性，便于CSS使用
    const root = document.documentElement;
    root.style.setProperty('--background', colors.background);
    root.style.setProperty('--card-background', colors.cardBackground);
    root.style.setProperty('--container-background', colors.containerBackground);
    root.style.setProperty('--text-primary', colors.textPrimary);
    root.style.setProperty('--text-secondary', colors.textSecondary);
    root.style.setProperty('--text-header', colors.textHeader);
    root.style.setProperty('--accent', colors.accent);
    root.style.setProperty('--accent-secondary', colors.accentSecondary);
    root.style.setProperty('--border', colors.border);
  }, [theme]);

  const toggleTheme = (newTheme: ThemeType) => {
    setTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, themeColors, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};