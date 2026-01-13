import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { reportError } from '../components/ErrorToast';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: false,  // Changed to false for wildcard CORS
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens, logging, etc.
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Helper to extract error message from various API error formats
const extractErrorMessage = (data: unknown): string => {
  if (!data) return '';

  // Handle Pydantic validation errors (array of objects)
  if (typeof data === 'object' && 'detail' in (data as Record<string, unknown>)) {
    const detail = (data as Record<string, unknown>).detail;

    // Pydantic returns detail as an array of validation errors
    if (Array.isArray(detail)) {
      return detail
        .map((err: { msg?: string; loc?: string[] }) => {
          const field = err.loc?.slice(-1)[0] || 'field';
          return `${field}: ${err.msg || 'validation error'}`;
        })
        .join(', ');
    }

    // Standard string detail
    if (typeof detail === 'string') {
      return detail;
    }
  }

  // Handle message field
  if (typeof data === 'object' && 'message' in (data as Record<string, unknown>)) {
    const message = (data as Record<string, unknown>).message;
    if (typeof message === 'string') {
      return message;
    }
  }

  return '';
};

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API Response] ${response.config.url}`, response.data);
    }
    return response;
  },
  (error: AxiosError<{ detail?: string | unknown[]; message?: string }>) => {
    // Handle common errors with visible toast notifications
    const url = error.config?.url || 'unknown endpoint';

    if (error.response) {
      const status = error.response.status;
      const detail = extractErrorMessage(error.response.data);

      switch (status) {
        case 401:
          reportError('Session expired', 'Please log in again');
          localStorage.removeItem('auth_token');
          break;
        case 403:
          reportError('Access denied', 'Insufficient permissions');
          break;
        case 404:
          reportError(`Not found: ${url}`, detail);
          break;
        case 422:
          reportError('Validation error', detail || 'Invalid request parameters');
          break;
        case 500:
          reportError('Server error', detail || 'Internal server error');
          break;
        default:
          reportError(`API Error (${status})`, detail || `Request to ${url} failed`);
      }
    } else if (error.request) {
      reportError('Network error', `Cannot reach server at ${API_BASE_URL}`);
    } else {
      reportError('Request error', error.message);
    }

    return Promise.reject(error);
  }
);

// Helper function for handling API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string | unknown[]; message?: string }>;

    if (axiosError.response?.data) {
      const message = extractErrorMessage(axiosError.response.data);
      if (message) return message;
    }

    if (axiosError.message) {
      return axiosError.message;
    }
  }

  return 'An unexpected error occurred';
};

// Generic request wrapper with error handling
export async function apiRequest<T>(
  config: AxiosRequestConfig
): Promise<T> {
  try {
    const response = await apiClient.request<T>(config);
    return response.data;
  } catch (error) {
    throw new Error(handleApiError(error));
  }
}

export default apiClient;
