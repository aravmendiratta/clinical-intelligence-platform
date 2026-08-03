// frontend/src/pages/UploadPage.tsx
import React, { useCallback, useEffect, useState } from 'react';
import api from '../lib/api';

interface UploadedDoc {
  id: number;
  filename: string;
  content_type: string;
  uploaded_at: string | null;
}

const UploadPage: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [documents, setDocuments] = useState<UploadedDoc[]>([]);
  const [taskStatuses, setTaskStatuses] = useState<Record<string, { status: string; error?: string }>>({});

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await api.get('/ingest/');
      setDocuments(res.data);
    } catch (err) {
      console.error('Failed to fetch documents', err);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUpload = async (files: FileList | File[]) => {
    setUploading(true);
    for (const file of Array.from(files)) {
      setUploadProgress(`Uploading ${file.name}...`);
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await api.post('/ingest/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        const taskId = res.data.task_id;
        setTaskStatuses((prev) => ({ ...prev, [taskId]: { status: 'queued' } }));

        // Poll task status
        const pollInterval = setInterval(async () => {
          try {
            const statusRes = await api.get(`/ingest/${taskId}`);
            const { status, error_message } = statusRes.data;
            setTaskStatuses((prev) => ({ ...prev, [taskId]: { status, error: error_message } }));
            if (status === 'completed' || status === 'failed') {
              clearInterval(pollInterval);
              fetchDocuments();
            }
          } catch {
            clearInterval(pollInterval);
          }
        }, 2000);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
    setUploadProgress('');
    setUploading(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files.length) {
      handleUpload(e.dataTransfer.files);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ fontSize: 'var(--font-size-3xl)', fontWeight: 800, marginBottom: '0.5rem' }}>
        Upload Documents 📄
      </h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
        Upload clinical documents for AI-powered analysis. Supports PDF, DOCX, and image files (OCR).
      </p>

      {/* Drop Zone */}
      <div
        className="glass-card"
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        style={{
          padding: '3rem',
          textAlign: 'center',
          cursor: 'pointer',
          border: dragActive ? '2px dashed var(--color-accent)' : '2px dashed var(--color-border)',
          background: dragActive ? 'rgba(99, 102, 241, 0.05)' : 'var(--color-bg-glass)',
          borderRadius: 'var(--radius-xl)',
          transition: 'all var(--transition-base)',
          marginBottom: '2rem',
        }}
        onClick={() => {
          const input = document.createElement('input');
          input.type = 'file';
          input.multiple = true;
          input.accept = '.pdf,.docx,.doc,.png,.jpg,.jpeg,.tiff,.bmp,.txt';
          input.onchange = (e) => {
            const files = (e.target as HTMLInputElement).files;
            if (files) handleUpload(files);
          };
          input.click();
        }}
      >
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
          {uploading ? '⏳' : dragActive ? '📥' : '☁️'}
        </div>
        <p style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '0.5rem' }}>
          {uploading ? uploadProgress : 'Drag & drop files here'}
        </p>
        <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)' }}>
          or click to browse — PDF, DOCX, Images (OCR), Text files
        </p>
      </div>

      {/* Active Tasks */}
      {Object.keys(taskStatuses).length > 0 && (
        <div className="glass-card animate-fade-in" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '1rem' }}>
            ⚙️ Processing Queue
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {Object.entries(taskStatuses).map(([taskId, { status, error }]) => (
              <div
                key={taskId}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.625rem 0.75rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--color-bg-glass)',
                }}
              >
                <span style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>
                  {taskId.slice(0, 8)}...
                </span>
                <span className={`badge ${status === 'completed' ? 'badge-success' : status === 'failed' ? 'badge-error' : status === 'processing' ? 'badge-warning' : 'badge-info'}`}>
                  {status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="glass-card animate-fade-in" style={{ padding: '1.5rem' }}>
        <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 600, marginBottom: '1rem' }}>
          📁 Your Documents ({documents.length})
        </h2>
        {documents.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            {documents.map((doc) => (
              <div
                key={doc.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--color-bg-glass)',
                  transition: 'background var(--transition-fast)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
                  <span style={{ fontSize: '1.25rem' }}>
                    {doc.content_type.includes('pdf') ? '📕' : doc.content_type.includes('image') ? '🖼️' : doc.content_type.includes('word') ? '📘' : '📝'}
                  </span>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {doc.filename}
                    </div>
                    <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                      {doc.content_type}
                    </div>
                  </div>
                </div>
                {doc.uploaded_at && (
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', flexShrink: 0 }}>
                    {new Date(doc.uploaded_at).toLocaleString()}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--color-text-muted)', fontSize: 'var(--font-size-sm)', textAlign: 'center', padding: '2rem 0' }}>
            No documents uploaded yet. Drag and drop files above to get started.
          </p>
        )}
      </div>
    </div>
  );
};

export default UploadPage;
