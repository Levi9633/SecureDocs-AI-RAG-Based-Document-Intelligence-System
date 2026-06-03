/**
 * Home Page — Main Application Layout
 * Assembles: Navbar + Sidebar + ChatWindow
 * Manages global state: activeChatId, refresh triggers
 */

import { useState, useCallback } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';

export default function Home() {
  const [activeChatId, setActiveChatId] = useState(null);
  const [sidebarRefresh, setSidebarRefresh] = useState(0);

  // Trigger sidebar to reload data
  const refreshSidebar = useCallback(() => {
    setSidebarRefresh(prev => prev + 1);
  }, []);

  // Handle selecting a chat from sidebar
  const handleChatSelect = (chatId) => {
    setActiveChatId(chatId);
  };

  // Handle new chat created — navigate to it
  const handleChatCreated = (newChatId) => {
    setActiveChatId(newChatId);
    refreshSidebar();
  };

  // Handle chat updated (e.g., title auto-generated)
  const handleChatUpdated = () => {
    refreshSidebar();
  };

  // Handle documents cleared from navbar
  const handleClearDocuments = () => {
    refreshSidebar();
  };

  return (
    <>
      {/* Top Navigation Bar */}
      <Navbar onClearDocuments={handleClearDocuments} />

      {/* Main App Layout */}
      <div className="app-layout">
        {/* Left Sidebar */}
        <Sidebar
          activeChatId={activeChatId}
          onChatSelect={handleChatSelect}
          onChatCreated={handleChatCreated}
          refreshTrigger={sidebarRefresh}
        />

        {/* Main Chat Window */}
        <ChatWindow
          chatId={activeChatId}
          onDocumentUploaded={refreshSidebar}
          onChatUpdated={handleChatUpdated}
        />
      </div>
    </>
  );
}
