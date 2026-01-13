/**
 * Transmission Line Service
 *
 * Provides access to North American transmission line data
 * including geometry, voltage levels, capacities, and statistics.
 */

import { apiClient } from './api';

export interface TransmissionLine {
  id: string;
  voltage_kv: number;
  voltage_class: string;
  owner: string;
  sub_1: string;
  sub_2: string;
  status: string;
  length_km: number;
  capacity_mw: number;
  country: string;
  state_province: string;
  distance_km?: number; // For nearby queries
}

export interface TransmissionGeoJSON {
  type: 'FeatureCollection';
  features: Array<{
    type: 'Feature';
    properties: {
      id: string;
      voltage_kv: number;
      capacity_mw: number;
      owner: string;
      status: string;
      country: string;
    };
    geometry: {
      type: 'LineString';
      coordinates: number[][];
    };
  }>;
  metadata?: {
    total_count: number;
    filtered: boolean;
  };
}

export interface TransmissionStats {
  total_lines: number;
  total_length_km: number;
  total_capacity_mw: number;
  by_country: Record<string, { count: number; length_km: number; capacity_mw: number }>;
  by_voltage_class: Record<string, { count: number; length_km: number }>;
  by_status: Record<string, number>;
  voltage_range: { min: number; max: number };
}

export interface TransmissionQueryParams {
  min_lat?: number;
  max_lat?: number;
  min_lon?: number;
  max_lon?: number;
  min_voltage?: number;
  max_voltage?: number;
  country?: string;
  status?: string;
  simplify?: boolean;
  limit?: number;
}

export interface NearbyLinesRequest {
  latitude: number;
  longitude: number;
  radius_km?: number;
  min_voltage?: number;
}

const transmissionService = {
  /**
   * Get transmission lines as GeoJSON for map visualization
   */
  async getTransmissionGeoJSON(params: TransmissionQueryParams = {}): Promise<TransmissionGeoJSON> {
    const queryParams = new URLSearchParams();

    if (params.min_lat !== undefined) queryParams.append('min_lat', String(params.min_lat));
    if (params.max_lat !== undefined) queryParams.append('max_lat', String(params.max_lat));
    if (params.min_lon !== undefined) queryParams.append('min_lon', String(params.min_lon));
    if (params.max_lon !== undefined) queryParams.append('max_lon', String(params.max_lon));
    if (params.min_voltage !== undefined) queryParams.append('min_voltage', String(params.min_voltage));
    if (params.simplify !== undefined) queryParams.append('simplify', String(params.simplify));
    if (params.limit !== undefined) queryParams.append('limit', String(params.limit));

    const response = await apiClient.get<TransmissionGeoJSON>(
      `/api/v1/transmission/lines/geojson?${queryParams.toString()}`
    );
    return response.data;
  },

  /**
   * Get transmission lines as list (without geometry)
   */
  async getTransmissionLines(params: TransmissionQueryParams = {}): Promise<{
    lines: TransmissionLine[];
    count: number;
  }> {
    const queryParams = new URLSearchParams();
    queryParams.append('format', 'list');

    if (params.min_lat !== undefined) queryParams.append('min_lat', String(params.min_lat));
    if (params.max_lat !== undefined) queryParams.append('max_lat', String(params.max_lat));
    if (params.min_lon !== undefined) queryParams.append('min_lon', String(params.min_lon));
    if (params.max_lon !== undefined) queryParams.append('max_lon', String(params.max_lon));
    if (params.min_voltage !== undefined) queryParams.append('min_voltage', String(params.min_voltage));
    if (params.max_voltage !== undefined) queryParams.append('max_voltage', String(params.max_voltage));
    if (params.country !== undefined) queryParams.append('country', params.country);
    if (params.status !== undefined) queryParams.append('status', params.status);
    if (params.limit !== undefined) queryParams.append('limit', String(params.limit));

    const response = await apiClient.get(`/api/v1/transmission/lines?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Get transmission statistics
   */
  async getStatistics(): Promise<TransmissionStats> {
    const response = await apiClient.get<TransmissionStats>('/api/v1/transmission/stats');
    return response.data;
  },

  /**
   * Find transmission lines near a point
   */
  async findNearbyLines(request: NearbyLinesRequest): Promise<{
    center: { latitude: number; longitude: number };
    radius_km: number;
    lines: TransmissionLine[];
    count: number;
  }> {
    const response = await apiClient.post('/api/v1/transmission/nearby', request);
    return response.data;
  },

  /**
   * Get voltage class reference data
   */
  async getVoltageClasses(): Promise<{
    voltage_classes: Array<{
      voltage_kv: number;
      class: string;
      typical_capacity_mw: number;
    }>;
    notes: string[];
  }> {
    const response = await apiClient.get('/api/v1/transmission/voltage-classes');
    return response.data;
  },

  /**
   * Get data coverage information
   */
  async getCoverage(): Promise<{
    data_sources: Array<{
      name: string;
      full_name: string;
      coverage: string;
      url: string;
    }>;
    geographic_coverage: {
      countries: string[];
      bbox: { min_lat: number; max_lat: number; min_lon: number; max_lon: number };
    };
    total_lines: number;
    total_length_km: number;
  }> {
    const response = await apiClient.get('/api/v1/transmission/coverage');
    return response.data;
  },
};

export default transmissionService;
