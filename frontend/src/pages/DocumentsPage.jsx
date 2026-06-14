import React, { useState, useEffect } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import { useDocuments } from '../hooks/useDocuments';
import '../styles/DocumentsPage.css';

function DocumentsPage() {
  const { documents, loading, error, uploadDocument, deleteDocument, fetchDocuments } = useDocuments();
  const [selectedDocs, setSelectedDocs] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (file) => {
    await uploadDocument(file);
    setSelectedDocs([]);
  };

  const handleDelete = async (docId) => {
    await deleteDocument(docId);
    setSelectedDocs((prev) => prev.filter((id) => id !== docId));
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedDocs(documents.map((d) => d.id));
    } else {
      setSelectedDocs([]);
    }
  };

  const handleSelectDoc = (docId) => {
    setSelectedDocs((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );
  };

  const handleDeleteSelected = async () => {
    if (window.confirm(`Delete ${selectedDocs.length} document(s)?`)) {
      for (const docId of selectedDocs) {
        await deleteDocument(docId);
      }
      setSelectedDocs([]);
    }
  };

  return (
    <div className="documents-page">
      <div className="documents-container">
        <div className="page-header">
          <h1>📄 Document Manager</h1>
          <p className="subtitle">Upload and manage your documents for RAG</p>
        </div>

        <div className="documents-grid">
          <div className="upload-section">
            <DocumentUpload onUpload={handleUpload} />
          </div>

          <div className="documents-section">
            <div className="section-header">
              <h2>Indexed Documents ({documents.length})</h2>
              {selectedDocs.length > 0 && (
                <button
                  className="delete-selected-btn"
                  onClick={handleDeleteSelected}
                >
                  🗑️ Delete Selected
                </button>
              )}
            </div>

            {error && (
              <div className="error-message">
                <span>❌</span> {error}
              </div>
            )}

            {loading && <div className="loading">Loading documents...</div>}

            {documents.length === 0 && !loading ? (
              <div className="empty-state">
                <p>No documents uploaded yet.</p>
                <p>Upload a document to get started!</p>
              </div>
            ) : (
              <div className="documents-list">
                <div className="list-header">
                  <input
                    type="checkbox"
                    onChange={handleSelectAll}
                    checked={
                      documents.length > 0 &&
                      selectedDocs.length === documents.length
                    }
                  />
                  <div className="col-name">Filename</div>
                  <div className="col-size">Size</div>
                  <div className="col-date">Uploaded</div>
                  <div className="col-status">Status</div>
                  <div className="col-actions">Actions</div>
                </div>

                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`document-item ${
                      selectedDocs.includes(doc.id) ? 'selected' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocs.includes(doc.id)}
                      onChange={() => handleSelectDoc(doc.id)}
                    />
                    <div className="col-name">
                      <span className="file-icon">📎</span>
                      {doc.filename}
                    </div>
                    <div className="col-size">{formatBytes(doc.size)}</div>
                    <div className="col-date">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </div>
                    <div className="col-status">
                      <span className={`status ${doc.status}`}>{doc.status}</span>
                    </div>
                    <div className="col-actions">
                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(doc.id)}
                        title="Delete document"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export default DocumentsPage;
