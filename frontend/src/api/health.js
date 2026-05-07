import { api } from './client';

export const fetchHealth = () => api.get('/health/');
export const fetchHealthDetailed = () => api.get('/health/detailed/');
