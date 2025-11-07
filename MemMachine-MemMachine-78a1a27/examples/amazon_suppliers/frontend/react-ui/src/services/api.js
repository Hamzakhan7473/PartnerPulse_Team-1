import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 100000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const supplierApi = {
  // Ingest supplier comments
  ingestSupplierData: async (comments, interactionDate = null) => {
    const response = await api.post('/supplier/ingest', { 
      comments,
      interaction_date: interactionDate || null
    });
    return response.data;
  },

  // Query supplier
  querySupplier: async (query) => {
    const response = await api.post('/supplier/query', { query });
    return response.data;
  },

  // Chat with LLM (calls backend endpoint)
  chatWithLLM: async (messages, supplierId, modelId = 'gpt-4.1-mini') => {
    const response = await api.post('/supplier/chat', {
      messages,
      supplier_id: supplierId,
      model_id: modelId,
    });
    return response.data;
  },

  // CRM Profile APIs
  addSupplierProfile: async (profileData) => {
    const response = await api.post('/crm/supplier/profile', profileData);
    return response.data;
  },

  getSupplierProfile: async (supplierId) => {
    const response = await api.get(`/crm/supplier/profile/${supplierId}`);
    return response.data;
  },

  listSuppliers: async (search = null) => {
    const params = search ? { search } : {};
    const response = await api.get('/crm/suppliers', { params });
    return response.data;
  },

  // Health checks
  getSystemHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;

