import React from 'react';
import './TypingIndicator.css';

const TypingIndicator = () => {
  return (
    <div className="message ai">
      <div className="message-content">
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
