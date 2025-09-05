import React from 'react';
import './Header.css';

const Header = ({ theme, toggleTheme, onClearChat }) => {
  return (
    <header className="header">
      <div className="header-right">
        <button 
          className="theme-toggle" 
          onClick={toggleTheme} 
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          <span className="material-icons">
            {theme === 'dark' ? 'light_mode' : 'dark_mode'}
          </span>
        </button>
        <button 
          className="header-button" 
          onClick={onClearChat} 
          title="Clear chat"
        >
          <span className="material-icons">refresh</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
