import axios from 'axios';

// API Base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Add auth token when authentication is implemented
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ========================================
// Projects API
// ========================================

/**
 * Get all projects
 */
export const getProjects = async () => {
  const response = await apiClient.get('/api/projects');
  return response.data;
};

/**
 * Get a single project
 * @param {string} projectId - Project ID
 */
export const getProject = async (projectId) => {
  const response = await apiClient.get(`/api/projects/${projectId}`);
  return response.data;
};

/**
 * Create a new project
 * @param {Object} data - Project data
 */
export const createProject = async (data) => {
  const response = await apiClient.post('/api/projects', data);
  return response.data;
};

/**
 * Update a project
 * @param {string} projectId - Project ID
 * @param {Object} data - Updated project data
 */
export const updateProject = async (projectId, data) => {
  const response = await apiClient.put(`/api/projects/${projectId}`, data);
  return response.data;
};

/**
 * Delete a project
 * @param {string} projectId - Project ID
 */
export const deleteProject = async (projectId) => {
  const response = await apiClient.delete(`/api/projects/${projectId}`);
  return response.data;
};

// ========================================
// Pages API
// ========================================

/**
 * Fetch list of pages with filters
 * @param {Object} params - Query parameters
 * @param {string} params.project_id - Filter by project/worldview
 * @param {string} params.category - Filter by category (e.g., 'characters/player')
 * @param {string} params.status - Filter by status (active/archived/draft)
 * @param {string} params.sort - Sort field (created_at/updated_at/title/view_count)
 * @param {string} params.order - Sort order (asc/desc)
 * @param {number} params.page - Page number
 * @param {number} params.limit - Items per page
 */
export const getPages = async (params = {}) => {
  const response = await apiClient.get('/api/pages', { params });
  return response.data;
};

/**
 * Fetch a single page by slug
 * @param {string} slug - Page slug
 */
export const getPage = async (slug) => {
  const response = await apiClient.get(`/api/pages/${slug}`);
  return response.data;
};

/**
 * Create a new page
 * @param {Object} data - Page data
 * @param {string} data.slug - Page slug
 * @param {string} data.title - Page title
 * @param {string} data.category - Page category
 * @param {string} data.content - Page content (markdown)
 * @param {string} data.author - Author name
 * @param {string} data.status - Page status (active/draft/archived)
 * @param {string} data.summary - Page summary
 * @param {string[]} data.tags - Page tags
 */
export const createPage = async (data) => {
  const response = await apiClient.post('/api/pages', data);
  return response.data;
};

/**
 * Update an existing page
 * @param {string} slug - Page slug
 * @param {Object} data - Page data to update
 * @param {string} data.title - Page title
 * @param {string} data.content - Page content (markdown)
 * @param {string} data.status - Page status
 * @param {string} data.summary - Page summary
 * @param {string[]} data.tags - Page tags
 * @param {string} data.expected_sha - Expected GitHub SHA for conflict detection
 * @param {boolean} data.force - Force update even if conflict
 */
export const updatePage = async (slug, data) => {
  const response = await apiClient.put(`/api/pages/${slug}`, data);
  return response.data;
};

/**
 * Delete a page
 * @param {string} slug - Page slug
 * @param {boolean} hard - Hard delete (remove from GitHub) vs soft delete
 */
export const deletePage = async (slug, hard = false) => {
  const response = await apiClient.delete(`/api/pages/${slug}`, {
    params: { hard },
  });
  return response.data;
};

// ========================================
// Search API
// ========================================

/**
 * Search pages
 * @param {Object} params - Search parameters
 * @param {string} params.q - Search query (required)
 * @param {string} params.category - Filter by category
 * @param {number} params.limit - Result limit (max 100)
 */
export const searchPages = async (params) => {
  const response = await apiClient.get('/api/search', { params });
  return response.data;
};

// ========================================
// Tags API
// ========================================

/**
 * Get all tags
 */
export const getTags = async () => {
  const response = await apiClient.get('/api/tags');
  return response.data;
};

/**
 * Get pages by tag
 * @param {string} tagName - Tag name
 * @param {Object} params - Query parameters
 */
export const getPagesByTag = async (tagName, params = {}) => {
  const response = await apiClient.get(`/api/tags/${tagName}/pages`, { params });
  return response.data;
};

// ========================================
// Upload API
// ========================================

/**
 * Upload an image
 * @param {File} file - Image file
 */
export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// ========================================
// Health Check
// ========================================

/**
 * Check API health
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
