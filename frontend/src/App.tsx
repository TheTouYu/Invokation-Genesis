import React from 'react';
import AppRouter from './router';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';
import ThemeToggle from './components/ThemeToggle/ThemeToggle';

function App() {
  return (
    <ThemeProvider>
      <div className="App">
        <ThemeToggle />
        <AppRouter />
      </div>
    </ThemeProvider>
  );
}

export default App;
