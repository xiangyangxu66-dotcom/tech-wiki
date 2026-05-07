import { api } from './client';
export const fetchCategories = () => api.get('/categories/');
