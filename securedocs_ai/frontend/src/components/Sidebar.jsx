/**
 * Sidebar Component
 * Full sidebar layout per spec:
 *   Section 1: DocumentList (uploaded docs)
 *   Section 2: New Chat button (smart sparkle icon)
 *   Section 3: ChatList (history)
 *   Section 4: UserProfile (username Shivu at bottom)
 */

import { useState, useEffect, useCallback } from 'react';
import DocumentList from './DocumentList';
import ChatList from './ChatList';
import { SparkleIcon } from './Icons';
import {
  listDocuments,
  listChats,
  createChat,
  summarizeChat,
} from '../services/api';

export default function Sidebar({ activeChatId, onChatSelect, onChatCreated, refreshTrigger }) {
  const [documents, setDocuments] = useState([]);
  const [chats, setChats] = useState([]);
  const [newChatLoading, setNewChatLoading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const docsRes = await listDocuments();
      setDocuments(docsRes.data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }

    try {
      const chatsRes = await listChats();
      setChats(chatsRes.data);
    } catch (err) {
      console.error('Failed to load chats:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData, refreshTrigger]);

  const handleNewChat = async () => {
    if (newChatLoading) return;
    setNewChatLoading(true);

    try {
      // Step 1+2: Summarize current chat (long-term memory) if exists
      if (activeChatId) {
        try {
          await summarizeChat(activeChatId);
        } catch {
          // Non-critical — continue even if summarization fails
        }
      }

      // Step 3+4: Create new chat and open it
      const res = await createChat('New Chat');
      const newChat = res.data;

      // Refresh sidebar + navigate to new chat
      await loadData();
      onChatCreated?.(newChat.id);
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to create new chat.');
    } finally {
      setNewChatLoading(false);
    }
  };

  return (
    <aside className="sidebar glass-panel">
      {/* Section 1: Document List */}
      <DocumentList
        documents={documents}
        onDelete={loadData}
      />

      {/* Section 2: New Chat Button */}
      <div style={{ padding: '0 16px', marginTop: '6px' }}>
        <button
          id="new-chat-btn"
          className="new-chat-btn"
          onClick={handleNewChat}
          disabled={newChatLoading}
        >
          {newChatLoading ? (
            <>
              <div className="spinner" style={{ width: '14px', height: '14px' }} />
              Saving...
            </>
          ) : (
            <>
              <SparkleIcon size={15} />
              New Chat
            </>
          )}
        </button>
      </div>

      {/* Section 3: Chat History List */}
      <ChatList
        chats={chats}
        activeChatId={activeChatId}
        onSelect={onChatSelect}
        onRefresh={loadData}
      />

      {/* Section 4: User Profile (Shivakumar / Shivu) */}
      <div className="user-profile">
        <div className="user-avatar">S</div>
        <span className="user-name">Shivu</span>
      </div>
    </aside>
  );
}
