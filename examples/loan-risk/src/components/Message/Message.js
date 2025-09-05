import React from 'react';
import './Message.css';

const Message = ({ message }) => {
  const { text, sender, timestamp } = message;

  return (
    <div className={`message ${sender}`}>
      <div className="message-content">
        <div className="message-text">{text}</div>
        <div className="message-time">{timestamp}</div>
      </div>
    </div>
  );
};

export default Message;
