import React, { useState } from 'react';
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

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
      
      {/* AI Details Sidebar */}
      <div className={`ai-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="ai-sidebar-content">
          <div className="ai-sidebar-header">
            <h3 className="ai-sidebar-title">¿Cómo funciona?</h3>
            <button className="ai-sidebar-close" onClick={toggleSidebar}>
              <span className="material-icons">close</span>
            </button>
          </div>
          <div className="ai-sidebar-body">
            <p className="ai-assessment-text">
              This AI agent analyzes your ID, payslip, and bank statement, extracting structured fields such as name, SSN, income, and bank balance. It then applies rules to classify risk:
            </p>
            <ul className="ai-rules-list">
              <li>Income below threshold → <span className="risk-high">High Risk</span></li>
              <li>Inconsistent balances → <span className="risk-fraud">Potential Fraud</span></li>
              <li>Missing SSN → <span className="risk-invalid">Invalid Application</span></li>
            </ul>
            <p className="ai-assessment-conclusion">
              Finally, it determines whether your loan is approved or rejected.
            </p>
          </div>
        </div>
      </div>
      
      {/* Sidebar Toggle Button */}
      <button className="ai-sidebar-toggle" onClick={toggleSidebar}>
        <span className="material-icons">info</span>
      </button>
    </div>
  );
};

export default WelcomeSection;
