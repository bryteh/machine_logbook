import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Configure axios defaults
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// Authenticated API instance (existing)
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout (increased from 10s)
});

// Public API instance (new - no credentials required)
const publicApi = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // 15 second timeout (increased from 10s)
});

// Add CSRF token to authenticated requests only
api.interceptors.request.use((config) => {
  // Get CSRF token from cookies - handle multiple formats
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
    console.log('Adding CSRF token to request:', csrfToken.substring(0, 10) + '...');
  } else {
    console.warn('No CSRF token found in cookies for authenticated request');
  }
  
  // Ensure credentials are included for session-based auth
  config.withCredentials = true;
  
  console.log('Making authenticated API request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Public API doesn't need CSRF tokens
publicApi.interceptors.request.use((config) => {
  console.log('Making public API request:', config.method?.toUpperCase(), config.url);
  return config;
});

// Response interceptor for authenticated API
api.interceptors.response.use(
  (response) => {
    console.log('Authenticated API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('Authenticated API Error:', error.response?.status, error.response?.data, error.config?.url);
    
    // Handle authentication errors but let AuthContext manage redirects
    if (error.response?.status === 401) {
      console.log('Unauthorized - user may need to re-login');
      // Don't force redirect here - let AuthContext handle it properly
    }
    
    // Handle CSRF token issues 
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      console.error('CSRF token issue detected:', error.response.data);
      console.log('Current cookies:', document.cookie);
      // Could implement CSRF token refresh logic here if needed
    }
    
    return Promise.reject(error);
  }
);

// Response interceptor for public API
publicApi.interceptors.response.use(
  (response) => {
    console.log('Public API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('Public API Error:', error.response?.status, error.response?.data, error.config?.url);
    return Promise.reject(error);
  }
);

// Add authentication methods
export const auth = {
  login: async (username: string, password: string) => {
    try {
      console.log('Attempting login for:', username);
      // Use api instance with credentials for login
      const response = await api.post('/auth/login/', { username, password });
      console.log('Login successful:', response.data);
      return response;
    } catch (error: any) {
      console.error('Login failed:', error.response?.data);
      throw error;
    }
  },
  
  logout: async () => {
    try {
      const response = await api.post('/auth/logout/');
      console.log('Logout successful');
      return response;
    } catch (error: any) {
      console.error('Logout failed:', error.response?.data);
      throw error;
    }
  },
  
  getCurrentUser: async () => {
    try {
      console.log('API: Making getCurrentUser request...');
      const response = await api.get('/auth/user/');
      console.log('API: getCurrentUser successful:', response.data);
      return response;
    } catch (error: any) {
      console.error('API: getCurrentUser failed:', error.response?.status, error.response?.data, error.message);
      throw error;
    }
  },
};

// Public API methods for non-authenticated operations
export const publicAPI = {
  createIssue: (data: any) => publicApi.post('/issues/', data),
  createRemedy: (issueId: string, data: any) => publicApi.post(`/issues/${issueId}/remedies/`, data),
  updateRemedy: (issueId: string, remedyId: string, data: any) => publicApi.put(`/issues/${issueId}/remedies/${remedyId}/`, data),
  getIssues: () => publicApi.get('/issues/'),
  getIssue: (id: string) => publicApi.get(`/issues/${id}/`),
  getRemedies: (issueId: string) => publicApi.get(`/issues/${issueId}/remedies/`),
  uploadRemedyAttachment: (issueId: string, remedyId: string, formData: FormData) => 
    publicApi.post(`/issues/${issueId}/remedies/${remedyId}/attachments/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
};

// Authenticated API methods
export const authAPI = {
  generateReport: async (issueId: string) => {
    // First, ensure we have a fresh CSRF token
    try {
      await api.get('/auth/csrf/'); // This will refresh the CSRF token
    } catch (error) {
      console.warn('Could not refresh CSRF token:', error);
    }
    
    return api.post(`/issues/${issueId}/generate_report/`, {}, {
      responseType: 'blob',
      headers: {
        'Accept': 'application/pdf'
      }
    });
  },
};

// RBAC API endpoints
export const rbacAPI = {
  // Roles
  getRoles: () => api.get('/roles/'),
  getRole: (id: number) => api.get(`/roles/${id}/`),
  createRole: (data: any) => api.post('/roles/', data),
  updateRole: (id: number, data: any) => api.put(`/roles/${id}/`, data),
  deleteRole: (id: number) => api.delete(`/roles/${id}/`),
  cloneRole: (id: number, data: any) => api.post(`/roles/${id}/clone/`, data),
  getPermissionMatrix: () => api.get('/roles/permission_matrix/'),
  
  // Permissions
  getPermissions: () => api.get('/permissions/'),
  getPermissionsByCategory: () => api.get('/permissions/by_category/'),
  
  // User Roles
  getUserRoles: () => api.get('/user-roles/'),
  getUserRole: (id: number) => api.get(`/user-roles/${id}/`),
  createUserRole: (data: any) => api.post('/user-roles/', data),
  updateUserRole: (id: number, data: any) => api.put(`/user-roles/${id}/`, data),
  deleteUserRole: (id: number) => api.delete(`/user-roles/${id}/`),
  getAvailableUsers: () => api.get('/user-roles/available_users/'),
  setPermissionOverride: (id: number, data: any) => api.post(`/user-roles/${id}/set_permission_override/`, data),
  removePermissionOverride: (id: number, data: any) => api.delete(`/user-roles/${id}/remove_permission_override/`, data),
  
  // Public Role
  getPublicRole: () => api.get('/public-role/current/'),
  updatePublicPermissions: (data: any) => api.post('/public-role/update_permissions/', data),
  
  // Global Settings
  getGlobalSettings: () => api.get('/global-settings/current/'),
  updateGlobalSettings: (data: any) => api.put('/global-settings/1/', data),
};

// Settings API endpoints
export const settingsAPI = {
  getSettings: () => rbacAPI.getGlobalSettings(),
  updateSettings: (data: any) => rbacAPI.updateGlobalSettings(data),
};

// User Role API endpoints  
export const userRoleAPI = {
  getUserRoles: () => rbacAPI.getUserRoles(),
  updateUserRole: (id: number, data: any) => rbacAPI.updateUserRole(id, data),
  createUserRole: (data: any) => rbacAPI.createUserRole(data),
  deleteUserRole: (id: number) => rbacAPI.deleteUserRole(id),
};

export default api;