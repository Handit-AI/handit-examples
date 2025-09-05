import React from 'react';
import InputForm from '../InputForm/InputForm';
import './WelcomeSection.css';

const WelcomeSection = ({ 
  inputValue, 
  setInputValue, 
  onSubmit, 
  onKeyPress, 
  onToggleRecording, 
  isRecording, 
  isLoading, 
  inputRef 
}) => {
  return (
    <div className="welcome-section">
      <h2 className="welcome-title">What can I help with?</h2>
      <InputForm
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSubmit={onSubmit}
        onKeyPress={onKeyPress}
        onToggleRecording={onToggleRecording}
        isRecording={isRecording}
        isLoading={isLoading}
        inputRef={inputRef}
        placeholder="Ask anything"
        className="centered-input-form"
      />
    </div>
  );
};

export default WelcomeSection;
