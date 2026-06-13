import { apiClient } from './api';

export async function getAnalytics() {
  return apiClient('/analytics');
}
