import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors for error handling later if needed
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Just a placeholder for global error handling
    return Promise.reject(error);
  }
);
