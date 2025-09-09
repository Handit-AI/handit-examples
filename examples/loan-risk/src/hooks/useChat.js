import { useState, useRef, useEffect } from 'react';

const useChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: `# Welcome to Loan Risk AI 🤖

I'm your AI-powered loan risk assessment assistant. I can analyze your financial documents to provide a comprehensive risk evaluation for your loan application.

## What I can do:
- **Document Classification**: Identify ID documents, payslips, and bank statements
- **Data Extraction**: Extract key information from your documents
- **Identity Validation**: Verify document completeness and expiry dates
- **Cross-Document Analysis**: Check consistency across multiple documents
- **Fraud Detection**: Identify potential fraud signals and financial risks
- **Risk Scoring**: Calculate a final risk score and tier (LOW/MEDIUM/HIGH)

## How to get started:
1. **Upload your documents** using the file attachment button
2. **Supported formats**: PDF, PNG, JPG, JPEG, CSV
3. **Required documents**: ID, payslip, bank statement
4. **Click send** and I'll analyze everything for you

Ready to assess your loan application? Please upload your documents below! 📄`,
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateStreaming = async (fullText) => {
    const words = fullText.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];
      
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'ai' && lastMessage.isStreaming) {
          lastMessage.text = currentText;
        }
        return newMessages;
      });
      
      // Random delay between 50-150ms per word
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
    }
    
    // Mark streaming as complete
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      if (lastMessage && lastMessage.sender === 'ai' && lastMessage.isStreaming) {
        lastMessage.isStreaming = false;
      }
      return newMessages;
    });
    
    setIsStreaming(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if ((!inputValue.trim() && selectedFiles.length === 0) || isLoading || isStreaming) return;

    const userInput = inputValue || "Please assess my loan application";
    const attachedFiles = [...selectedFiles];
    const userMessage = {
      id: Date.now(),
      text: userInput,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
      files: attachedFiles
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSelectedFiles([]); // Clear selected files after sending
    setIsLoading(true);

    // Show typing indicator for a brief moment before streaming
    await new Promise(resolve => setTimeout(resolve, 800));

    // Create AI message placeholder
    const aiMessage = {
      id: Date.now() + 1,
      text: '',
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true
    };

    setMessages(prev => [...prev, aiMessage]);
    setIsLoading(false);
    setIsStreaming(true);

    try {
      // Call the backend API
      const response = await callLoanRiskAPI(userInput, attachedFiles);
      await simulateStreaming(response);
      
      // Add follow-up message
      setTimeout(() => {
        const followUpMessage = {
          id: Date.now() + 2,
          text: `## Ready for Another Assessment? 🔄

If you'd like to submit additional documents or get a new assessment, simply upload your files again and I'll analyze them for you.

**Supported documents:**
- Identity documents (passport, driver's license, national ID)
- Income documents (payslips, salary statements)
- Financial documents (bank statements, transaction histories)

Upload your documents below to get started! 📄`,
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isStreaming: false
        };
        setMessages(prev => [...prev, followUpMessage]);
      }, 2000);

    } catch (error) {
      console.error('Error calling API:', error);
      const errorMessage = `## Error Processing Your Request ❌

I encountered an issue while processing your documents. This could be due to:

- **Network connectivity issues**
- **Backend service temporarily unavailable**
- **Invalid file formats**

**Please try again:**
1. Check your internet connection
2. Ensure your files are in supported formats (PDF, PNG, JPG, JPEG, CSV)
3. Try uploading your documents again

If the problem persists, please contact support.`;

      await simulateStreaming(errorMessage);
    }
  };

  const callLoanRiskAPI = async (message, files) => {
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    
    console.log('API Base URL:', API_BASE_URL);
    console.log('Sending message:', message);
    console.log('Files:', files.map(f => ({ name: f.name, size: f.size, type: f.type })));
    
    // Validate files before sending
    const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'csv'];
    const MAX_FILE_SIZE_MB = 10;
    const MAX_FILES = 6;
    
    if (files.length > MAX_FILES) {
      throw new Error(`Too many files. Maximum ${MAX_FILES} allowed`);
    }
    
    for (const file of files) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(extension)) {
        throw new Error(`File ${file.name} has unsupported format. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`);
      }
      
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        throw new Error(`File ${file.name} exceeds maximum size of ${MAX_FILE_SIZE_MB}MB`);
      }
    }
    
    const formData = new FormData();
    formData.append('messages', JSON.stringify([{ role: 'user', content: message }]));
    
    // Add files to form data - backend expects 'files' key, not 'files[]'
    files.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('options', JSON.stringify({
      country: 'US',
      currency: 'USD'
    }));

    const response = await fetch(`${API_BASE_URL}/v1/chat/messages`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', response.status, errorText);
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    
    // Format the response based on the API structure
    const assessment = data.assessment;
    const assistantMessage = data.assistant_message;
    
    return `## Loan Risk Assessment Results 📊

${assistantMessage}

### Risk Analysis Summary
- **Risk Score**: ${assessment.risk_score}/100
- **Risk Tier**: ${assessment.risk_tier}
- **Document Types Identified**: ${Object.values(assessment.doc_types).join(', ')}

### Risk Factors
${assessment.reasons.length > 0 ? assessment.reasons.map(reason => `- ${reason}`).join('\n') : '- No significant risk factors identified'}

### Detailed Checks
${assessment.checks.map(check => 
  `- **${check.check_id}**: ${check.passed ? '✅ Passed' : '❌ Failed'} (${check.severity} severity)${check.details ? ` - ${check.details}` : ''}`
).join('\n')}

### Extracted Information
${assessment.extracted ? Object.entries(assessment.extracted).map(([key, value]) => 
  `- **${key}**: ${typeof value === 'object' ? JSON.stringify(value, null, 2) : value}`
).join('\n') : 'No additional information extracted'}

---
*Assessment completed at ${new Date().toLocaleString()}*`;
  };


  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: `# Welcome to Loan Risk AI 🤖

I'm your AI-powered loan risk assessment assistant. I can analyze your financial documents to provide a comprehensive risk evaluation for your loan application.

## What I can do:
- **Document Classification**: Identify ID documents, payslips, and bank statements
- **Data Extraction**: Extract key information from your documents
- **Identity Validation**: Verify document completeness and expiry dates
- **Cross-Document Analysis**: Check consistency across multiple documents
- **Fraud Detection**: Identify potential fraud signals and financial risks
- **Risk Scoring**: Calculate a final risk score and tier (LOW/MEDIUM/HIGH)

## How to get started:
1. **Upload your documents** using the file attachment button
2. **Supported formats**: PDF, PNG, JPG, JPEG, CSV
3. **Required documents**: ID, payslip, bank statement
4. **Click send** and I'll analyze everything for you

Ready to assess your loan application? Please upload your documents below! 📄`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString(),
        isStreaming: false
      }
    ]);
    setSelectedFiles([]);
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return {
    messages,
    inputValue,
    setInputValue,
    isLoading,
    isStreaming,
    selectedFiles,
    messagesEndRef,
    inputRef,
    fileInputRef,
    handleSubmit,
    handleFileSelect,
    removeFile,
    openFileDialog,
    clearChat
  };
};

export default useChat;
