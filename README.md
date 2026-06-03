# 🛡️ SecureDocs AI — RAG-Based Document Intelligence System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19+-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev)
[![Gemini](https://img.shields.io/badge/Gemini_API-2.5_Flash-4285F4?style=for-the-badge&logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq_API-Llama_3.1-F55A42?style=for-the-badge)](https://groq.com)

**SecureDocs AI** is a state-of-the-art Retrieval-Augmented Generation (RAG) system built with **Django REST Framework** (Backend) and **React + Vite** (Frontend). It allows users to upload documents (PDFs, Word documents, text files), automatically extracts and indexes their contents locally into a **FAISS** vector store using Sentence Transformers, and supports natural language conversations with detailed source citations. It features a advanced memory system that retains context from past conversation summaries (long-term memory) and the last 15 messages (short-term memory).

---

## 📸 Interface Preview

The application features a modern, liquid radial-gradient glassmorphism UI designed for a premium user experience:

*   **Left Sidebar:** Manage active chat threads, create new chats, and list globally uploaded files.
*   **Top Navigation Bar:** Manage overall system functions, review active configs, or clear documents globally.
*   **Main Chat Window:** Enjoy clean, responsive chat bubbles, real-time message sending, and inline source citation cards showing the exact file chunks retrieved by the vector search.

---

## ⚡ Key Features

*   **🧠 Advanced Context Memory (Dual-Layer):**
    *   *Short-Term Memory:* Recalls the last 15 messages in the active chat thread for conversational flow.
    *   *Long-Term Memory:* Generates and stores summaries of the last 5 chat threads to maintain overall context without bloating the prompt token count.
*   **🔄 High-Availability LLM Fallback Pipeline:**
    *   Primary LLM: **Gemini-2.5-Flash** (using the new `google-genai` SDK v1.x) with automatic retries for rate limits.
    *   Secondary Fallback: Automatically downgrades to `gemini-3.5-flash` or `gemini-flash-latest`.
    *   Failover Provider: If all Gemini models are exhausted, it automatically redirects requests to **Groq API** running `llama-3.1-8b-instant` to guarantee 100% uptime.
*   **📂 Multiformat Document Processing:** Support for uploading `.txt`, `.pdf` (using `pdfplumber`), and `.docx` (using `python-docx`).
*   **⚡ Offline Local Embeddings:** Utilizes `SentenceTransformer` (`all-MiniLM-L6-v2`) locally to compute 384-dimensional vector embeddings, saving API costs and processing chunks in milliseconds.
*   **🔍 Vector Search with FAISS:** Indexes and performs similarity searches on text chunks, retrieving the top 4 matching sources with exact citation highlights.
*   **📝 Auto-Title Generation:** Automatically generates descriptive, contextual chat titles from your first question.

---

## 🏗️ System Architecture & Workflow

The diagram below represents the complete flow of data from when you upload a document to when a user asks a question and receives a grounded response:

```mermaid
graph TD
    User([User]) <-->|Interacts| UI[React Frontend]
    UI <-->|JSON / Multipart HTTP| Django[Django REST Framework]
    
    subgraph Django Backend Services
        Django <-->|Read/Write| DB[(SQLite Database)]
        Django -->|Extracts & Chunks| DocService[Document Service]
        Django <-->|Assemble Prompt| RAGService[RAG Service]
        
        DocService -->|Compute 384-d Vectors| Embed[Sentence Transformers]
        Embed -->|Store Embeddings| FAISS[(FAISS Index)]
        
        RAGService -->|Query Match| FAISS
        RAGService -->|Fetch Last 15 Msgs| DB
        RAGService -->|Fetch Last 5 Summaries| DB
    end

    subgraph LLM APIs (External Providers)
        RAGService -->|Request Response| Gemini{Gemini API}
        Gemini -.->|If Rate Limited / Down| Groq{Groq API Fallback}
        Gemini -->|Returns grounded response| RAGService
        Groq -->|Returns grounded response| RAGService
    end

    DB -->|chats, messages, summaries| Django
    RAGService -->|Response + Citations| UI
```

---

## 🗂️ Project Directory Structure

```text
securedocs_ai/
├── backend/
│   ├── core/               # Main configuration (settings.py, urls.py)
│   ├── chats/              # Chat management, message histories & summaries
│   ├── documents/          # Document uploads, text extraction pipelines
│   ├── rag/                # Embeddings, chunking, FAISS indexer, LLM integrations
│   ├── media/              # Dynamic uploaded documents & local FAISS indexes
│   ├── db.sqlite3          # SQLite Database
│   ├── manage.py           # Django management CLI
│   └── test_pipeline.py    # End-to-end backend verification pipeline
└── frontend/
    ├── src/
    │   ├── components/     # Reusable UI components (Sidebar, ChatWindow, etc.)
    │   ├── pages/          # Layout page elements (Home.jsx)
    │   ├── services/       # Axios API central configuration (api.js)
    │   └── App.jsx         # Root router component
    ├── package.json        # Frontend dependencies
    └── vite.config.js      # Vite build configurations
```

---

## 🚀 Getting Started

### 📋 Prerequisites
Ensure you have the following installed on your system:
*   Python 3.9 or higher
*   Node.js (v18 or higher) and npm

---

### 🔧 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd securedocs_ai/backend
    ```

2.  **Create and activate a Python virtual environment:**
    *   **Windows (PowerShell):**
        ```powershell
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        ```
    *   **Linux/macOS:**
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Copy the `.env.example` template:
        ```bash
        cp .env.example .env
        ```
    *   Open `.env` and fill in your Gemini and Groq API keys:
        ```ini
        GEMINI_API_KEY=your_actual_gemini_key_here
        GROQ_API_KEY=your_actual_groq_key_here
        ```

5.  **Run Database Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start the Django Development Server:**
    ```bash
    python manage.py runserver
    ```
    The backend will start running on **`http://127.0.0.1:8000`**.

---

### 💻 2. Frontend Setup

1.  **Navigate to the frontend directory:**
    *   Open a new terminal window/tab:
    ```bash
    cd securedocs_ai/frontend
    ```

2.  **Install Node packages:**
    ```bash
    npm install
    ```

3.  **Start the Vite Local Server:**
    ```bash
    npm run dev
    ```
    The frontend will start running on **`http://localhost:5173`**.

---

## 🧪 Verification & Testing

To run the full end-to-end pipeline verification test (which verifies Django routing, DB insertions, document extraction, vector indexing, chat history, auto-titling, memory, and LLM responses):

1.  With the Django backend server running (`python manage.py runserver` in one window):
2.  Open another terminal, enter the backend directory, and activate the virtual environment.
3.  Run the verification pipeline:
    ```bash
    python test_pipeline.py
    ```

If everything is configured correctly, you will see a success output:
`[PASS] Gemini API responds` ... `ALL FEATURES VERIFIED AND WORKING!`

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
