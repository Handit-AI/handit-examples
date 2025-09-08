import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import './Message.css';
import 'highlight.js/styles/github-dark.css';

const Message = ({ message }) => {
  const { text, sender, timestamp, isStreaming, files = [] } = message;
  const [selectedImage, setSelectedImage] = useState(null);

  return (
    <div className={`message ${sender}`}>
      {files.length > 0 && (
        <div className="message-files-container">
          <div className="message-files">
            {files.map((file, index) => (
              <div key={index} className="message-file">
                <div className="file-preview">
                  {file.type?.startsWith('image/') ? (
                    <img 
                      src={URL.createObjectURL(file)} 
                      alt={file.name}
                      onClick={() => setSelectedImage(URL.createObjectURL(file))}
                      style={{ cursor: 'pointer' }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className="file-icon" style={{ display: file.type?.startsWith('image/') ? 'none' : 'flex' }}>
                    <span className="material-icons">
                      {file.type?.startsWith('image/') ? 'image' : 'description'}
                    </span>
                  </div>
                </div>
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {text ? (
        <>
          <div className="message-content">
            <div className="message-text">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <pre className="code-block">
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    ) : (
                      <code className="inline-code" {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre({ children }) {
                    return <div className="code-wrapper">{children}</div>;
                  }
                }}
              >
                {text}
              </ReactMarkdown>
              {isStreaming && <span className="streaming-cursor">|</span>}
            </div>
          </div>
          {sender === 'user' ? (
            <div className="message-time-only">{timestamp}</div>
          ) : (
            <div className="message-time">{timestamp}</div>
          )}
        </>
      ) : (
        <div className="message-time-only">{timestamp}</div>
      )}
      
      {/* Image Preview Modal */}
      {selectedImage && (
        <div className="image-preview-modal" onClick={() => setSelectedImage(null)}>
          <div className="image-preview-content" onClick={(e) => e.stopPropagation()}>
            <button 
              className="image-preview-close"
              onClick={() => setSelectedImage(null)}
            >
              <span className="material-icons">close</span>
            </button>
            <img 
              src={selectedImage} 
              alt="Preview" 
              className="image-preview-large"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Message;
