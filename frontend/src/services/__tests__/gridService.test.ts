import { gridService } from '../gridService';
import { apiClient } from '../api';

jest.mock('../api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
  handleApiError: jest.fn((error) => error.message || 'API Error'),
}));

describe('gridService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getGridTopology', () => {
    it('should fetch and transform grid topology', async () => {
      const mockBackendData = {
        nodes: [
          {
            id: 'node1',
            name: 'Substation A',
            latitude: 34.05,
            longitude: -118.25,
            voltage_kv: 500,
            type: 'substation',
          },
        ],
        branches: [
          {
            id: 'branch1',
            from_node_id: 'node1',
            to_node_id: 'node2',
            capacity_mw: 1000,
            voltage_kv: 500,
            length_km: 50,
          },
        ],
      };

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockBackendData });

      const topology = await gridService.getGridTopology({
        min_lat: 30,
        max_lat: 40,
        min_lon: -120,
        max_lon: -110,
      });

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/topology', {
        params: {
          min_lat: 30,
          max_lat: 40,
          min_lon: -120,
          max_lon: -110,
        },
      });

      expect(topology.nodes).toHaveLength(1);
      expect(topology.nodes[0]).toMatchObject({
        id: 'node1',
        name: 'Substation A',
        coordinates: { latitude: 34.05, longitude: -118.25 },
        voltage_kv: 500,
        type: 'substation',
      });

      expect(topology.lines).toHaveLength(1);
      expect(topology.lines[0]).toMatchObject({
        id: 'branch1',
        from_node_id: 'node1',
        to_node_id: 'node2',
        capacity_mw: 1000,
        status: 'operational',
      });
    });

    it('should handle empty topology', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: { nodes: [], branches: [] },
      });

      const topology = await gridService.getGridTopology();

      expect(topology.nodes).toEqual([]);
      expect(topology.lines).toEqual([]);
    });
  });

  describe('getNetworkNodes', () => {
    it('should fetch network nodes with filters', async () => {
      const mockNodes = [
        {
          id: 'node1',
          name: 'Substation A',
          coordinates: { latitude: 34.05, longitude: -118.25 },
          voltage_kv: 500,
          type: 'substation',
        },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockNodes });

      const nodes = await gridService.getNetworkNodes({
        type: 'substation',
        voltage_min: 230,
      });

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/nodes', {
        params: { type: 'substation', voltage_min: 230 },
      });
      expect(nodes).toEqual(mockNodes);
    });
  });

  describe('findNearestSubstation', () => {
    it('should find nearest substation to coordinates', async () => {
      const mockSubstation = {
        id: 'sub1',
        name: 'Nearest Substation',
        coordinates: { latitude: 34.06, longitude: -118.24 },
        voltage_kv: 230,
        type: 'substation',
      };

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockSubstation });

      const substation = await gridService.findNearestSubstation(34.05, -118.25);

      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/grid/nearest-substation', {
        params: { latitude: 34.05, longitude: -118.25 },
      });
      expect(substation).toEqual(mockSubstation);
    });
  });

  describe('calculateInterconnectionCost', () => {
    it('should calculate interconnection cost', async () => {
      const mockCostData = {
        distance_km: 25.5,
        estimated_cost: 12750000,
        voltage_kv: 230,
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockCostData });

      const costData = await gridService.calculateInterconnectionCost('project1', 'sub1');

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/grid/interconnection-cost', {
        project_id: 'project1',
        substation_id: 'sub1',
      });
      expect(costData).toEqual(mockCostData);
      expect(costData.distance_km).toBe(25.5);
      expect(costData.estimated_cost).toBe(12750000);
    });
  });
});
