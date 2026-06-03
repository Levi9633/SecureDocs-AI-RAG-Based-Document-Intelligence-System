/**
 * MessageInput Component
 * Bottom input bar per spec:
 *   Left: + upload button (PDF/DOCX/TXT)
 *   Center: Text input "Type Something"
 *   Right: Send button (arrow)
 */

import { useRef, useState } from 'react';
import { uploadDocument } from '../services/api';
import { UploadIcon, SendIcon } from './Icons';

export default function MessageInput({ onSend, onDocumentUploaded, disabled }) {
  const [text, setText] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    // Auto-resize textarea
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowed = ['.pdf', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
      alert(`Invalid file type. Please upload PDF, DOCX, or TXT files only.`);
      e.target.value = '';
      return;
    }

    setUploading(true);
    setUploadMsg(`⏳ Uploading ${file.name}...`);

    try {
      const res = await uploadDocument(file);
      setUploadMsg(`✅ ${file.name} indexed (${res.data.chunks_created} chunks)`);
      onDocumentUploaded?.();
    } catch (err) {
      const msg = err.response?.data?.error || 'Upload failed.';
      setUploadMsg(`❌ ${msg}`);
    } finally {
      setUploading(false);
      setTimeout(() => setUploadMsg(''), 4000);
      e.target.value = '';
    }
  };

  return (
    <div className="input-bar">
      {/* Upload status message */}
      {uploadMsg && (
        <div className="upload-progress" style={{ marginBottom: '10px' }}>
          {uploadMsg}
        </div>
      )}

      <div className={`input-container ${text ? 'has-text' : ''}`}>
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          id="file-upload-input"
        />

        {/* Upload (+) button */}
        <button
          id="upload-btn"
          className="upload-btn"
          onClick={handleFileClick}
          disabled={uploading}
          title="Upload document (PDF, DOCX, TXT)"
        >
          {uploading ? (
            <div className="spinner" style={{ width: '14px', height: '14px' }} />
          ) : (
            <UploadIcon size={15} style={{ color: 'var(--accent-cyan)' }} />
          )}
        </button>

        {/* Message text area */}
        <textarea
          ref={textareaRef}
          id="message-input"
          className="message-input"
          placeholder="Type something..."
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />

        {/* Send button */}
        <button
          id="send-btn"
          className="send-btn"
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          title="Send message"
        >
          <SendIcon size={15} />
        </button>
      </div>
    </div>
  );
}
