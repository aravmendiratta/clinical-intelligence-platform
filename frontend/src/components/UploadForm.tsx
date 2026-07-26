import React, { useState } from 'react';
import axios from 'axios';
import { CloudUploadIcon } from '@heroicons/react/24/solid';

const UploadForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setMessage('');
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await axios.post('/api/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(`Uploaded: ${res.data.filename || file.name}`);
    } catch (err) {
      setMessage('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      className="w-full max-w-md p-6 bg-glass backdrop-blur-xs rounded-xl shadow-lg border border-white/20"
      onDragOver={e => e.preventDefault()}
      onDrop={onDrop}
    >
      <h2 className="text-2xl font-semibold text-secondary mb-4">Upload File</h2>
      <div className="flex items-center space-x-3 mb-4">
        <CloudUploadIcon className="h-6 w-6 text-primary" />
        <input type="file" onChange={onFileChange} className="flex-1 text-white bg-transparent" />
      </div>
      {file && <p className="mb-2 text-sm text-white">Selected: {file.name}</p>}
      <button
        onClick={handleUpload}
        disabled={uploading || !file}
        className={`w-full py-2 px-4 rounded bg-primary hover:bg-primary/80 transition ${{
          uploading: 'opacity-50 cursor-not-allowed',
          '!uploading && !file': 'opacity-50 cursor-not-allowed',
        }[uploading || !file ? 'uploading' : '']}`}
      >
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p className="mt-2 text-sm text-white">{message}</p>}
    </div>
  );
};

export default UploadForm;
