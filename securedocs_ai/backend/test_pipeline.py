"""
Full End-to-End Verification Script
Tests every feature of Levi AI with the real Gemini API key
"""

import django, os, json, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import urllib.request, urllib.error

BASE = 'http://localhost:8000/api'

def http(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={'Content-Type': 'application/json'},
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

PASS = '[PASS]'
FAIL = '[FAIL]'
results = []

def check(label, condition, info=''):
    status = PASS if condition else FAIL
    msg = f'{status} {label}'
    if info:
        msg += f'  →  {info}'
    print(msg)
    results.append((label, condition))
    return condition

# ─────────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print(' LEVI AI — FULL END-TO-END VERIFICATION')
print('='*60)

# ─────────────────────────────────────────────────────────────────────
print('\n[1/7] GEMINI API KEY TEST')
print('-'*40)
from rag.llm import generate_response
answer = generate_response("Say 'Hello from Levi AI' in exactly 5 words.")
is_working = 'Error' not in answer and len(answer) > 3
check('Gemini API responds', is_working, answer[:100])

# ─────────────────────────────────────────────────────────────────────
print('\n[2/7] CHAT CREATE / LIST / RENAME / DELETE')
print('-'*40)

# Create chat
status, data = http('POST', '/chats/', {'title': 'Verify Chat'})
check('POST /api/chats/ → 201', status == 201, f"id={data.get('id')}, title={data.get('title')}")
chat_id = data.get('id')

# List chats
status, data = http('GET', '/chats/')
check('GET /api/chats/ → 200', status == 200, f'{len(data)} chat(s) found')

# Get single chat
status, data = http('GET', f'/chats/{chat_id}/')
check('GET /api/chats/{id}/ → 200', status == 200, f"title={data.get('title')}")

# Rename chat
status, data = http('PATCH', f'/chats/{chat_id}/', {'title': 'Renamed Chat'})
check('PATCH /api/chats/{id}/ → 200 (rename)', status == 200, f"new title={data.get('title')}")

# Verify rename
status, data = http('GET', f'/chats/{chat_id}/')
check('Rename persisted in DB', data.get('title') == 'Renamed Chat', data.get('title'))

# ─────────────────────────────────────────────────────────────────────
print('\n[3/7] DOCUMENT UPLOAD + PROCESSING PIPELINE')
print('-'*40)

# Create a real test document
test_doc_path = os.path.join(os.path.dirname(__file__), 'test_verify_doc.txt')
with open(test_doc_path, 'w') as f:
    f.write("""ARTIFICIAL INTELLIGENCE OVERVIEW

Artificial Intelligence (AI) is the simulation of human intelligence by machines.
Machine learning is a subset of AI that enables computers to learn from data.
Deep learning uses neural networks with many layers to process complex patterns.

NEURAL NETWORKS
Neural networks are inspired by the human brain. They consist of neurons and synapses.
Backpropagation is used to train neural networks by adjusting weights.

LARGE LANGUAGE MODELS
Large language models like Gemini and GPT are trained on vast amounts of text.
They use transformer architecture with attention mechanisms.
These models can generate, summarize, and answer questions about text.

RETRIEVAL AUGMENTED GENERATION
RAG combines document retrieval with language model generation.
FAISS is a vector similarity search library used for fast retrieval.
Embeddings convert text to numerical vectors for semantic search.
""")

# Upload document via multipart POST
import urllib.parse
boundary = 'LeviAITestBoundary123'
with open(test_doc_path, 'rb') as f:
    file_content = f.read()

body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="ai_overview.txt"\r\n'
    f'Content-Type: text/plain\r\n\r\n'
).encode() + file_content + f'\r\n--{boundary}--\r\n'.encode()

upload_req = urllib.request.Request(
    BASE + '/documents/upload/',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
    method='POST'
)
try:
    with urllib.request.urlopen(upload_req, timeout=30) as r:
        upload_status = r.status
        upload_data = json.loads(r.read())
except urllib.error.HTTPError as e:
    upload_status = e.code
    upload_data = json.loads(e.read())

check('POST /api/documents/upload/ → 201', upload_status == 201,
      f"chunks={upload_data.get('chunks_created', '?')}, file={upload_data.get('filename','?')}")
doc_id = upload_data.get('id')

# List documents
status, data = http('GET', '/documents/')
check('GET /api/documents/ → 200', status == 200, f'{len(data)} document(s)')
check('Document appears in list', any(d.get('id') == doc_id for d in data), f'doc_id={doc_id}')

# Check FAISS was populated
from rag.vector_store import get_index_size
faiss_size = get_index_size()
check('FAISS index populated', faiss_size > 0, f'{faiss_size} vectors stored')

# ─────────────────────────────────────────────────────────────────────
print('\n[4/7] RAG CHAT — GEMINI RESPONSE + SOURCE CITATIONS')
print('-'*40)

# Send a question that should be answered from the document
status, data = http('POST', '/chat/', {
    'chat_id': chat_id,
    'question': 'What is RAG and what is FAISS used for?'
})
check('POST /api/chat/ → 200', status == 200, f'HTTP {status}')

answer = data.get('answer', '')
sources = data.get('sources', [])
check('Answer is not empty', len(answer) > 20, answer[:120])
check('Answer not an error', 'Error' not in answer and '⚠️' not in answer, '')
check('Sources returned', len(sources) > 0, f'{len(sources)} source(s): {[s.get("filename","?") for s in sources]}')
check('Source filename correct', any('ai_overview' in s.get('filename','') for s in sources), str(sources))

# Verify messages saved to DB
status, msgs = http('GET', f'/chats/{chat_id}/messages/')
check('GET /api/chats/{id}/messages/ → 200', status == 200, f'{len(msgs)} message(s)')
check('User message saved', any(m.get('role') == 'user' for m in msgs), '')
check('Assistant message saved', any(m.get('role') == 'assistant' for m in msgs), '')

# ─────────────────────────────────────────────────────────────────────
print('\n[5/7] AUTO-TITLE GENERATION (First message)')
print('-'*40)

# Create fresh chat and send first message
_, new_chat = http('POST', '/chats/', {'title': 'New Chat'})
new_chat_id = new_chat.get('id')

http('POST', '/chat/', {
    'chat_id': new_chat_id,
    'question': 'Explain how neural networks work'
})

# Fetch updated chat — title should have been auto-generated
time.sleep(1)
_, updated = http('GET', f'/chats/{new_chat_id}/')
new_title = updated.get('title', '')
check('Auto-title generated from first message', new_title != 'New Chat' and len(new_title) > 3, f'"{new_title}"')

# ─────────────────────────────────────────────────────────────────────
print('\n[6/7] MEMORY SYSTEM (Summarize + New Chat Flow)')
print('-'*40)

# Summarize the main chat (simulates clicking "New Chat")
status, data = http('POST', f'/chats/{chat_id}/summarize/')
check('POST /api/chats/{id}/summarize/ → 200', status == 200, f'HTTP {status}')
summary_text = data.get('summary', '')
check('Summary generated (not empty)', len(summary_text) > 20, summary_text[:120])

# Verify stored in DB
from chats.models import ChatSummary
stored = ChatSummary.objects.filter(chat_id=chat_id).first()
check('Summary stored in ChatSummary table', stored is not None, 
      stored.summary[:80] if stored else 'NOT FOUND')

# Test that summaries load for next chat prompt
from rag.memory import get_recent_summaries, format_summaries
summaries = get_recent_summaries(n=5)
check('Summaries load for long-term memory', len(summaries) > 0, f'{len(summaries)} summary/summaries')
memory_text = format_summaries(summaries)
check('Summaries formatted for prompt', len(memory_text) > 0, f'{len(memory_text)} chars')

# ─────────────────────────────────────────────────────────────────────
print('\n[7/7] DOCUMENT DELETE (SQLite + FAISS + Disk)')
print('-'*40)

faiss_before = get_index_size()
status, data = http('DELETE', f'/documents/{doc_id}/')
check('DELETE /api/documents/{id}/ → 200', status == 200, data.get('message', ''))

faiss_after = get_index_size()
check('FAISS vectors removed', faiss_after < faiss_before, f'{faiss_before} → {faiss_after} vectors')

from documents.models import Document
doc_exists = Document.objects.filter(id=doc_id).exists()
check('Document removed from SQLite', not doc_exists, f'doc_id={doc_id}')

disk_path = upload_data.get('filepath', '')
if disk_path:
    check('File removed from disk', not os.path.exists(disk_path), disk_path)

# ─────────────────────────────────────────────────────────────────────
print('\n[CLEANUP] Removing test data...')
http('DELETE', f'/chats/{chat_id}/')
http('DELETE', f'/chats/{new_chat_id}/')
if os.path.exists(test_doc_path):
    os.remove(test_doc_path)
print('Done.')

# ─────────────────────────────────────────────────────────────────────
print('\n' + '='*60)
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
total = len(results)
print(f' RESULTS: {passed}/{total} passed  |  {failed} failed')
print('='*60)

if failed > 0:
    print('\nFailed checks:')
    for label, ok in results:
        if not ok:
            print(f'  ✗ {label}')
else:
    print('\n ALL FEATURES VERIFIED AND WORKING!')
    print(' Levi AI is ready to use.')
    print(f'\n Frontend: http://localhost:5173')
    print(f' Backend:  http://localhost:8000')
