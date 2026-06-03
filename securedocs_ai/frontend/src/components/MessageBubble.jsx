/**
 * MessageBubble Component
 * Per spec:
 *   - User messages: right-aligned
 *   - Assistant messages: left-aligned with copy button + source citations
 *   - Both have copy button inside the bubble at top right
 *   - Removed You/Levi AI text
 */

import { useState, useEffect } from "react";
import SourceCitation from "./SourceCitation";
import { CopyIcon, CheckIcon } from "./Icons";

export default function MessageBubble({ message, sources }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  // Typing effect state for new assistant messages
  const [displayedText, setDisplayedText] = useState(() => {
    return (isUser || !message.isNew) ? message.content : "";
  });
  const [isTyping, setIsTyping] = useState(() => {
    return !isUser && message.isNew;
  });

  useEffect(() => {
    if (isUser || !message.isNew) {
      setDisplayedText(message.content);
      setIsTyping(false);
      return;
    }

    setDisplayedText("");
    setIsTyping(true);
    let index = 0;
    const fullText = message.content;
    
    // Dynamic typing speed adjusting to the content size (decelerated for readability)
    const textLength = fullText.length;
    const charsPerTick = textLength > 1000 ? 3 : textLength > 400 ? 2 : 1;
    const intervalMs = 24;

    const timer = setInterval(() => {
      index += charsPerTick;
      if (index >= fullText.length) {
        setDisplayedText(fullText);
        setIsTyping(false);
        clearInterval(timer);
        message.isNew = false; // Turn off flag
      } else {
        setDisplayedText(fullText.substring(0, index));
        // Auto-scroll screen while typing if currently close to bottom
        const area = document.querySelector('.messages-area');
        if (area) {
          const isNearBottom = area.scrollHeight - area.scrollTop - area.clientHeight < 150;
          if (isNearBottom) {
            area.scrollTop = area.scrollHeight;
          }
        }
      }
    }, intervalMs);

    return () => {
      clearInterval(timer);
    };
  }, [message.content, message.isNew, isUser]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const el = document.createElement("textarea");
      el.value = message.content;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Simple text formatter — handle line breaks, basic markdown, and the blinking cursor
  const renderContent = (text) => {
    const formatted = text.split("\n").map((line, i) => (
      <span key={i}>
        {line}
        {i < text.split("\n").length - 1 && <br />}
      </span>
    ));
    return (
      <>
        {formatted}
        {isTyping && <span className="typing-cursor">▊</span>}
      </>
    );
  };

  return (
    <div className={`message-wrapper ${isUser ? "user" : "assistant"}`}>
      {/* Message bubble */}
      <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
        <div className="message-content">
          {renderContent(displayedText)}
        </div>
        <button
          id={`copy-btn-${message.id || Math.random()}`}
          className={`copy-btn-inside ${copied ? "copied" : ""}`}
          onClick={handleCopy}
          title="Copy message"
        >
          {copied ? <CheckIcon size={14} /> : <CopyIcon size={14} />}
        </button>
      </div>

      {/* Source citations — only for assistant messages */}
      {!isUser && sources && sources.length > 0 && (
        <SourceCitation sources={sources} />
      )}
    </div>
  );
}
