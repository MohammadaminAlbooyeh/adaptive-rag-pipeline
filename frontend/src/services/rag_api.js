import { apiClient } from './api';

export async function submitQuery(text, options = {}) {
  return apiClient('/query', {
    method: 'POST',
    body: JSON.stringify({ text, ...options }),
  });
}

export async function getStrategies() {
  return apiClient('/strategies');
}
