import React from 'react';
import InputForm from '../InputForm/InputForm';
import FilePreview from '../FilePreview/FilePreview';
import './WelcomeSection.css';

const WelcomeSection = ({ 
  inputValue, 
  setInputValue, 
  onSubmit, 
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
      <h2 className="welcome-title">Apply for a loan</h2>
      <p className="welcome-description">Upload your ID, payslip, and bank statement to apply for a loan in seconds</p>
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
        selectedFiles={selectedFiles}
        placeholder="Ask anything"
        className="centered-input-form"
      />
    </div>
  );
};

export default WelcomeSection;
