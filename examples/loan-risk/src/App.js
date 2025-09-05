import React from 'react';
import { useTheme, useChat } from './hooks';
import { Header, WelcomeSection, MessageList } from './components';
import './App.css';

const App = () => {
  const { theme, toggleTheme } = useTheme();
  const {
    messages,
    inputValue,
    setInputValue,
    isLoading,
    isRecording,
    messagesEndRef,
    inputRef,
    handleSubmit,
    handleKeyPress,
    toggleRecording,
    clearChat
  } = useChat();

  return (
    <div className="app">
      <Header 
        theme={theme}
        toggleTheme={toggleTheme}
        onClearChat={clearChat}
      />

      <main className="main-content">
        {messages.length === 0 ? (
          <WelcomeSection
            inputValue={inputValue}
            setInputValue={setInputValue}
            onSubmit={handleSubmit}
            onKeyPress={handleKeyPress}
            onToggleRecording={toggleRecording}
            isRecording={isRecording}
            isLoading={isLoading}
            inputRef={inputRef}
          />
        ) : (
          <MessageList
            messages={messages}
            isLoading={isLoading}
            messagesEndRef={messagesEndRef}
          />
        )}
      </main>
    </div>
  );
};

export default App;
