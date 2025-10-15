import React, { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import '../../App.css'; // 确保导入相关样式

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [showDropdown, setShowDropdown] = useState(false);

  const themeOptions = [
    { id: 'light', name: '白天模式' },
    { id: 'dark', name: '黑夜模式' },
    { id: 'eye-care', name: '护眼模式' }
  ];

  const currentThemeName = themeOptions.find(option => option.id === theme)?.name || '主题';

  // 点击外部区域关闭下拉菜单
  const handleClickOutside = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('.theme-section') && !target.closest('.theme-toggle')) {
      setShowDropdown(false);
    }
  };

  React.useEffect(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  return (
    <div className="theme-section">
      <button 
        className="theme-toggle" 
        onClick={(e) => {
          e.stopPropagation();
          setShowDropdown(!showDropdown);
        }}
        aria-label="切换主题"
        title={currentThemeName}
      >
        {/* 使用SVG图标 */}
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
        </svg>
      </button>
      
      {showDropdown && (
        <div className="theme-dropdown">
          {themeOptions.map((option) => (
            <button
              key={option.id}
              className="theme-option"
              onClick={() => {
                toggleTheme(option.id as 'light' | 'dark' | 'eye-care');
                setShowDropdown(false);
              }}
            >
              {option.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThemeToggle;