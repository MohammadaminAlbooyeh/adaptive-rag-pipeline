import { apiClient } from './api';

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient('/documents/upload', {
    method: 'POST',
    body: formData,
    headers: {},
  });
}

export async function listDocuments() {
  return apiClient('/documents');
}
