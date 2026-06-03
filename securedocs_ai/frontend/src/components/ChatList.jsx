/**
 * ChatList Component
 * Sidebar Section 3 per spec:
 *   - Chat title + last updated time
 *   - Open chat (click)
 *   - Rename chat (pencil button)
 *   - Delete chat (trash button)
 */

import { useState } from 'react';
import { renameChat, deleteChat } from '../services/api';
import { PencilIcon, TrashIcon, SparkleIcon } from './Icons';

function formatTime(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export default function ChatList({ chats, activeChatId, onSelect, onRefresh }) {
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState('');

  const handleRenameStart = (e, chat) => {
    e.stopPropagation();
    setRenamingId(chat.id);
    setRenameValue(chat.title);
  };

  const handleRenameSubmit = async (chatId) => {
    if (!renameValue.trim()) {
      setRenamingId(null);
      return;
    }
    try {
      await renameChat(chatId, renameValue.trim());
      onRefresh?.();
    } catch {
      alert('Failed to rename chat.');
    } finally {
      setRenamingId(null);
    }
  };

  const handleDelete = async (e, chatId) => {
    e.stopPropagation();
    if (!window.confirm('Delete this chat and all its messages?')) return;
    try {
      await deleteChat(chatId);
      onRefresh?.();
    } catch {
      alert('Failed to delete chat.');
    }
  };

  if (chats.length === 0) {
    return (
      <div className="chat-list" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: 'var(--text-muted)', fontSize: '12px', textAlign: 'center', padding: '20px' }}>
          <div style={{ fontSize: '20px', marginBottom: '8px', opacity: 0.6 }}>💬</div>
          No chats yet.<br />Click <strong>New Chat</strong> to start.
        </div>
      </div>
    );
  }

  return (
    <div className="chat-list">
      <div className="sidebar-section-title" style={{ padding: '4px 6px 12px' }}>
        <SparkleIcon size={12} style={{ color: 'var(--accent-purple)' }} />
        Recent Chats
      </div>
      {chats.map((chat, idx) => (
        <div
          key={chat.id}
          id={`chat-item-${chat.id}`}
          className={`chat-item ${activeChatId === chat.id ? 'active' : ''}`}
          style={{ animationDelay: `${idx * 0.05}s` }}
          onClick={() => renamingId !== chat.id && onSelect(chat.id)}
        >
          {renamingId === chat.id ? (
            <input
              className="rename-input"
              value={renameValue}
              autoFocus
              onChange={(e) => setRenameValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRenameSubmit(chat.id);
                if (e.key === 'Escape') setRenamingId(null);
              }}
              onBlur={() => handleRenameSubmit(chat.id)}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <>
              <div className="chat-item-info">
                <div className="chat-item-title">{chat.title}</div>
                <div className="chat-item-time">{formatTime(chat.updated_at)}</div>
              </div>
              <div className="chat-item-actions">
                <button
                  id={`rename-chat-${chat.id}`}
                  className="chat-action-btn"
                  onClick={(e) => handleRenameStart(e, chat)}
                  title="Rename chat"
                >
                  <PencilIcon size={12} />
                </button>
                <button
                  id={`delete-chat-${chat.id}`}
                  className="chat-action-btn delete"
                  onClick={(e) => handleDelete(e, chat.id)}
                  title="Delete chat"
                >
                  <TrashIcon size={12} />
                </button>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
