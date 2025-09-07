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
          placeholder={placeholder}
          className="message-input"
          disabled={isLoading}
          rows={1}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputValue.trim()}
        >
          <span className="material-icons">send</span>
        </button>
      </div>
    </form>
  );
};

export default InputForm;
