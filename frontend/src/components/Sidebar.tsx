// frontend/src/components/Sidebar.tsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'chat', label: 'Clinical Chat', icon: '💬' },
  { id: 'upload', label: 'Upload Documents', icon: '📄' },
  { id: 'search', label: 'Search', icon: '🔍' },
  { id: 'audit', label: 'Audit Log', icon: '📋' },
];

const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate }) => {
  const { user } = useAuth();

  return (
    <aside
      style={{
        width: '260px',
        minHeight: '100vh',
        background: 'var(--color-bg-secondary)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 0',
      }}
    >
      {/* Logo */}
      <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }} onClick={() => onNavigate('dashboard')}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-lg)',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            🧬
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, color: 'var(--color-text-primary)', lineHeight: 1.2 }}>
              MedIntel
            </h1>
            <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
              Clinical Intelligence
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '0 0.75rem' }}>
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.625rem 0.75rem',
                marginBottom: '0.25rem',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                color: isActive ? 'var(--color-accent-hover)' : 'var(--color-text-secondary)',
                cursor: 'pointer',
                fontSize: 'var(--font-size-sm)',
                fontWeight: isActive ? 600 : 400,
                fontFamily: 'var(--font-family)',
                textAlign: 'left',
                transition: 'all var(--transition-fast)',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'var(--color-bg-hover)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* GitHub Link */}
      <div style={{ padding: '0 1.5rem', marginBottom: '1rem' }}>
        <a
          href="https://github.com/aravmendiratta/clinical-intelligence-platform"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            padding: '0.625rem',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-text-primary)',
            textDecoration: 'none',
            fontSize: 'var(--font-size-sm)',
            fontWeight: 500,
            transition: 'all var(--transition-fast)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
            e.currentTarget.style.borderColor = 'rgba(255,255,255,0.2)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.05)';
            e.currentTarget.style.borderColor = 'var(--color-border)';
          }}
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          Explore Code on GitHub
        </a>
      </div>

      {/* User / Demo Status Info */}
      <div
        style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500, color: 'var(--color-text-primary)' }}>
            {user?.full_name || 'Reviewer'}
          </div>
          <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
            Full Access ({user?.role})
          </div>
        </div>
        <span
          className="badge badge-success"
          style={{
            fontSize: '11px',
            padding: '0.25rem 0.5rem',
            letterSpacing: '0.03em',
            boxShadow: '0 0 10px rgba(16, 185, 129, 0.2)',
          }}
        >
          🟢 Demo
        </span>
      </div>
    </aside>
  );
};

export default Sidebar;
