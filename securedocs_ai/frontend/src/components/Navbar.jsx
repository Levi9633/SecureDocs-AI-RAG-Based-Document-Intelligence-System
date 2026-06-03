/**
 * Navbar Component
 * TOP BAR per spec:
 *   Left: Logo (central premium SVG)
 *   Center: "Levi AI" gradient title
 *   Right: More Options dropdown (Clear Documents, Export Chat, Settings, About)
 */

import { useState, useRef, useEffect } from 'react';
import { deleteDocument, listDocuments } from '../services/api';
import { LogoIcon, TrashIcon, UploadIcon, SettingsIcon, InfoIcon } from './Icons';

export default function Navbar({ onClearDocuments }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleClearDocuments = async () => {
    setOpen(false);
    if (!window.confirm('Clear all uploaded documents? This will also remove them from the AI index.')) return;
    try {
      const res = await listDocuments();
      const docs = res.data;
      await Promise.all(docs.map(d => deleteDocument(d.id)));
      onClearDocuments?.();
    } catch {
      alert('Failed to clear documents.');
    }
  };

  const handleExportChat = () => {
    setOpen(false);
    // Export current chat messages as text
    const messages = document.querySelectorAll('.message-bubble');
    let text = '';
    messages.forEach(m => { text += m.textContent + '\n\n'; });
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'levi-ai-chat-export.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <nav className="navbar">
      {/* Left: Logo */}
      <div className="navbar-logo">
        <div className="navbar-logo-icon">
          <LogoIcon size={18} />
        </div>
        <span style={{ fontSize: '13.5px', color: '#ffffff', fontWeight: 800, letterSpacing: '0.5px' }}>
          SECUREDOCS
        </span>
      </div>

      {/* Center: Title */}
      <span className="navbar-title">Levi AI</span>

      {/* Right: More Options */}
      <div className="navbar-more" ref={dropdownRef}>
        <button
          id="navbar-more-btn"
          className="navbar-more-btn"
          onClick={() => setOpen(o => !o)}
        >
          <SettingsIcon size={14} />
          More Options
          <span style={{ fontSize: '8px', opacity: 0.7, marginLeft: '2px' }}>▼</span>
        </button>

        {open && (
          <div className="navbar-dropdown">
            <button
              id="menu-clear-docs"
              className="navbar-dropdown-item danger"
              onClick={handleClearDocuments}
            >
              <TrashIcon size={14} />
              Clear Documents
            </button>
            <button
              id="menu-export"
              className="navbar-dropdown-item"
              onClick={handleExportChat}
            >
              <UploadIcon size={14} style={{ transform: 'rotate(180deg)' }} />
              Export Chat
            </button>
            <button
              id="menu-settings"
              className="navbar-dropdown-item"
              onClick={() => { setOpen(false); alert('Settings coming soon!'); }}
            >
              <SettingsIcon size={14} />
              Settings
            </button>
            <button
              id="menu-about"
              className="navbar-dropdown-item"
              onClick={() => { setOpen(false); alert('Levi AI — RAG-powered Document Intelligence System\nBuilt with Django + React + Gemini + FAISS'); }}
            >
              <InfoIcon size={14} />
              About
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
