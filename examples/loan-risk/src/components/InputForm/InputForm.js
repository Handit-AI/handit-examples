import React, { useEffect, useRef } from 'react';
import './InputForm.css';

const InputForm = ({
  onSubmit,
  isLoading,
  fileInputRef,
  onFileSelect,
  onOpenFileDialog,
  selectedFiles = [],
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
        accept=".pdf,.png,.jpg,.jpeg,.csv"
      />
      <div className="input-container file-only">
        <button 
          type="button" 
          className="attach-button"
          onClick={onOpenFileDialog}
          title="Upload documents for loan assessment"
          disabled={isLoading}
        >
          <span className="material-icons">add</span>
        </button>
        <div className="file-input-placeholder">
          {selectedFiles.length > 0 ? (
            <span className="file-count">
              {selectedFiles.length} document{selectedFiles.length > 1 ? 's' : ''} selected
            </span>
          ) : (
            <span className="placeholder-text">
              Upload your documents (ID, payslip, bank statement)
            </span>
          )}
        </div>
        <button
          type="submit"
          className={`send-button ${selectedFiles.length > 0 ? 'has-files' : ''}`}
          disabled={isLoading || selectedFiles.length === 0}
          title="Submit documents for loan assessment"
        >
          <span className="material-icons">send</span>
        </button>
      </div>
    </form>
  );
};

export default InputForm;
