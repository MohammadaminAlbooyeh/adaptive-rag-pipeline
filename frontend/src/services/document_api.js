import { apiClient } from './api';

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
  const url = `${API_BASE}/documents/upload`;

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }

  return response.json();
}

export async function listDocuments() {
  return apiClient('/documents');
}

export async function deleteDocument(docId) {
  return apiClient(`/documents/${docId}`, {
    method: 'DELETE',
  });
}
