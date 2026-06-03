# 🛡️ SecureDocs AI — RAG-Based Document Intelligence System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19+-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8+-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev)
[![Gemini](https://img.shields.io/badge/Gemini_API-2.5_Flash-4285F4?style=for-the-badge&logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq_API-Llama_3.1-F55A42?style=for-the-badge)](https://groq.com)

**SecureDocs AI** is an enterprise-grade Retrieval-Augmented Generation (RAG) system built with **Django REST Framework** (Backend) and **React + Vite** (Frontend). It enables secure, local-first document indexing and context-grounded AI conversations. By combining sentence-level vector searches with a dual-layer memory architecture and multi-provider LLM fallbacks, SecureDocs AI delivers fast, highly reliable, and grounded answers with exact source citations.

---

## 🎨 User Interface & Experience

The application is engineered with a modern, high-fidelity liquid glassmorphism interface, featuring micro-interactions and smooth state transitions.

| Component | UI Design Styling | Functional Highlight |
| :--- | :--- | :--- |
| **🌌 Liquid Backdrop** | Custom HSL CSS Radial Gradients | Active background animation providing a premium depth-of-field experience. |
| **⚡ Glassmorphic Sidebar** | CSS Backdrop-Filter (`blur`) & Flexbox | Interactive, collapsible repository layout managing all active chat threads and uploaded files. |
| **💬 Streamlined Chat Window** | Dynamic Bubbles & Scroll Anchoring | Clean, alternating speech blocks with instant auto-scroll and auto-resizing text area. |
| **🔖 Smart Citations** | Floating Source Cards & Badges | Highlights the exact document chunk retrieved by the vector engine, complete with metadata. |

---

## ⚡ Core Technical Pillars

| Technical Pillar | Technology | Functional Specification |
| :--- | :--- | :--- |
| **🧠 Dual-Layer Memory** | `SQLite` + `Django ORM` | **Short-Term Context:** Retains the last 15 messages in the active thread for smooth conversation flow.<br>**Long-Term Context:** Auto-generates summaries of the 5 most recent chat sessions, injection-feeding historical context into new prompts. |
| **🔄 High-Availability LLM** | `Gemini 2.5` ➔ `Groq API` | **Cascade Auto-Retry:** Cascades queries through `gemini-2.5-flash`, `gemini-3.5-flash`, and `gemini-flash-latest` with intelligent rate-limit retries.<br>**Failover Provider:** Automatically switches providers to Groq (`llama-3.1-8b-instant`) if Gemini limits are exhausted. |
| **⚡ Offline Local Embeddings** | `SentenceTransformers` | **Zero API Costs:** Local processing of 384-dimensional text embeddings using the `all-MiniLM-L6-v2` model.<br>**Ultra-Fast Indexing:** High-speed vector generation running entirely on-device. |
| **🔍 Vector Similarity Search** | `FAISS` (CPU) | **Chunk Retrieval:** Indexes doc chunks locally. When a question is asked, it queries the index and returns the top 4 matching document contexts. |
| **📂 Document Ingest Pipeline** | `pdfplumber` + `python-docx` | **Multi-Format Extraction:** Automatically handles plain `.txt`, complex tables in `.pdf`, and headers/lists in `.docx` documents. |
| **📝 Auto-Title Generator** | `google-genai` SDK | Uses the first user message in a chat to generate a concise, human-like title for the thread. |

---

## 🏗️ System Architecture & Workflow

The diagram below outlines the full data flow—from document indexing to context retrieval and LLM response generation:

```mermaid
graph TD
    %% Define CSS classes for custom nodes
    classDef default fill:#111827,stroke:#374151,stroke-width:1px,color:#e5e7eb;
    classDef highlight fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#f3f4f6;
    classDef success fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f3f4f6;
    classDef warning fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#f3f4f6;

    User([👤 User])
    UI[🖥️ React Frontend]
    Django[⚙️ Django REST Framework]
    
    subgraph DjangoBackend ["📦 Django Backend Services"]
        DB[(🗄️ SQLite Database)]
        DocService[📄 Document Service]
        RAGService[🧠 RAG Service]
        
        DocService -->|Compute 384-d Vectors| Embed[sentence-transformers]
        Embed -->|Store Embeddings| FAISS[(⚡ FAISS Vector Store)]
        
        RAGService -->|Query Match| FAISS
        RAGService -->|Fetch Last 15 Msgs| DB
        RAGService -->|Fetch Last 5 Summaries| DB
    end

    subgraph ExternalAPIs ["🌐 External AI Services (Fallback)"]
        Gemini{♊ Gemini 2.5 Flash}
        Groq{🔥 Groq Fallback}
    end

    User <-->|Interacts| UI
    UI <-->|JSON / Multipart HTTP| Django
    Django <-->|Read/Write| DB
    Django -->|Extracts & Chunks| DocService
    Django <-->|Assemble Prompt| RAGService
    
    RAGService -->|Generate Content| Gemini
    Gemini -.->|On Rate Limit / 429| Groq
    Gemini -->|Return Response| RAGService
    Groq -->|Return Response| RAGService
    
    DB -->|History & Memory| Django
    RAGService -->|Response + Citations| UI

    %% Assign styles to nodes
    class User,UI highlight;
    class Django,RAGService,DocService default;
    class FAISS,Embed success;
    class Gemini,Groq warning;
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
│   ├── media/              # Dynamic uploaded documents & local FAISS indexes (Git-ignored)
│   ├── db.sqlite3          # SQLite Database (Git-ignored)
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
*   **Python 3.9+** installed
*   **Node.js (v18+)** and **npm** installed

---

### 🔧 1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd securedocs_ai/backend
    ```

2.  **Create and activate a virtual environment:**
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

4.  **Configure environment variables:**
    *   Copy the `.env.example` template:
        ```bash
        cp .env.example .env
        ```
    *   Open `.env` and fill in your Gemini and Groq API keys:
        ```ini
        GEMINI_API_KEY=your_actual_gemini_key_here
        GROQ_API_KEY=your_actual_groq_key_here
        ```

5.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start Django server:**
    ```bash
    python manage.py runserver
    ```
    Backend will run on **`http://127.0.0.1:8000`**.

---

### 💻 2. Frontend Setup

1.  **Open a new terminal and navigate to the frontend directory:**
    ```bash
    cd securedocs_ai/frontend
    ```

2.  **Install Node packages:**
    ```bash
    npm install
    ```

3.  **Start Vite dev server:**
    ```bash
    npm run dev
    ```
    Frontend will run on **`http://localhost:5173`**.

---

## 🧪 Verification & Testing

To run the complete system verification suite (testing Django, database migrations, document extractors, FAISS vector indexing, memory systems, and LLM responses):

1.  Ensure the Django backend is running (`python manage.py runserver`).
2.  Open another terminal, enter the `backend` directory, activate the virtual environment, and run:
    ```bash
    python test_pipeline.py
    ```

Successful run output:
`[PASS] Gemini API responds` ... `ALL FEATURES VERIFIED AND WORKING!`

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
