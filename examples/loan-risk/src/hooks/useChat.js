import { useState, useRef, useEffect } from 'react';

const useChat = () => {
  const [messages, setMessages] = useState([]);
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
    if (!inputValue.trim() || isLoading || isStreaming) return;

    const userInput = inputValue;
    const userMessage = {
      id: Date.now(),
      text: userInput,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
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

    // Simulate streaming response
    const fullResponse = `I understand you're asking about "${userInput}". This is a simulated streaming response where text appears word by word to create a more realistic chat experience. How can I help you with that?`;
    
    await simulateStreaming(fullResponse);
  };


  const clearChat = () => {
    setMessages([]);
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
