import { apiClient, handleApiError } from './api';
import { GridTopology, NetworkNode, TransmissionLine } from '../types';

export const gridService = {
  // Get grid topology for a region
  async getGridTopology(params?: {
    min_lat?: number;
    max_lat?: number;
    min_lon?: number;
    max_lon?: number;
    voltage_threshold?: number;
    limit?: number;
  }): Promise<GridTopology> {
    try {
      const response = await apiClient.get<any>('/api/v1/grid/topology', {
        params,
      });

      // Transform backend format to frontend format
      const backendData = response.data;
      return {
        nodes: (backendData.nodes || []).map((node: any) => ({
          id: node.id,
          name: node.name,
          coordinates: {
            latitude: node.latitude,
            longitude: node.longitude,
          },
          voltage_kv: node.voltage_kv,
          type: node.type,
        })),
        lines: (backendData.branches || []).map((branch: any) => ({
          id: branch.id,
          from_node_id: branch.from_node_id,
          to_node_id: branch.to_node_id,
          capacity_mw: branch.capacity_mw,
          voltage_kv: branch.voltage_kv,
          length_km: branch.length_km,
          status: 'operational', // Default status
        })),
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get network nodes
  async getNetworkNodes(params?: {
    type?: 'substation' | 'generator' | 'load';
    voltage_min?: number;
  }): Promise<NetworkNode[]> {
    try {
      const response = await apiClient.get<NetworkNode[]>('/api/v1/grid/nodes', {
        params,
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get transmission lines
  async getTransmissionLines(params?: {
    status?: 'operational' | 'planned' | 'under_construction';
    voltage_min?: number;
  }): Promise<TransmissionLine[]> {
    try {
      const response = await apiClient.get<TransmissionLine[]>('/api/v1/grid/lines', {
        params,
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Find nearest substation to a location
  async findNearestSubstation(latitude: number, longitude: number): Promise<NetworkNode> {
    try {
      const response = await apiClient.get<NetworkNode>('/api/v1/grid/nearest-substation', {
        params: { latitude, longitude },
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Calculate interconnection cost
  async calculateInterconnectionCost(
    projectId: string,
    substationId: string
  ): Promise<{
    distance_km: number;
    estimated_cost: number;
    voltage_kv: number;
  }> {
    try {
      const response = await apiClient.post('/api/v1/grid/interconnection-cost', {
        project_id: projectId,
        substation_id: substationId,
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

export default gridService;
