import { api } from './client';
export const fetchTags = () => api.get('/tags/');
