// types/theme.ts
export type ThemeType = 'light' | 'dark' | 'eye-care';

export interface ThemeColors {
  // 背景颜色
  background: string;
  cardBackground: string;
  containerBackground: string;
  
  // 文字颜色
  textPrimary: string;
  textSecondary: string;
  textHeader: string;
  
  // 强调色
  accent: string;
  accentSecondary: string;
  
  // 边框颜色
  border: string;
  
  // 特殊颜色
  success: string;
  warning: string;
  error: string;
}

export const lightTheme: ThemeColors = {
  background: 'linear-gradient(135deg, #e0eafc, #cfdef3)',
  cardBackground: '#ffffff',
  containerBackground: 'rgba(255, 255, 255, 0.9)',
  textPrimary: '#333333',
  textSecondary: '#666666',
  textHeader: '#1a2a6c',
  accent: '#1a2a6c',
  accentSecondary: '#b21f1f',
  border: '#cccccc',
  success: '#2ecc71',
  warning: '#f1c40f',
  error: '#e74c3c'
};

export const darkTheme: ThemeColors = {
  background: 'linear-gradient(135deg, #1a2a6c, #b21f1f, #1a2a6c)',
  cardBackground: 'rgba(30, 30, 40, 0.9)',
  containerBackground: 'rgba(0, 0, 0, 0.7)',
  textPrimary: '#ffffff',
  textSecondary: '#cccccc',
  textHeader: '#ffd700',
  accent: '#ffd700',
  accentSecondary: '#ff8c00',
  border: '#444444',
  success: '#2ecc71',
  warning: '#f1c40f',
  error: '#e74c3c'
};

export const eyeCareTheme: ThemeColors = {
  background: 'linear-gradient(135deg, #d9e4c9, #a3b18a, #d9e4c9)',
  cardBackground: '#e9f5db',
  containerBackground: 'rgba(233, 245, 219, 0.9)',
  textPrimary: '#3a4a3f',
  textSecondary: '#5a6a5f',
  textHeader: '#2d5016',
  accent: '#2d5016',
  accentSecondary: '#517c3a',
  border: '#a3b18a',
  success: '#517c3a',
  warning: '#bca635',
  error: '#a64942'
};