import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 120000, // 2 minutes to allow AI batch extraction to complete without timing out
});

/**
 * Sets or clears the Authorization header on all future apiClient requests.
 * Called by AuthContext's login() and logout() functions.
 */
export function setAuthToken(token) {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
}

// Intercept 401 Unauthorized responses — token expired or invalid.
// Clear session and redirect to landing page so user can re-authenticate.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      sessionStorage.removeItem('token');
      delete apiClient.defaults.headers.common['Authorization'];
      // Only redirect if not already on the landing page
      if (!window.location.pathname || window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
