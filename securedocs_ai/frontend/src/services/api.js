/**
 * SecureDocs AI — Axios API Service
 * All backend API calls centralized here
 * Backend base URL: http://127.0.0.1:8000
 */

import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
});

// ─── CHAT ENDPOINTS ───────────────────────────────────────────────

/** POST /api/chats/ → Create new chat */
export const createChat = (title = 'New Chat') =>
  API.post('/chats/', { title });

/** GET /api/chats/ → List all chats (sidebar) */
export const listChats = () => API.get('/chats/');

/** GET /api/chats/{id}/ → Get single chat */
export const getChat = (chatId) => API.get(`/chats/${chatId}/`);

/** PATCH /api/chats/{id}/ → Rename chat */
export const renameChat = (chatId, title) =>
  API.patch(`/chats/${chatId}/`, { title });

/** DELETE /api/chats/{id}/ → Delete chat */
export const deleteChat = (chatId) => API.delete(`/chats/${chatId}/`);

/** GET /api/chats/{id}/messages/ → Load all messages */
export const getMessages = (chatId) => API.get(`/chats/${chatId}/messages/`);

/**
 * POST /api/chats/{id}/summarize/ → Generate + store summary
 * Called during "New Chat" flow BEFORE creating new chat
 */
export const summarizeChat = (chatId) =>
  API.post(`/chats/${chatId}/summarize/`);

// ─── AI CHAT ENDPOINT ─────────────────────────────────────────────

/**
 * POST /api/chat/ → Main RAG Q&A endpoint
 * Full pipeline: memory → FAISS → Gemini → response + sources
 */
export const sendMessage = (chatId, question) =>
  API.post('/chat/', { chat_id: chatId, question });

// ─── DOCUMENT ENDPOINTS ───────────────────────────────────────────

/**
 * POST /api/documents/upload/ → Upload + process document
 * Uses multipart form data
 */
export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return API.post('/documents/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/** GET /api/documents/ → List all uploaded documents */
export const listDocuments = () => API.get('/documents/');

/** DELETE /api/documents/{id}/ → Delete document + remove from FAISS */
export const deleteDocument = (docId) => API.delete(`/documents/${docId}/`);

export default API;
