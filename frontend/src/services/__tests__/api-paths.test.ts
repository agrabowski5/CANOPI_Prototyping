/**
 * API Path Tests
 *
 * These tests verify that all API service calls use the correct
 * /api/v1/ prefix to match the backend route structure.
 */

import { projectsService } from '../projectsService';
import { gridService } from '../gridService';
import { transmissionService } from '../transmissionService';
import { optimizationService } from '../optimizationService';
import { apiClient } from '../api';

jest.mock('../api', () => ({
  apiClient: {
    get: jest.fn().mockResolvedValue({ data: [] }),
    post: jest.fn().mockResolvedValue({ data: {} }),
    put: jest.fn().mockResolvedValue({ data: {} }),
    patch: jest.fn().mockResolvedValue({ data: {} }),
    delete: jest.fn().mockResolvedValue({ data: {} }),
  },
  handleApiError: jest.fn((error) => error.message || 'API Error'),
}));

describe('API Path Verification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Projects Service Paths', () => {
    it('should use /api/v1/projects/ for getProjects', async () => {
      await projectsService.getProjects();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/', expect.any(Object));
    });

    it('should use /api/v1/projects/{id} for getProject', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { id: '1', name: 'Test', location: {} },
      });
      await projectsService.getProject('1');
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/projects/1');
    });

    it('should use /api/v1/projects/ for createProject', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { id: '1', name: 'Test', location: {} },
      });
      await projectsService.createProject({
        name: 'Test',
        type: 'solar',
        latitude: 34,
        longitude: -118,
        capacity_mw: 100,
      });
      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/projects/', expect.any(Object));
    });

    it('should use /api/v1/projects/{id}/coordinates for updateProjectCoordinates', async () => {
      (apiClient.patch as jest.Mock).mockResolvedValue({
        data: { id: '1', name: 'Test', location: { lat: 35, lon: -119 } },
      });
      await projectsService.updateProjectCoordinates('1', 35, -119);
      expect(apiClient.patch).toHaveBeenCalledWith(
        '/api/v1/projects/1/coordinates',
        expect.any(Object)
      );
    });

    it('should use /api/v1/projects/bulk for bulkCreateProjects', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ data: [] });
      await projectsService.bulkCreateProjects([]);
      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/projects/bulk', expect.any(Object));
    });
  });

  describe('Grid Service Paths', () => {
    it('should use /api/v1/grid/topology for getGridTopology', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { nodes: [], branches: [] },
      });
      await gridService.getGridTopology();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/topology', expect.any(Object));
    });

    it('should use /api/v1/grid/nodes for getNetworkNodes', async () => {
      await gridService.getNetworkNodes();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/nodes', expect.any(Object));
    });

    it('should use /api/v1/grid/lines for getTransmissionLines', async () => {
      await gridService.getTransmissionLines();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/lines', expect.any(Object));
    });

    it('should use /api/v1/grid/nearest-substation for findNearestSubstation', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { id: '1', name: 'Test', coordinates: {} },
      });
      await gridService.findNearestSubstation(34, -118);
      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/grid/nearest-substation',
        expect.any(Object)
      );
    });

    it('should use /api/v1/grid/interconnection-cost for calculateInterconnectionCost', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { distance_km: 10, estimated_cost: 5000000, voltage_kv: 230 },
      });
      await gridService.calculateInterconnectionCost('proj1', 'sub1');
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/grid/interconnection-cost',
        expect.any(Object)
      );
    });
  });

  describe('Transmission Service Paths', () => {
    it('should use /api/v1/transmission/lines/geojson for getTransmissionGeoJSON', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { type: 'FeatureCollection', features: [] },
      });
      await transmissionService.getTransmissionGeoJSON();
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/transmission/lines/geojson')
      );
    });

    it('should use /api/v1/transmission/lines for getTransmissionLines', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { lines: [], count: 0 },
      });
      await transmissionService.getTransmissionLines();
      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/transmission/lines')
      );
    });

    it('should use /api/v1/transmission/stats for getStatistics', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { total_lines: 0, total_length_km: 0, total_capacity_mw: 0 },
      });
      await transmissionService.getStatistics();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/transmission/stats');
    });

    it('should use /api/v1/transmission/nearby for findNearbyLines', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { center: {}, radius_km: 10, lines: [], count: 0 },
      });
      await transmissionService.findNearbyLines({ latitude: 34, longitude: -118 });
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/transmission/nearby',
        expect.any(Object)
      );
    });

    it('should use /api/v1/transmission/voltage-classes for getVoltageClasses', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { voltage_classes: [], notes: [] },
      });
      await transmissionService.getVoltageClasses();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/transmission/voltage-classes');
    });

    it('should use /api/v1/transmission/coverage for getCoverage', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {
          data_sources: [],
          geographic_coverage: { countries: [], bbox: {} },
          total_lines: 0,
          total_length_km: 0,
        },
      });
      await transmissionService.getCoverage();
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/transmission/coverage');
    });
  });

  describe('Optimization Service Paths', () => {
    it('should use /api/v1/optimization/jobs for createOptimizationJob', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { id: '1', status: 'pending' },
      });
      await optimizationService.createOptimizationJob({
        name: 'Test',
        config: {} as any,
        project_ids: [],
      });
      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/v1/optimization/jobs',
        expect.any(Object)
      );
    });

    it('should use /api/v1/optimization/jobs for getOptimizationJobs', async () => {
      await optimizationService.getOptimizationJobs();
      expect(apiClient.get).toHaveBeenCalledWith(
        '/api/v1/optimization/jobs',
        expect.any(Object)
      );
    });

    it('should use /api/v1/optimization/jobs/{id} for getOptimizationJob', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { id: '1', status: 'running' },
      });
      await optimizationService.getOptimizationJob('1');
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/optimization/jobs/1');
    });

    it('should use /api/v1/optimization/jobs/{id}/status for getJobStatus', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { status: 'running', progress_percentage: 50 },
      });
      await optimizationService.getJobStatus('1');
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/optimization/jobs/1/status');
    });

    it('should use /api/v1/optimization/jobs/{id}/results for getJobResults', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { optimal_value: 1000000 },
      });
      await optimizationService.getJobResults('1');
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/optimization/jobs/1/results');
    });

    it('should use /api/v1/optimization/quick for runQuickOptimization', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { id: '1', status: 'pending' },
      });
      await optimizationService.runQuickOptimization([]);
      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/optimization/quick', {
        project_ids: [],
        mode: 'evaluate',
      });
    });
  });

  describe('Path Format Verification', () => {
    it('should ensure all paths start with /api/v1/', () => {
      const mockCalls = (apiClient.get as jest.Mock).mock.calls;

      mockCalls.forEach((call) => {
        const path = call[0] as string;
        if (path && typeof path === 'string') {
          expect(path).toMatch(/^\/api\/v1\//);
        }
      });
    });

    it('should not contain legacy /v1/ paths without /api prefix', async () => {
      // Reset mocks
      jest.clearAllMocks();

      // Make several service calls
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { nodes: [], branches: [] },
      });
      await gridService.getGridTopology();

      (apiClient.get as jest.Mock).mockResolvedValue({ data: [] });
      await projectsService.getProjects();

      // Check all calls
      const allCalls = [
        ...(apiClient.get as jest.Mock).mock.calls,
        ...(apiClient.post as jest.Mock).mock.calls,
      ];

      allCalls.forEach((call) => {
        const path = call[0] as string;
        if (path && typeof path === 'string' && path.includes('/v1/')) {
          // Should have /api prefix
          expect(path).toMatch(/^\/api\/v1\//);
          // Should NOT match legacy format
          expect(path).not.toMatch(/^\/v1\//);
        }
      });
    });
  });
});
