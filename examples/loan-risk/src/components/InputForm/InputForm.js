import React, { useEffect, useRef } from 'react';
import './InputForm.css';

const InputForm = ({
  inputValue,
  setInputValue,
  onSubmit,
  isLoading,
  inputRef,
  fileInputRef,
  onFileSelect,
  onOpenFileDialog,
  selectedFiles = [],
  placeholder = "Ask anything",
  className = ""
}) => {
  const textareaRef = useRef(null);

  // Auto-resize textarea based on content
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 120; // Maximum height in pixels
      const minHeight = 24; // Minimum height in pixels
      
      if (scrollHeight > maxHeight) {
        textarea.style.height = `${maxHeight}px`;
        textarea.style.overflowY = 'auto';
      } else if (scrollHeight < minHeight) {
        textarea.style.height = `${minHeight}px`;
        textarea.style.overflowY = 'hidden';
      } else {
        textarea.style.height = `${scrollHeight}px`;
        textarea.style.overflowY = 'hidden';
      }
    }
  };

  // Adjust height when input value changes
  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  // Adjust height on mount
  useEffect(() => {
    adjustTextareaHeight();
  }, []);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    adjustTextareaHeight();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && !isLoading) {
        onSubmit(e);
      }
    }
  };
  return (
    <form onSubmit={onSubmit} className={`input-form ${className}`}>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={onFileSelect}
        style={{ display: 'none' }}
        accept="*/*"
      />
      <div className="input-container">
        <button 
          type="button" 
          className="attach-button"
          onClick={onOpenFileDialog}
          title="Attach files"
        >
          <span className="material-icons">add</span>
        </button>
        <textarea
          ref={(el) => {
            inputRef.current = el;
            textareaRef.current = el;
          }}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="message-input"
          disabled={isLoading}
          rows={1}
        />
        <button
          type="submit"
          className={`send-button ${selectedFiles.length > 0 ? 'has-files' : ''}`}
          disabled={isLoading || (!inputValue.trim() && selectedFiles.length === 0)}
        >
          <span className="material-icons">send</span>
        </button>
      </div>
    </form>
  );
};

export default InputForm;
