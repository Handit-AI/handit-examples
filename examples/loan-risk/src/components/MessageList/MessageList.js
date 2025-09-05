import React from 'react';
import Message from '../Message/Message';
import TypingIndicator from '../TypingIndicator/TypingIndicator';
import './MessageList.css';

const MessageList = ({ messages, isLoading, messagesEndRef }) => {
  return (
    <div className="messages-container">
      {messages.map((message) => (
        <Message
          key={message.id}
          message={message}
        />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
