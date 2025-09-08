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
    if ((!inputValue.trim() && selectedFiles.length === 0) || isLoading || isStreaming) return;

    const userInput = inputValue;
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

    // Generate response with Markdown examples
    const markdownExamples = [
      `## Response to: "${userInput}"

I understand your question! Here are some examples of what I can help you with using **Markdown formatting**:

### Code Examples
\`\`\`javascript
function processData(input) {
  return input.map(item => ({
    ...item,
    processed: true,
    timestamp: new Date()
  }));
}
\`\`\`

### Data Tables
| Feature | Status | Description |
|---------|--------|-------------|
| Markdown | ✅ | Full support |
| Code Highlighting | ✅ | Syntax highlighting |
| Tables | ✅ | Responsive tables |
| Lists | ✅ | Ordered & unordered |

### Key Points
- **Bold text** for emphasis
- *Italic text* for subtle emphasis
- \`inline code\` for technical terms
- [Links](https://example.com) for references

> **Note:** This is a simulated response with streaming text to demonstrate the chat interface capabilities.

How else can I assist you?`,

      `## Analysis: "${userInput}"

Great question! Let me break this down with some **structured information**:

### Overview
Your query involves several important aspects that I can help clarify.

### Technical Details
\`\`\`python
def analyze_query(query):
    """Process and analyze user queries"""
    keywords = extract_keywords(query)
    context = determine_context(keywords)
    return generate_response(context)
\`\`\`

### Implementation Steps
1. **First**, identify the core requirements
2. **Then**, break down into smaller tasks
3. **Finally**, implement and test

### Resources
- [Documentation](https://docs.example.com)
- [API Reference](https://api.example.com)
- [Community Forum](https://community.example.com)

> **Tip:** Feel free to ask for more specific details about any of these points!`,

      `## Solution for: "${userInput}"

Here's a comprehensive approach to your question:

### Quick Answer
The solution involves **three main components**:

1. **Setup** - Initial configuration
2. **Implementation** - Core functionality  
3. **Testing** - Validation and verification

### Code Implementation
\`\`\`typescript
interface SolutionConfig {
  enabled: boolean;
  timeout: number;
  retries: number;
}

class SolutionProcessor {
  constructor(private config: SolutionConfig) {}
  
  async process(input: string): Promise<string> {
    // Implementation details here
    return processedInput;
  }
}
\`\`\`

### Configuration Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| \`enabled\` | boolean | true | Enable processing |
| \`timeout\` | number | 5000 | Timeout in ms |
| \`retries\` | number | 3 | Max retry attempts |

### Next Steps
- Review the configuration
- Test with sample data
- Monitor performance metrics

**Need more details?** Just ask!`
    ];

    // Select a random example
    const randomExample = markdownExamples[Math.floor(Math.random() * markdownExamples.length)];
    
    await simulateStreaming(randomExample);
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
