import { apiClient, handleApiError } from './api';
import { OptimizationJob, OptimizationConfig, OptimizationResults } from '../types';

export const optimizationService = {
  // Create and start a new optimization job
  async createOptimizationJob(data: {
    name: string;
    config: OptimizationConfig;
    project_ids: string[];
  }): Promise<OptimizationJob> {
    try {
      const response = await apiClient.post<OptimizationJob>('/api/v1/optimization/jobs', data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get all optimization jobs
  async getOptimizationJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<OptimizationJob[]> {
    try {
      const response = await apiClient.get<OptimizationJob[]>('/api/v1/optimization/jobs', {
        params,
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get a single optimization job by ID
  async getOptimizationJob(id: string): Promise<OptimizationJob> {
    try {
      const response = await apiClient.get<OptimizationJob>(`/api/v1/optimization/jobs/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get optimization job status (for polling)
  async getJobStatus(id: string): Promise<{
    status: string;
    progress_percentage: number;
    message?: string;
  }> {
    try {
      const response = await apiClient.get(`/api/v1/optimization/jobs/${id}/status`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get optimization job results
  async getJobResults(id: string): Promise<OptimizationResults> {
    try {
      const response = await apiClient.get<OptimizationResults>(
        `/api/v1/optimization/jobs/${id}/results`
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Cancel a running optimization job
  async cancelJob(id: string): Promise<void> {
    try {
      await apiClient.post(`/api/v1/optimization/jobs/${id}/cancel`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Delete an optimization job
  async deleteJob(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/optimization/jobs/${id}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Run quick optimization (simplified interface)
  async runQuickOptimization(project_ids: string[]): Promise<OptimizationJob> {
    try {
      const response = await apiClient.post<OptimizationJob>('/api/v1/optimization/quick', {
        project_ids,
        mode: 'evaluate',
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Run greenfield optimization - find optimal locations for new projects
  async runGreenfieldOptimization(): Promise<OptimizationJob> {
    try {
      const response = await apiClient.post<OptimizationJob>('/api/v1/optimization/quick', {
        project_ids: [],
        mode: 'greenfield',
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

export default optimizationService;
