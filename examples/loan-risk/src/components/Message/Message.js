import React from 'react';
import './Message.css';

const Message = ({ message }) => {
  const { text, sender, timestamp, isStreaming } = message;

  return (
    <div className={`message ${sender}`}>
      <div className="message-content">
        <div className="message-text">
          {text}
          {isStreaming && <span className="streaming-cursor">|</span>}
        </div>
        <div className="message-time">{timestamp}</div>
      </div>
    </div>
  );
};

export default Message;
