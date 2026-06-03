/**
 * ChatWindow Component
 * Main chat area per spec:
 *   - Scrollable message area
 *   - Auto-scroll to bottom on new message
 *   - Typing indicator while AI responds
 *   - Scroll-to-bottom FAB button
 *   - Welcome screen when no messages
 */

import { useEffect, useRef, useState } from 'react';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { sendMessage, getMessages } from '../services/api';
import { LogoIcon, SparkleIcon, DocIcon, ArrowDownIcon } from './Icons';

export default function ChatWindow({ chatId, onDocumentUploaded, onChatUpdated }) {
  const [messages, setMessages] = useState([]);
  const [sourcesMap, setSourcesMap] = useState({}); // messageId → sources[]
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showScrollBtn, setShowScrollBtn] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesAreaRef = useRef(null);

  // Load messages when chat is selected
  useEffect(() => {
    if (!chatId) {
      setMessages([]);
      setSourcesMap({});
      return;
    }
    loadMessages();
  }, [chatId]);

  const loadMessages = async () => {
    if (!chatId) return;
    try {
      setLoading(true);
      const res = await getMessages(chatId);
      setMessages(res.data);
    } catch {
      console.error('Failed to load messages');
    } finally {
      setLoading(false);
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    const area = messagesAreaRef.current;
    if (!area) return;
    const isNearBottom = area.scrollHeight - area.scrollTop - area.clientHeight < 100;
    setShowScrollBtn(!isNearBottom);
  };

  const handleSend = async (question) => {
    if (!chatId || !question.trim()) return;

    // Optimistically add user message
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempUserMsg]);
    setIsTyping(true);

    try {
      const res = await sendMessage(chatId, question);
      const { answer, sources, message_id } = res.data;

      // Add assistant message
      const assistantMsg = {
        id: message_id,
        role: 'assistant',
        content: answer,
        timestamp: new Date().toISOString(),
        isNew: true,
      };

      setMessages(prev => [...prev, assistantMsg]);

      // Store sources for this message
      if (sources && sources.length > 0) {
        setSourcesMap(prev => ({ ...prev, [message_id]: sources }));
      }

      // Notify parent to refresh chat list (title may have changed)
      onChatUpdated?.();
    } catch (err) {
      const errMsg = err.response?.data?.error || 'Failed to get response. Please try again.';
      const errorMsg = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `⚠️ ${errMsg}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  // No chat selected
  if (!chatId) {
    return (
      <div className="chat-window">
        <div className="chat-welcome">
          <div className="welcome-logo-container">
            <div className="chat-welcome-icon">
              <LogoIcon size={38} />
            </div>
          </div>
          <h2>Welcome to Levi AI</h2>
          <p>Your intelligent document assistant powered by Gemini + FAISS RAG.</p>
          <div className="welcome-hints">
            <div className="welcome-hint">
              <div className="welcome-hint-icon">
                <DocIcon size={16} />
              </div>
              <div className="welcome-hint-title">Upload Documents</div>
              <div style={{ opacity: 0.7, marginTop: '4px' }}>Indexed vector storage for PDF, DOCX, or TXT files.</div>
            </div>
            <div className="welcome-hint">
              <div className="welcome-hint-icon">
                <SparkleIcon size={16} />
              </div>
              <div className="welcome-hint-title">Instant Conversations</div>
              <div style={{ opacity: 0.7, marginTop: '4px' }}>Start interactive chat sessions instantly by clicking New Chat.</div>
            </div>
            <div className="welcome-hint">
              <div className="welcome-hint-icon">
                <LogoIcon size={16} />
              </div>
              <div className="welcome-hint-title">Contextual Q&A</div>
              <div style={{ opacity: 0.7, marginTop: '4px' }}>Ask precise questions and retrieve answers grounded in document content.</div>
            </div>
            <div className="welcome-hint">
              <div className="welcome-hint-icon">
                <SparkleIcon size={16} style={{ color: 'var(--accent-purple)' }} />
              </div>
              <div className="welcome-hint-title">Long-Term Memory</div>
              <div style={{ opacity: 0.7, marginTop: '4px' }}>Automated summaries capture core concepts across chat threads.</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {/* Messages area */}
      <div
        id="messages-area"
        className="messages-area"
        ref={messagesAreaRef}
        onScroll={handleScroll}
      >
        {loading && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <div className="spinner" style={{ margin: '0 auto' }} />
          </div>
        )}

        {!loading && messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '36px', marginBottom: '14px', filter: 'drop-shadow(0 0 10px rgba(6, 182, 212, 0.2))' }}>💬</div>
            <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Send a message to start the conversation.</div>
            {/* Hint if no documents */}
            <div style={{ marginTop: '10px', fontSize: '12.5px', color: 'var(--text-muted)' }}>
              Tip: Upload documents using the <strong>+</strong> button below
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            sources={sourcesMap[msg.id] || []}
          />
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="message-wrapper assistant">
            <div className="typing-indicator">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Scroll to bottom button */}
      {showScrollBtn && (
        <button
          id="scroll-to-bottom-btn"
          className="scroll-btn"
          onClick={scrollToBottom}
          title="Scroll to bottom"
        >
          <ArrowDownIcon size={18} />
        </button>
      )}

      {/* Input bar */}
      <MessageInput
        onSend={handleSend}
        onDocumentUploaded={onDocumentUploaded}
        disabled={isTyping}
      />
    </div>
  );
}
