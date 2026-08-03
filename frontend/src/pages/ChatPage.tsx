// frontend/src/pages/ChatPage.tsx
import React, { useEffect, useRef, useState } from 'react';
import { useChat, ChatMessage, Conversation } from '../hooks/useChat';

// ---------- Robust Markdown-to-HTML Renderer ----------
function renderMarkdown(raw: string): string {
  // Work line-by-line so block-level patterns work reliably
  const lines = raw.split('\n');
  const out: string[] = [];
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    // ── Horizontal rule ──
    if (/^-{3,}$/.test(line.trim())) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<hr style="border:none;border-top:1px solid var(--color-border);margin:0.75rem 0" />');
      continue;
    }

    // ── Headers ── (strip leading #s)
    const h4 = line.match(/^#{4}\s+(.+)/);
    if (h4) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push(`<h4 style="font-size:0.9rem;font-weight:700;margin:0.75rem 0 0.25rem;color:var(--color-text-primary)">${inlineFormat(h4[1])}</h4>`);
      continue;
    }
    const h3 = line.match(/^#{3}\s+(.+)/);
    if (h3) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push(`<h3 style="font-size:1.05rem;font-weight:700;margin:0.75rem 0 0.25rem;color:var(--color-text-primary)">${inlineFormat(h3[1])}</h3>`);
      continue;
    }
    const h2 = line.match(/^#{2}\s+(.+)/);
    if (h2) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push(`<h2 style="font-size:1.15rem;font-weight:700;margin:0.75rem 0 0.25rem;color:var(--color-text-primary)">${inlineFormat(h2[1])}</h2>`);
      continue;
    }

    // ── Blockquote ── (lines starting with >)
    if (/^>\s?/.test(line)) {
      if (inList) { out.push('</ul>'); inList = false; }
      const content = line.replace(/^>\s?/, '');
      out.push(`<blockquote style="border-left:3px solid var(--color-accent);padding:0.4rem 0.75rem;margin:0.4rem 0;background:rgba(99,102,241,0.06);border-radius:0 6px 6px 0;color:var(--color-text-secondary)">${inlineFormat(content)}</blockquote>`);
      continue;
    }

    // ── Unordered list item ── (lines starting with - )
    const li = line.match(/^[-•]\s+(.+)/);
    if (li) {
      if (!inList) { out.push('<ul style="padding-left:1.25rem;margin:0.375rem 0">'); inList = true; }
      out.push(`<li style="margin-bottom:0.2rem;color:var(--color-text-secondary)">${inlineFormat(li[1])}</li>`);
      continue;
    }

    // ── Numbered list item ──
    const oli = line.match(/^(\d+)\.\s+(.+)/);
    if (oli) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push(`<div style="display:flex;gap:0.4rem;margin-bottom:0.2rem;color:var(--color-text-secondary)"><span style="color:var(--color-accent-hover);font-weight:600;flex-shrink:0">${oli[1]}.</span><span>${inlineFormat(oli[2])}</span></div>`);
      continue;
    }

    // ── Blank line ──
    if (line.trim() === '') {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<div style="margin-top:0.5rem"></div>');
      continue;
    }

    // ── Normal paragraph ──
    if (inList) { out.push('</ul>'); inList = false; }
    out.push(`<span>${inlineFormat(line)}</span><br/>`);
  }

  if (inList) out.push('</ul>');
  return out.join('\n');
}

/** Format inline elements: bold, italic, code, links */
function inlineFormat(text: string): string {
  let s = text;
  // Escape HTML entities (but preserve already-safe content)
  s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // Inline code first (protect from other replacements)
  s = s.replace(/`([^`]+)`/g, '<code style="background:rgba(99,102,241,0.12);padding:0.1rem 0.3rem;border-radius:4px;font-size:0.85em;color:var(--color-accent-hover)">$1</code>');
  // Bold: **text**
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--color-text-primary)">$1</strong>');
  // Italic: *text*
  s = s.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
  return s;
}

// ---------- Sample Questions ----------
const SAMPLE_QUESTIONS = [
  {
    icon: '💊',
    label: 'Medication Query',
    text: 'What antiplatelet therapy was prescribed after the coronary angioplasty, and for how long?',
  },
  {
    icon: '🧠',
    label: 'Diagnosis Lookup',
    text: 'What diagnostic findings led to the Multiple Sclerosis diagnosis for patient Elena Rostova?',
  },
  {
    icon: '🫁',
    label: 'Treatment Plan',
    text: 'What is the targeted therapy prescribed for the EGFR-positive lung adenocarcinoma patient?',
  },
  {
    icon: '📋',
    label: 'Cross-Patient',
    text: 'Compare the treatment plans across all three patients. What common follow-up patterns exist?',
  },
];

interface CitationItem {
  index: number;
  filename: string;
  section: string;
  document_id: string;
  chunk_id: string;
  score: number;
  snippet?: string;
  strategy?: string;
  metric?: string;
}

const RagTelemetryDrawer: React.FC<{ citations?: string | null }> = ({ citations }) => {
  const [open, setOpen] = useState(false);
  if (!citations) return null;

  let items: CitationItem[] = [];
  try {
    items = JSON.parse(citations);
  } catch {
    return null;
  }
  if (!Array.isArray(items) || items.length === 0) return null;

  const topMatch = items[0];

  return (
    <div style={{ marginTop: '0.875rem', paddingTop: '0.625rem', borderTop: '1px dashed rgba(255,255,255,0.1)' }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.35rem 0.75rem',
          borderRadius: 'var(--radius-sm)',
          background: open ? 'rgba(99, 102, 241, 0.2)' : 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.35)',
          color: 'var(--color-accent-hover)',
          fontFamily: 'var(--font-family)',
          fontSize: 'var(--font-size-xs)',
          fontWeight: 600,
          cursor: 'pointer',
          transition: 'all var(--transition-fast)'
        }}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(99, 102, 241, 0.25)'}
        onMouseLeave={(e) => e.currentTarget.style.background = open ? 'rgba(99, 102, 241, 0.2)' : 'rgba(99, 102, 241, 0.1)'}
      >
        <span>🛠️</span>
        <span>{open ? 'Hide RAG Retrieval Telemetry ▲' : 'Inspect RAG Retrieval Engine & Telemetry ▼'}</span>
      </button>

      {open && (
        <div
          className="animate-fade-in"
          style={{
            marginTop: '0.75rem',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(15, 23, 42, 0.75)',
            border: '1px solid rgba(148, 163, 184, 0.2)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--color-text-secondary)',
            boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.3)',
          }}
        >
          {/* Telemetry Header Badge bar */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', marginBottom: '0.875rem', paddingBottom: '0.625rem', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
            <span style={{ color: '#10b981', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              <span>●</span> HYBRID SEARCH ACTIVE
            </span>
            <span className="badge badge-info" style={{ fontSize: '10px' }}>QDRANT VECTOR DB</span>
            <span className="badge badge-warning" style={{ fontSize: '10px' }}>384-DIM DENSE EMBEDDINGS</span>
            <span style={{ marginLeft: 'auto', color: 'var(--color-text-muted)', fontSize: '11px' }}>
              Evaluated {items.length} top semantic chunks | Peak confidence: {(topMatch.score * 100).toFixed(1)}%
            </span>
          </div>

          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>
            📥 Retrieved Evidence Matrix (Fed to AI Content Window):
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            {items.map((cite, idx) => (
              <div
                key={idx}
                style={{
                  padding: '0.625rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.07)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <div style={{ fontWeight: 600, color: 'var(--color-accent-hover)', display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                    <span>#{cite.index}</span>
                    <span style={{ color: 'var(--color-text-primary)' }}>{cite.filename}</span>
                    {cite.section && (
                      <span style={{ padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(99,102,241,0.15)', fontSize: '10px', color: '#a5b4fc' }}>
                        Section: {cite.section}
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <span style={{ color: 'var(--color-text-muted)', fontSize: '10px' }}>{cite.metric || 'Cosine Similarity'}</span>
                    <span style={{ fontWeight: 700, color: cite.score > 0.85 ? '#10b981' : '#f59e0b' }}>
                      {(cite.score * 100).toFixed(1)}% match
                    </span>
                  </div>
                </div>

                {cite.strategy && (
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginBottom: '0.4rem' }}>
                    ⚙️ Chunk Strategy: <strong style={{ color: '#cbd5e1' }}>{cite.strategy}</strong>
                  </div>
                )}

                {cite.snippet && (
                  <div
                    style={{
                      fontFamily: 'monospace',
                      fontSize: '11px',
                      padding: '0.5rem',
                      borderRadius: '4px',
                      background: 'rgba(0, 0, 0, 0.4)',
                      color: '#94a3b8',
                      lineHeight: 1.4,
                      whiteSpace: 'pre-wrap',
                      overflow: 'hidden',
                      borderLeft: '2px solid #10b981'
                    }}
                  >
                    "{cite.snippet}"
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div style={{ marginTop: '0.75rem', fontSize: '11px', color: 'var(--color-text-muted)', textAlign: 'center', fontStyle: 'italic' }}>
            ℹ️ MedIntel injects these verifiable chunk buffers into the inference context window to eliminate clinical hallucination.
          </div>
        </div>
      )}
    </div>
  );
};

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

  const handleSend = (text?: string) => {
    const msg = (text || input).trim();
    if (!msg || streaming) return;
    setInput('');
    sendMessage(msg);
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
              No conversations yet.
              <br />
              <span style={{ fontSize: 'var(--font-size-xs)' }}>
                Type a question below to start one automatically.
              </span>
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
            Ask questions about your clinical documents — answers include source citations from the RAG retrieval engine
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
              <div style={{ textAlign: 'center', maxWidth: '560px', width: '100%' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔬</div>
                <h3 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 600, marginBottom: '0.375rem' }}>
                  Ask a Clinical Question
                </h3>
                <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)', lineHeight: 1.6, marginBottom: '1.5rem' }}>
                  MedIntel will search your uploaded documents, retrieve the most relevant
                  clinical excerpts, and cite sources in the response. Try one of these:
                </p>

                {/* Sample Questions Grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '0.625rem',
                }}>
                  {SAMPLE_QUESTIONS.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(q.text)}
                      style={{
                        textAlign: 'left',
                        padding: '0.875rem',
                        borderRadius: 'var(--radius-lg)',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid var(--color-border)',
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)',
                        color: 'var(--color-text-secondary)',
                        fontFamily: 'var(--font-family)',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(99, 102, 241, 0.08)';
                        e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.3)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
                        e.currentTarget.style.borderColor = 'var(--color-border)';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.375rem' }}>
                        <span style={{ fontSize: '1rem' }}>{q.icon}</span>
                        <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--color-accent-hover)' }}>
                          {q.label}
                        </span>
                      </div>
                      <p style={{ fontSize: 'var(--font-size-xs)', lineHeight: 1.45, margin: 0, color: 'var(--color-text-muted)' }}>
                        {q.text}
                      </p>
                    </button>
                  ))}
                </div>
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
                  maxWidth: msg.role === 'user' ? '65%' : '88%',
                  padding: '0.875rem 1.125rem',
                  borderRadius: msg.role === 'user'
                    ? 'var(--radius-xl) var(--radius-xl) var(--radius-sm) var(--radius-xl)'
                    : 'var(--radius-xl) var(--radius-xl) var(--radius-xl) var(--radius-sm)',
                  background: msg.role === 'user' ? 'var(--gradient-primary)' : 'var(--color-bg-card)',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--color-border)',
                  color: 'var(--color-text-primary)',
                  fontSize: 'var(--font-size-sm)',
                  lineHeight: 1.7,
                  wordBreak: 'break-word',
                }}
              >
                {msg.role === 'assistant' && (
                  <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-accent-hover)', fontWeight: 600, marginBottom: '0.375rem' }}>
                    🧬 MedIntel
                  </div>
                )}
                {msg.role === 'assistant' ? (
                  <div dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                ) : (
                  <span style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</span>
                )}
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
                {msg.role === 'assistant' && <RagTelemetryDrawer citations={msg.citations} />}
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
                onClick={() => handleSend()}
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
