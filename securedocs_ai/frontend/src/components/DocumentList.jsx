/**
 * DocumentList Component
 * Sidebar Section 1 per spec:
 *   - List of uploaded documents with filename + delete button
 *   - Shows high-fidelity SVG file type icon for PDF/DOCX/TXT
 */

import { deleteDocument } from '../services/api';
import { DocIcon, PdfIcon, WordIcon, TxtIcon, TrashIcon } from './Icons';

export default function DocumentList({ documents, onDelete }) {
  const getDocIcon = (filename = '') => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <PdfIcon size={15} />;
    if (ext === 'docx' || ext === 'doc') return <WordIcon size={15} />;
    if (ext === 'txt') return <TxtIcon size={15} />;
    return <DocIcon size={15} />;
  };

  const handleDelete = async (doc) => {
    if (!window.confirm(`Delete "${doc.filename}"? This will remove it from the AI index.`)) return;
    try {
      await deleteDocument(doc.id);
      onDelete?.();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete document.');
    }
  };

  return (
    <div className="sidebar-section">
      <div className="sidebar-section-title">
        <DocIcon size={12} style={{ color: 'var(--accent-cyan)' }} />
        Documents
      </div>

      {documents.length === 0 ? (
        <div className="doc-empty">
          <div className="doc-empty-icon">
            <DocIcon size={24} />
          </div>
          <div>No documents uploaded yet.<br />Click <strong>+</strong> to upload.</div>
        </div>
      ) : (
        <div className="doc-list">
          {documents.map((doc) => (
            <div key={doc.id} className="doc-item" title={doc.filename}>
              <span className="doc-icon">{getDocIcon(doc.filename)}</span>
              <span className="doc-name">{doc.filename}</span>
              <button
                id={`delete-doc-${doc.id}`}
                className="doc-delete-btn"
                onClick={() => handleDelete(doc)}
                title={`Delete ${doc.filename}`}
              >
                <TrashIcon size={11} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
