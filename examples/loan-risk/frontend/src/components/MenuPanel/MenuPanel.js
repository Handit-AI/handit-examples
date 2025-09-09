import React, { useState } from 'react';
import './MenuPanel.css';

const MenuPanel = ({ onSidebarToggle }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    const newState = !isSidebarOpen;
    setIsSidebarOpen(newState);
    if (onSidebarToggle) {
      onSidebarToggle(newState);
    }
  };

  return (
    <div className={`ai-sidebar ${isSidebarOpen ? 'open' : ''}`}>
      {/* Hamburger button - always visible when closed */}
      <button 
        className="menu-panel-toggle" 
        onClick={toggleSidebar}
        title="Menu"
      >
        <span className="material-icons">menu</span>
      </button>

      {/* Sidebar content - only visible when open */}
      <div className="ai-sidebar-content">
        <div className="ai-sidebar-header">
          <h3 className="ai-sidebar-title">How does it work?</h3>
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
  );
};

export default MenuPanel;
