/**
 * SourceCitation Component
 * Displays document sources below AI responses.
 * Per spec: "Sources: employee_handbook.pdf — Page 12"
 */

import { DocIcon, PdfIcon, WordIcon, TxtIcon, ClipIcon } from './Icons';

export default function SourceCitation({ sources }) {
  if (!sources || sources.length === 0) return null;

  const getDocIcon = (filename = '') => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <PdfIcon size={12} />;
    if (ext === 'docx' || ext === 'doc') return <WordIcon size={12} />;
    if (ext === 'txt') return <TxtIcon size={12} />;
    return <DocIcon size={12} />;
  };

  return (
    <div className="source-citation">
      <div className="source-citation-title">
        <ClipIcon size={12} style={{ color: 'var(--accent-cyan)' }} />
        Sources
      </div>
      {sources.map((source, i) => (
        <div key={i} className="source-item">
          <span className="source-item-icon">{getDocIcon(source.filename)}</span>
          <span>
            <strong>{source.filename}</strong>
            {source.page && (
              <span style={{ color: 'var(--text-muted)', marginLeft: '6px' }}>
                — Page {source.page}
              </span>
            )}
          </span>
        </div>
      ))}
    </div>
  );
}
