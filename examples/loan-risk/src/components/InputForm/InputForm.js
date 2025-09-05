import React from 'react';
import './InputForm.css';

const InputForm = ({
  inputValue,
  setInputValue,
  onSubmit,
  onKeyPress,
  isLoading,
  inputRef,
  fileInputRef,
  onFileSelect,
  onOpenFileDialog,
  placeholder = "Ask anything",
  className = ""
}) => {
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
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={onKeyPress}
          placeholder={placeholder}
          className="message-input"
          disabled={isLoading}
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
