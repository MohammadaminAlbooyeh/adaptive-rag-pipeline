import React, { useState } from 'react';
import '../styles/DocumentUpload.css';

function DocumentUpload({ onUpload }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      await onUpload(file);
      setFile(null);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
    }
  };

  const acceptedFormats = '.pdf,.txt,.csv,.docx,.doc';

  return (
    <form className="document-upload" onSubmit={handleSubmit}>
      <div
        className={`upload-area ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📤</div>
          <h3>Upload Document</h3>
          <p>Drag and drop or click to select</p>

          {file && (
            <div className="file-selected">
              <span className="file-name">✓ {file.name}</span>
              <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
          )}

          <input
            type="file"
            accept={acceptedFormats}
            onChange={handleFileChange}
            className="file-input"
            disabled={loading}
          />

          <button
            type="submit"
            disabled={!file || loading}
            className="upload-btn"
          >
            {loading ? '⏳ Uploading...' : '📁 Upload Document'}
          </button>

          <p className="format-info">
            Supported: PDF, TXT, CSV, DOCX
          </p>
        </div>
      </div>
    </form>
  );
}

export default DocumentUpload;
