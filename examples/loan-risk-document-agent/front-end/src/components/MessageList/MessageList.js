import React from 'react';
import Message from '../Message/Message';
import TypingIndicator from '../TypingIndicator/TypingIndicator';
import InputForm from '../InputForm/InputForm';
import FilePreview from '../FilePreview/FilePreview';
import './MessageList.css';

const MessageList = ({ 
  messages, 
  isLoading, 
  isStreaming,
  messagesEndRef,
  onSubmit,
  fileInputRef,
  onFileSelect,
  onOpenFileDialog,
  selectedFiles,
  onRemoveFile
}) => {
  return (
    <div className="chat-container">
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
      
      <div className="chat-input-section">
        <FilePreview 
          files={selectedFiles}
          onRemoveFile={onRemoveFile}
        />
        <InputForm
          onSubmit={onSubmit}
          isLoading={isLoading}
          fileInputRef={fileInputRef}
          onFileSelect={onFileSelect}
          onOpenFileDialog={onOpenFileDialog}
          selectedFiles={selectedFiles}
          className="chat-input-form"
        />
      </div>
    </div>
  );
};

export default MessageList;
