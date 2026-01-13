import { apiClient, handleApiError } from './api';
import { Project, CreateProjectRequest } from '../types';

// Transform backend project data to frontend format
const transformProject = (backendProject: any): Project => {
  return {
    id: backendProject.id,
    name: backendProject.name,
    type: backendProject.type,
    coordinates: {
      latitude: backendProject.location?.lat || 0,
      longitude: backendProject.location?.lon || 0,
    },
    capacity_mw: backendProject.capacity_mw,
    capex_per_mw: backendProject.parameters?.capex
      ? backendProject.parameters.capex / backendProject.capacity_mw
      : undefined,
    opex_per_mw: backendProject.parameters?.opex
      ? backendProject.parameters.opex / backendProject.capacity_mw
      : undefined,
    status: backendProject.status,
    created_at: backendProject.created_at,
    updated_at: backendProject.updated_at,
  };
};

export const projectsService = {
  // Get all projects
  async getProjects(params?: {
    skip?: number;
    limit?: number;
    type?: string;
  }): Promise<Project[]> {
    try {
      const response = await apiClient.get<any[]>('/api/api/v1/projects/', {
        params,
      });
      // Backend returns array directly, transform each project
      return response.data.map(transformProject);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get a single project by ID
  async getProject(id: string): Promise<Project> {
    try {
      const response = await apiClient.get<any>(`/api/v1/projects/${id}`);
      return transformProject(response.data);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Create a new project
  async createProject(data: CreateProjectRequest): Promise<Project> {
    try {
      const response = await apiClient.post<any>('/api/v1/projects/', data);
      return transformProject(response.data);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Update an existing project
  async updateProject(id: string, data: Partial<CreateProjectRequest>): Promise<Project> {
    try {
      const response = await apiClient.put<any>(`/api/v1/projects/${id}`, data);
      return transformProject(response.data);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Delete a project
  async deleteProject(id: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/projects/${id}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Update project coordinates (for drag and drop)
  async updateProjectCoordinates(
    id: string,
    latitude: number,
    longitude: number
  ): Promise<Project> {
    try {
      const response = await apiClient.patch<any>(`/api/v1/projects/${id}/coordinates`, {
        latitude,
        longitude,
      });
      return transformProject(response.data);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Bulk create projects
  async bulkCreateProjects(projects: CreateProjectRequest[]): Promise<Project[]> {
    try {
      const response = await apiClient.post<any[]>('/api/v1/projects/bulk', {
        projects,
      });
      return response.data.map(transformProject);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

export default projectsService;
