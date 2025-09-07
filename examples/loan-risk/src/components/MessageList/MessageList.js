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
  inputValue,
  setInputValue,
  onSubmit,
  inputRef,
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
          inputValue={inputValue}
          setInputValue={setInputValue}
          onSubmit={onSubmit}
          isLoading={isLoading}
          inputRef={inputRef}
          fileInputRef={fileInputRef}
          onFileSelect={onFileSelect}
          onOpenFileDialog={onOpenFileDialog}
          placeholder="Ask anything"
          className="chat-input-form"
        />
      </div>
    </div>
  );
};

export default MessageList;
