// frontend/src/pages/ChatPage.tsx
import React, { useEffect, useRef, useState } from 'react';
import { useChat, ChatMessage, Conversation } from '../hooks/useChat';

const ChatPage: React.FC = () => {
  const {
    conversations, activeConversation, messages, streaming,
    fetchConversations, createConversation, loadMessages, sendMessage, stopStreaming,
  } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || streaming) return;
    setInput('');
    sendMessage(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* Conversation List */}
      <div
        style={{
          width: '280px',
          borderRight: '1px solid var(--color-border)',
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--color-border)' }}>
          <button
            className="btn-primary"
            onClick={() => createConversation()}
            style={{ width: '100%' }}
          >
            + New Conversation
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: '0.5rem' }}>
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => loadMessages(conv.id)}
              style={{
                width: '100%',
                display: 'block',
                padding: '0.75rem',
                marginBottom: '0.25rem',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                background: activeConversation === conv.id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                color: activeConversation === conv.id ? 'var(--color-accent-hover)' : 'var(--color-text-secondary)',
                cursor: 'pointer',
                textAlign: 'left',
                fontFamily: 'var(--font-family)',
                fontSize: 'var(--font-size-sm)',
                transition: 'all var(--transition-fast)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                if (activeConversation !== conv.id) e.currentTarget.style.background = 'var(--color-bg-hover)';
              }}
              onMouseLeave={(e) => {
                if (activeConversation !== conv.id) e.currentTarget.style.background = 'transparent';
              }}
            >
              💬 {conv.title}
            </button>
          ))}
          {conversations.length === 0 && (
            <p style={{ padding: '1rem', color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)', textAlign: 'center' }}>
              No conversations yet
            </p>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderBottom: '1px solid var(--color-border)',
            background: 'var(--color-bg-glass)',
          }}
        >
          <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600 }}>
            🧬 Clinical AI Chat
          </h2>
          <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
            Ask questions about your clinical documents — answers include source citations
          </p>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            overflow: 'auto',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          {messages.length === 0 && (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ textAlign: 'center', maxWidth: '400px' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔬</div>
                <h3 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 600, marginBottom: '0.5rem' }}>
                  Start a Clinical Query
                </h3>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)', lineHeight: 1.6 }}>
                  Ask questions like "Summarize the patient's medication history" or
                  "What were the lab results from the last visit?"
                </p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className="animate-fade-in"
              style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                animationDelay: `${i * 50}ms`,
              }}
            >
              <div
                style={{
                  maxWidth: '75%',
                  padding: '0.875rem 1.125rem',
                  borderRadius: msg.role === 'user'
                    ? 'var(--radius-xl) var(--radius-xl) var(--radius-sm) var(--radius-xl)'
                    : 'var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-sm)',
                  background: msg.role === 'user' ? 'var(--gradient-primary)' : 'var(--color-bg-card)',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--color-border)',
                  color: 'var(--color-text-primary)',
                  fontSize: 'var(--font-size-sm)',
                  lineHeight: 1.7,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {msg.role === 'assistant' && (
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-accent-hover)', fontWeight: 600, marginBottom: '0.375rem' }}>
                    🧬 MedIntel
                  </div>
                )}
                {msg.content}
                {msg.role === 'assistant' && streaming && i === messages.length - 1 && (
                  <span
                    style={{
                      display: 'inline-block',
                      width: '6px',
                      height: '16px',
                      background: 'var(--color-accent)',
                      marginLeft: '2px',
                      animation: 'blink 1s infinite',
                      verticalAlign: 'text-bottom',
                    }}
                  />
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
          <style>{`@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }`}</style>
        </div>

        {/* Input */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid var(--color-border)',
            background: 'var(--color-bg-glass)',
          }}
        >
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
            <textarea
              className="input-field"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your clinical documents..."
              rows={1}
              style={{
                flex: 1,
                resize: 'none',
                minHeight: '42px',
                maxHeight: '120px',
              }}
            />
            {streaming ? (
              <button className="btn-secondary" onClick={stopStreaming} style={{ flexShrink: 0 }}>
                ⏹ Stop
              </button>
            ) : (
              <button
                className="btn-primary"
                onClick={handleSend}
                disabled={!input.trim()}
                style={{ flexShrink: 0 }}
              >
                Send →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
