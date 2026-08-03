// frontend/src/pages/DashboardPage.tsx
import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { useAuth } from '../hooks/useAuth';

interface DashboardData {
  total_documents: number;
  recent_documents_7d: number;
  document_types: Record<string, number>;
  ingestion_status: Record<string, number>;
  total_conversations: number;
  total_messages: number;
  recent_uploads: Array<{
    id: number;
    filename: string;
    content_type: string;
    uploaded_at: string | null;
  }>;
  recent_conversations: Array<{
    id: string;
    title: string;
    updated_at: string | null;
  }>;
}

const StatCard: React.FC<{
  label: string;
  value: string | number;
  icon: string;
  color: string;
  delay?: number;
}> = ({ label, value, icon, color, delay = 0 }) => (
  <div
    className="glass-card animate-fade-in"
    style={{
      padding: '1.5rem',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
      animationDelay: `${delay}ms`,
    }}
  >
    <div
      style={{
        width: '48px',
        height: '48px',
        borderRadius: 'var(--radius-lg)',
        background: `${color}20`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '1.5rem',
        flexShrink: 0,
      }}
    >
      {icon}
    </div>
    <div>
      <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, color: 'var(--color-text-primary)', lineHeight: 1.2 }}>
        {value}
      </div>
      <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)' }}>
        {label}
      </div>
    </div>
  </div>
);

interface DashboardPageProps {
  onNavigate?: (page: string) => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/patients/dashboard')
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: '40px', height: '40px',
              border: '3px solid var(--color-border)',
              borderTop: '3px solid var(--color-accent)',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 1rem',
            }}
          />
          <p style={{ color: 'var(--color-text-secondary)' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const hasDocs = (data?.total_documents || 0) > 0;
  const hasConversations = (data?.total_conversations || 0) > 0;

  const steps = [
    {
      number: 1,
      title: 'Upload Clinical Documents',
      description: hasDocs
        ? `${data?.total_documents} document${(data?.total_documents || 0) !== 1 ? 's' : ''} ready — upload more or proceed to Step 2`
        : 'Upload PDFs, DOCX, or text files of clinical records. Demo documents are pre-loaded for you.',
      completed: hasDocs,
      action: () => onNavigate?.('upload'),
      actionLabel: hasDocs ? 'Upload More' : 'Upload Documents →',
      icon: '📄',
    },
    {
      number: 2,
      title: 'Ask Questions with AI Chat',
      description: hasConversations
        ? `${data?.total_conversations} conversation${(data?.total_conversations || 0) !== 1 ? 's' : ''} started — continue chatting`
        : 'Ask natural language questions about your documents. MedIntel retrieves relevant sections and cites sources.',
      completed: hasConversations,
      action: () => onNavigate?.('chat'),
      actionLabel: hasConversations ? 'Continue Chat' : 'Start Clinical Chat →',
      icon: '💬',
    },
    {
      number: 3,
      title: 'Explore Semantic Search',
      description: 'Search across all documents using AI-powered semantic understanding — not just keyword matching.',
      completed: false,
      action: () => onNavigate?.('search'),
      actionLabel: 'Try Semantic Search →',
      icon: '🔍',
    },
  ];

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, marginBottom: '0.25rem' }}>
          Welcome{user?.full_name ? `, ${user.full_name}` : ''} 👋
        </h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          Your clinical intelligence workspace is ready. Follow the steps below to explore.
        </p>
      </div>

      {/* Getting Started Stepper */}
      <div
        className="glass-card animate-fade-in"
        style={{
          padding: '1.75rem',
          marginBottom: '2rem',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '1.25rem' }}>
          <span
            style={{
              display: 'inline-block',
              background: 'rgba(16, 185, 129, 0.2)',
              color: '#10b981',
              padding: '0.25rem 0.75rem',
              borderRadius: '999px',
              fontSize: '11px',
              fontWeight: 600,
              letterSpacing: '0.05em',
              textTransform: 'uppercase' as const,
            }}
          >
            🚀 Getting Started
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {steps.map((step, i) => (
            <div
              key={step.number}
              className="animate-fade-in"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '1rem',
                padding: '1.25rem',
                borderRadius: 'var(--radius-lg)',
                background: step.completed
                  ? 'rgba(16, 185, 129, 0.06)'
                  : 'rgba(255, 255, 255, 0.03)',
                border: step.completed
                  ? '1px solid rgba(16, 185, 129, 0.2)'
                  : '1px solid var(--color-border)',
                cursor: 'pointer',
                transition: 'all var(--transition-base)',
                animationDelay: `${i * 100}ms`,
              }}
              onClick={step.action}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = step.completed
                  ? 'rgba(16, 185, 129, 0.1)'
                  : 'rgba(99, 102, 241, 0.08)';
                e.currentTarget.style.borderColor = step.completed
                  ? 'rgba(16, 185, 129, 0.35)'
                  : 'rgba(99, 102, 241, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = step.completed
                  ? 'rgba(16, 185, 129, 0.06)'
                  : 'rgba(255, 255, 255, 0.03)';
                e.currentTarget.style.borderColor = step.completed
                  ? 'rgba(16, 185, 129, 0.2)'
                  : 'var(--color-border)';
              }}
            >
              {/* Step number / check */}
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: step.completed
                    ? 'rgba(16, 185, 129, 0.2)'
                    : 'rgba(99, 102, 241, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: step.completed ? '1.1rem' : '0.875rem',
                  fontWeight: 700,
                  color: step.completed ? '#10b981' : 'var(--color-accent-hover)',
                  flexShrink: 0,
                }}
              >
                {step.completed ? '✓' : step.number}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '1rem' }}>{step.icon}</span>
                  <span style={{ fontSize: 'var(--font-size-base)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                    {step.title}
                  </span>
                  {step.completed && (
                    <span className="badge badge-success" style={{ fontSize: '10px', padding: '0.15rem 0.4rem' }}>
                      Done
                    </span>
                  )}
                </div>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  {step.description}
                </p>
              </div>
              <div
                style={{
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--color-accent-hover)',
                  fontWeight: 500,
                  whiteSpace: 'nowrap' as const,
                  alignSelf: 'center',
                }}
              >
                {step.actionLabel}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <StatCard label="Total Documents" value={data?.total_documents || 0} icon="📄" color="#6366f1" delay={0} />
        <StatCard label="This Week" value={data?.recent_documents_7d || 0} icon="📈" color="#10b981" delay={100} />
        <StatCard label="Conversations" value={data?.total_conversations || 0} icon="💬" color="#8b5cf6" delay={200} />
        <StatCard label="Messages" value={data?.total_messages || 0} icon="✉️" color="#3b82f6" delay={300} />
      </div>

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Recent Uploads */}
        <div className="glass-card animate-fade-in" style={{ padding: '1.5rem', animationDelay: '400ms' }}>
          <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📁 Recent Uploads
          </h2>
          {data?.recent_uploads && data.recent_uploads.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {data.recent_uploads.slice(0, 8).map((doc) => (
                <div
                  key={doc.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.625rem 0.75rem',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-bg-glass)',
                    transition: 'background var(--transition-fast)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', minWidth: 0 }}>
                    <span style={{ fontSize: '1.1rem' }}>
                      {doc.content_type.includes('pdf') ? '📕' : doc.content_type.includes('image') ? '🖼️' : '📝'}
                    </span>
                    <span
                      style={{
                        fontSize: 'var(--font-size-sm)',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {doc.filename}
                    </span>
                  </div>
                  {doc.uploaded_at && (
                    <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', flexShrink: 0 }}>
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)', textAlign: 'center', padding: '2rem 0' }}>
              No documents uploaded yet. Start by uploading clinical documents.
            </p>
          )}
        </div>

        {/* Ingestion Status + Recent Conversations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Ingestion Status */}
          <div className="glass-card animate-fade-in" style={{ padding: '1.5rem', animationDelay: '500ms' }}>
            <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              ⚙️ Ingestion Pipeline
            </h2>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {Object.entries(data?.ingestion_status || {}).map(([status, count]) => {
                const badgeClass = status === 'completed' ? 'badge-success' : status === 'failed' ? 'badge-error' : status === 'processing' ? 'badge-warning' : 'badge-info';
                return (
                  <div key={status} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className={`badge ${badgeClass}`}>{status}</span>
                    <span style={{ fontWeight: 600, fontSize: 'var(--font-size-lg)' }}>{count}</span>
                  </div>
                );
              })}
              {Object.keys(data?.ingestion_status || {}).length === 0 && (
                <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
                  No ingestion tasks yet.
                </p>
              )}
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="glass-card animate-fade-in" style={{ padding: '1.5rem', animationDelay: '600ms', flex: 1 }}>
            <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              💬 Recent Conversations
            </h2>
            {data?.recent_conversations && data.recent_conversations.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {data.recent_conversations.map((conv) => (
                  <div
                    key={conv.id}
                    style={{
                      padding: '0.625rem 0.75rem',
                      borderRadius: 'var(--radius-md)',
                      background: 'var(--color-bg-glass)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span style={{ fontSize: 'var(--font-size-sm)' }}>{conv.title}</span>
                    {conv.updated_at && (
                      <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                        {new Date(conv.updated_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)', textAlign: 'center', padding: '1rem 0' }}>
                No conversations yet. Start a clinical chat!
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
