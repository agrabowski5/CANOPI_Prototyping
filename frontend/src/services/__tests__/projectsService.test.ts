import { projectsService } from '../projectsService';
import { apiClient } from '../api';
import { Project, CreateProjectRequest } from '../../types';

// Mock the API client
jest.mock('../api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    patch: jest.fn(),
    delete: jest.fn(),
  },
  handleApiError: jest.fn((error) => error.message || 'API Error'),
}));

describe('projectsService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getProjects', () => {
    it('should fetch and transform projects successfully', async () => {
      const mockBackendData = [
        {
          id: '1',
          name: 'Solar Farm 1',
          type: 'solar',
          location: { lat: 34.05, lon: -118.25 },
          capacity_mw: 100,
          parameters: { capex: 150000000, opex: 2000000 },
          status: 'active',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockBackendData });

      const projects = await projectsService.getProjects();

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/', { params: undefined });
      expect(projects).toHaveLength(1);
      expect(projects[0]).toMatchObject({
        id: '1',
        name: 'Solar Farm 1',
        type: 'solar',
        coordinates: { latitude: 34.05, longitude: -118.25 },
        capacity_mw: 100,
        status: 'active',
      });
    });

    it('should handle empty project list', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: [] });

      const projects = await projectsService.getProjects();

      expect(projects).toEqual([]);
    });

    it('should pass query parameters correctly', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: [] });

      await projectsService.getProjects({ skip: 10, limit: 20, type: 'solar' });

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/', {
        params: { skip: 10, limit: 20, type: 'solar' },
      });
    });
  });

  describe('getProject', () => {
    it('should fetch a single project by ID', async () => {
      const mockBackendData = {
        id: '1',
        name: 'Wind Farm 1',
        type: 'wind',
        location: { lat: 40.0, lon: -105.0 },
        capacity_mw: 200,
        parameters: {},
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockBackendData });

      const project = await projectsService.getProject('1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/1');
      expect(project.id).toBe('1');
      expect(project.name).toBe('Wind Farm 1');
    });
  });

  describe('createProject', () => {
    it('should create a new project', async () => {
      const newProject: CreateProjectRequest = {
        name: 'New Solar Farm',
        type: 'solar',
        latitude: 35.0,
        longitude: -110.0,
        capacity_mw: 150,
        capex_per_mw: 1500000,
        opex_per_mw: 20000,
      };

      const mockBackendResponse = {
        id: '2',
        name: 'New Solar Farm',
        type: 'solar',
        location: { lat: 35.0, lon: -110.0 },
        capacity_mw: 150,
        parameters: { capex: 225000000, opex: 3000000 },
        status: 'planned',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockBackendResponse });

      const project = await projectsService.createProject(newProject);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/projects/', newProject);
      expect(project.id).toBe('2');
      expect(project.name).toBe('New Solar Farm');
    });
  });

  describe('updateProject', () => {
    it('should update an existing project', async () => {
      const updateData = { capacity_mw: 180 };
      const mockBackendResponse = {
        id: '1',
        name: 'Updated Solar Farm',
        type: 'solar',
        location: { lat: 35.0, lon: -110.0 },
        capacity_mw: 180,
        parameters: {},
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      };

      (apiClient.put as jest.Mock).mockResolvedValue({ data: mockBackendResponse });

      const project = await projectsService.updateProject('1', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/api/v1/projects/1', updateData);
      expect(project.capacity_mw).toBe(180);
    });
  });

  describe('deleteProject', () => {
    it('should delete a project', async () => {
      (apiClient.delete as jest.Mock).mockResolvedValue({});

      await projectsService.deleteProject('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/projects/1');
    });
  });

  describe('updateProjectCoordinates', () => {
    it('should update project coordinates', async () => {
      const mockBackendResponse = {
        id: '1',
        name: 'Solar Farm',
        type: 'solar',
        location: { lat: 36.0, lon: -111.0 },
        capacity_mw: 100,
        parameters: {},
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-03T00:00:00Z',
      };

      (apiClient.patch as jest.Mock).mockResolvedValue({ data: mockBackendResponse });

      const project = await projectsService.updateProjectCoordinates('1', 36.0, -111.0);

      expect(apiClient.patch).toHaveBeenCalledWith('/api/v1/projects/1/coordinates', {
        latitude: 36.0,
        longitude: -111.0,
      });
      expect(project.coordinates.latitude).toBe(36.0);
      expect(project.coordinates.longitude).toBe(-111.0);
    });
  });

  describe('bulkCreateProjects', () => {
    it('should create multiple projects', async () => {
      const projects: CreateProjectRequest[] = [
        {
          name: 'Solar 1',
          type: 'solar',
          latitude: 35.0,
          longitude: -110.0,
          capacity_mw: 100,
        },
        {
          name: 'Wind 1',
          type: 'wind',
          latitude: 40.0,
          longitude: -105.0,
          capacity_mw: 200,
        },
      ];

      const mockBackendResponse = [
        {
          id: '1',
          name: 'Solar 1',
          type: 'solar',
          location: { lat: 35.0, lon: -110.0 },
          capacity_mw: 100,
          parameters: {},
          status: 'planned',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
        {
          id: '2',
          name: 'Wind 1',
          type: 'wind',
          location: { lat: 40.0, lon: -105.0 },
          capacity_mw: 200,
          parameters: {},
          status: 'planned',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ];

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockBackendResponse });

      const result = await projectsService.bulkCreateProjects(projects);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/projects/bulk', { projects });
      expect(result).toHaveLength(2);
    });
  });
});
