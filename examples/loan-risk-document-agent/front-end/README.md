# QuickLoan

A modern, responsive loan application interface built with React and best practices. Upload your ID, payslip, and bank statement to apply for a loan in seconds.

## Features

- **Modern UI/UX**: Sleek interface with gradient backgrounds and smooth animations
- **File Upload Support**: Drag-and-drop file uploads with image previews
- **Real-time Chat**: Interactive messaging with AI loan application assessment
- **Markdown Support**: Rich text formatting with syntax highlighting for code blocks
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Fixed Header**: Clickable "QuickLoan" title for easy navigation
- **File Attachment Display**: Horizontal file previews in chat messages
- **Image Preview Modal**: Full-screen image viewing with minimalist design
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Key Loan Features

- **Document Upload**: Support for ID, payslip, bank statement and any type of files
- **File Preview**: Thumbnail previews for images and file attachments
- **Instant Processing**: Quick loan application processing with AI
- **File Management**: Easy file removal and selection before submission
- **Visual Feedback**: Clear indication of file attachments and upload status

## Best Practices Implemented

- **React Hooks**: Custom hooks for chat, theme, and state management
- **Component Architecture**: Modular, reusable component structure
- **CSS Grid/Flexbox**: Modern layout techniques with responsive design
- **Mobile-First**: Responsive design starting from mobile breakpoints
- **Performance**: Optimized animations and smooth scrolling
- **Semantic HTML**: Proper HTML structure for accessibility
- **File Handling**: Secure file upload and preview functionality

## Components

### Core Components
- **App.js**: Main application component with drag-and-drop functionality
- **Header**: Fixed header with clickable "QuickLoan" title
- **WelcomeSection**: Landing page with loan application call-to-action
- **MessageList**: Chat interface with pinned input at bottom
- **Message**: Individual message component with file display and Markdown support
- **InputForm**: Chat input with Enter key support and file attachment
- **FilePreview**: File thumbnail display with remove functionality
- **TypingIndicator**: Loading animation for AI responses

### Custom Hooks
- **useChat**: Chat state management, file handling, and message processing
- **useTheme**: Theme switching and persistence

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure API URL:
   Create a `.env` file in the root directory:
   ```bash
   # For local development
   REACT_APP_API_URL=http://localhost:5000
   
   # For production (replace with your deployed backend URL)
   # REACT_APP_API_URL=https://loan-risk-document-agent-xxxxx-uc.a.run.app
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Backend Integration

This frontend connects to the Loan Risk Document Agent backend API. Make sure your backend is running and accessible at the configured API URL.

**API Endpoint**: `POST /v1/chat/messages`
- Accepts multipart form data with messages and files
- Returns loan application assessment results
- Supports PDF, PNG, JPG, JPEG, CSV file formats

## Technologies Used

- **React 18.2.0** - Latest React with hooks and modern features
- **react-markdown 10.1.0** - Markdown rendering with GitHub Flavored Markdown
- **rehype-highlight 7.0.2** - Syntax highlighting for code blocks
- **remark-gfm 4.0.1** - GitHub Flavored Markdown support
- **CSS3** - Modern styling with gradients, backdrop-filter, and animations
- **Create React App 5.0.1** - Zero-configuration build tooling
- **ES6+** - Modern JavaScript features and async/await

## Key Features

- **Loan Application Interface**: Streamlined process for loan applications
- **File Upload & Preview**: Support for multiple file types with thumbnails
- **AI Chat Integration**: Interactive chat for loan application assessment
- **Markdown Support**: Rich text formatting in chat messages
- **Code Block Highlighting**: Syntax highlighting with copy-to-clipboard functionality
- **Image Preview Modal**: Full-screen image viewing with minimalist controls
- **Responsive Design**: Seamless experience across all devices
- **Modern Design**: Clean, professional interface with smooth transitions

## Project Structure

```
src/
├── App.js                 # Main application with file drag-and-drop
├── App.css                # Global styles and theme variables
├── index.js               # React entry point
├── components/
│   ├── index.js           # Component exports
│   ├── Header/
│   │   ├── Header.js      # Fixed header with clickable title
│   │   └── Header.css     # Header styling
│   ├── WelcomeSection/
│   │   ├── WelcomeSection.js  # Landing page with loan CTA
│   │   └── WelcomeSection.css # Welcome section styling
│   ├── MessageList/
│   │   ├── MessageList.js     # Chat container with pinned input
│   │   └── MessageList.css    # Message list styling
│   ├── Message/
│   │   ├── Message.js         # Individual message with Markdown
│   │   └── Message.css        # Message and code block styling
│   ├── InputForm/
│   │   ├── InputForm.js       # Chat input with file support
│   │   └── InputForm.css      # Input form styling
│   ├── FilePreview/
│   │   ├── FilePreview.js     # File thumbnail previews
│   │   └── FilePreview.css    # File preview styling
│   └── TypingIndicator/
│       ├── TypingIndicator.js # Loading animation
│       └── TypingIndicator.css# Animation styling
├── hooks/
│   ├── index.js           # Hook exports
│   ├── useChat.js         # Chat and file management logic
│   └── useTheme.js        # Theme switching functionality
└── public/
    └── index.html         # HTML template
```

## Usage

1. **Start Application**: Navigate to the welcome page
2. **Upload Documents**: Drag and drop or select ID, payslip, and bank statement
3. **Submit Application**: Click send to process your loan application
4. **Chat Interface**: Interact with the AI for loan application assessment
5. **View Results**: Review AI responses with rich Markdown formatting

## File Support

- **Images**: PNG, JPG, JPEG with thumbnail previews
- **Documents**: PDF, DOC, DOCX and other document formats
- **Drag & Drop**: Full drag-and-drop support throughout the interface
- **File Management**: Easy file removal and selection management