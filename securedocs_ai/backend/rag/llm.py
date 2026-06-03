"""
RAG — Gemini LLM Integration (using new google-genai SDK v1.x)
Uses: google-genai (NOT the deprecated google-generativeai)
Model: gemini-2.5-flash (latest, fast, cost-efficient)

Provides:
  - generate_response(prompt) → answer string
  - generate_summary(messages_text) → summary string
  - generate_title(first_message) → short title string
"""

import os
from google import genai
from google.genai import types
from django.conf import settings

from .prompts import build_summary_prompt, build_title_prompt


def _get_client():
    """Create and return a Gemini client using the new google-genai SDK."""
    api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY', '')

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add it to your .env file: GEMINI_API_KEY=your-key-here"
        )

    return genai.Client(api_key=api_key)


import time

def _call_groq(prompt: str) -> str:
    """
    Fallback call using the OpenAI SDK routed to Groq's high-speed completion API.
    Model: llama-3.1-8b-instant (Fast, free, and highly accurate)
    """
    import openai
    api_key = getattr(settings, 'GROQ_API_KEY', '') or os.getenv('GROQ_API_KEY', '')
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in settings or environment.")

    client = openai.OpenAI(
        base_url='https://api.groq.com/openai/v1',
        api_key=api_key
    )
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.0,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    """
    Core Gemini call using the new google-genai SDK.
    Tries gemini-2.5-flash first (up to 2 attempts, 1s delay on rate limit).
    If exhausted, falls back to gemini-3.5-flash and gemini-flash-latest
    (up to 2 attempts each, 1s delay).
    
    If all Gemini models fail, automatically falls back to Groq (llama-3.1-8b-instant).
    """
    client = _get_client()
    models_to_try = ['gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-flash-latest']

    last_exception = None

    for model_name in models_to_try:
        # Try up to 2 times per model with a 1s delay on 429/rate limits
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=2048,
                    ),
                )
                return response.text.strip() if response.text else ""
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Check if it is a rate limit or quota error
                is_rate_limit = (
                    'quota' in error_msg.lower() or 
                    'rate' in error_msg.lower() or 
                    '429' in error_msg or 
                    'limit' in error_msg.lower()
                )
                
                # If it's a rate limit and we have retries left, wait 1s and retry
                if is_rate_limit and attempt < 1:
                    time.sleep(1.0)
                    continue
                else:
                    # Break to try next model in fallback list
                    break

    # If we reached here, all Gemini models failed. Try Groq fallback!
    try:
        return _call_groq(prompt)
    except Exception as groq_err:
        raise Exception(
            f"Gemini failed (Last error: {last_exception}). "
            f"Groq fallback also failed (Error: {groq_err})."
        )


def generate_response(prompt: str) -> str:
    """
    Send the full RAG prompt to LLM (Gemini with Groq fallback) and return the generated answer.
    Used for: answering user questions grounded in document context.
    """
    try:
        return _call_gemini(prompt)
    except Exception as e:
        error_msg = str(e)
        if 'api_key' in error_msg.lower() or 'invalid' in error_msg.lower() or 'key' in error_msg.lower():
            return "⚠️ Error: Both Gemini and Groq APIs failed due to invalid API keys. Please verify your .env configuration."
        elif 'quota' in error_msg.lower() or 'rate' in error_msg.lower() or '429' in error_msg or 'exhausted' in error_msg.lower():
            return "⚠️ Error: Gemini and Groq API rate limits reached. Please wait a moment and try again."
        else:
            return f"⚠️ Error generating response: {error_msg}"


def generate_summary(messages_text: str) -> str:
    """
    Generate a concise summary of a completed chat for long-term memory storage.
    Called when user starts a New Chat.
    """
    try:
        prompt = build_summary_prompt(messages_text)
        return _call_gemini(prompt)
    except Exception as e:
        return f"Summary could not be generated: {str(e)}"


def generate_title(first_message: str) -> str:
    """
    Auto-generate a short chat title from the first user message.
    Example: "Explain neural networks" → "Neural Networks Basics"
    """
    try:
        prompt = build_title_prompt(first_message)
        title = _call_gemini(prompt)
        # Clean up and truncate
        title = title.strip().strip('"').strip("'")
        return title[:60] if title else first_message[:50]
    except Exception:
        # Fallback: use first 50 chars of the message
        return first_message[:50] if first_message else "New Chat"
