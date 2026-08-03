// frontend/src/pages/SearchPage.tsx
import React, { useState } from 'react';
import api from '../lib/api';

interface SearchResult {
  chunk_id: number;
  document_id: number;
  filename: string;
  section_title: string | null;
  content: string;
  score: number;
}

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await api.get('/search/', { params: { query, limit: 10 } });
      setResults(res.data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, marginBottom: '0.5rem' }}>
        Semantic Search 🔍
      </h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
        Search across all ingested clinical documents using AI-powered semantic search.
      </p>

      {/* Search Bar */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem' }}>
        <input
          className="input-field"
          type="text"
          placeholder="e.g., patient history of diabetes, lab results for HbA1c..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          style={{ flex: 1, padding: '0.875rem 1rem', fontSize: 'var(--font-size-base)' }}
        />
        <button
          className="btn-primary"
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          style={{ padding: '0.875rem 1.5rem' }}
        >
          {loading ? '⏳ Searching...' : '🔍 Search'}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--font-size-sm)' }}>
            Found {results.length} result{results.length !== 1 ? 's' : ''}
          </p>
          {results.map((result, i) => (
            <div
              key={result.chunk_id}
              className="glass-card animate-fade-in"
              style={{ padding: '1.25rem', animationDelay: `${i * 80}ms` }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                  <span style={{ fontSize: '1.25rem' }}>📄</span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 'var(--font-size-sm)' }}>{result.filename}</div>
                    {result.section_title && (
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-accent-hover)' }}>
                        {result.section_title}
                      </div>
                    )}
                  </div>
                </div>
                <div
                  style={{
                    padding: '0.125rem 0.5rem',
                    borderRadius: '9999px',
                    background: `rgba(99, 102, 241, ${Math.min(result.score, 1) * 0.3})`,
                    color: 'var(--color-accent-hover)',
                    fontSize: 'var(--font-size-xs)',
                    fontWeight: 600,
                  }}
                >
                  {(result.score * 100).toFixed(0)}% match
                </div>
              </div>
              <p style={{
                fontSize: 'var(--font-size-sm)',
                color: 'var(--color-text-secondary)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
              }}>
                {result.content.length > 500 ? result.content.slice(0, 500) + '...' : result.content}
              </p>
            </div>
          ))}
        </div>
      )}

      {searched && !loading && results.length === 0 && (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔎</div>
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '0.5rem' }}>
            No results found
          </h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
            Try a different query or upload more documents.
          </p>
        </div>
      )}

      {!searched && (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧠</div>
          <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '0.5rem' }}>
            AI-Powered Document Search
          </h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)', maxWidth: '400px', margin: '0 auto' }}>
            Search uses semantic embeddings to find relevant document sections,
            not just keyword matching. Try natural language queries!
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
