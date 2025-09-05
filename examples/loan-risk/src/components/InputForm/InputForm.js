import React from 'react';
import './InputForm.css';

const InputForm = ({
  inputValue,
  setInputValue,
  onSubmit,
  onKeyPress,
  onToggleRecording,
  isRecording,
  isLoading,
  inputRef,
  placeholder = "Ask anything",
  className = ""
}) => {
  return (
    <form onSubmit={onSubmit} className={`input-form ${className}`}>
      <div className="input-container">
        <button type="button" className="attach-button">
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
        <div className="input-actions">
          <button
            type="button"
            className={`voice-button ${isRecording ? 'recording' : ''}`}
            onClick={onToggleRecording}
            disabled={isLoading}
          >
            <span className="material-icons">mic</span>
          </button>
          <button
            type="button"
            className="wave-button"
            disabled={isLoading}
          >
            <span className="material-icons">graphic_eq</span>
          </button>
        </div>
      </div>
    </form>
  );
};

export default InputForm;
