import React from 'react';
import InputForm from '../InputForm/InputForm';
import FilePreview from '../FilePreview/FilePreview';
import './WelcomeSection.css';

const WelcomeSection = ({ 
  inputValue, 
  setInputValue, 
  onSubmit, 
  onKeyPress, 
  isLoading, 
  inputRef,
  fileInputRef,
  onFileSelect,
  onOpenFileDialog,
  selectedFiles,
  onRemoveFile
}) => {
  return (
    <div className="welcome-section">
      <h2 className="welcome-title">What can I help with?</h2>
      <FilePreview 
        files={selectedFiles}
        onRemoveFile={onRemoveFile}
      />
      <InputForm
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSubmit={onSubmit}
        onKeyPress={onKeyPress}
        isLoading={isLoading}
        inputRef={inputRef}
        fileInputRef={fileInputRef}
        onFileSelect={onFileSelect}
        onOpenFileDialog={onOpenFileDialog}
        placeholder="Ask anything"
        className="centered-input-form"
      />
    </div>
  );
};

export default WelcomeSection;
