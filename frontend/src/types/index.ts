// Project Types
export enum ProjectType {
  SOLAR = 'solar',
  WIND = 'wind',
  STORAGE = 'storage',
  DATACENTER = 'datacenter',
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Project {
  id: string;
  name: string;
  type: ProjectType;
  coordinates: Coordinates;
  capacity_mw: number;
  capex_per_mw?: number;
  opex_per_mw?: number;
  status?: 'draft' | 'active' | 'optimized';
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}

export interface CreateProjectRequest {
  name: string;
  type: ProjectType;
  coordinates: Coordinates;
  capacity_mw: number;
  capex_per_mw?: number;
  opex_per_mw?: number;
}

// Network Types
export interface NetworkNode {
  id: string;
  name: string;
  coordinates: Coordinates;
  voltage_kv: number;
  type: 'substation' | 'generator' | 'load';
}

export interface TransmissionLine {
  id: string;
  from_node_id: string;
  to_node_id: string;
  capacity_mw: number;
  voltage_kv: number;
  length_km: number;
  status: 'operational' | 'planned' | 'under_construction';
}

export interface GridTopology {
  nodes: NetworkNode[];
  lines: TransmissionLine[];
}

// Optimization Types
export enum OptimizationStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface OptimizationConfig {
  objective: 'minimize_cost' | 'maximize_renewable' | 'minimize_emissions';
  constraints: {
    max_budget?: number;
    min_renewable_percentage?: number;
    max_emissions?: number;
    reliability_threshold?: number;
  };
  time_horizon_years: number;
  discount_rate: number;
}

export interface OptimizationJob {
  id: string;
  name: string;
  status: OptimizationStatus;
  config: OptimizationConfig;
  project_ids: string[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress_percentage?: number;
  error_message?: string;
  results?: OptimizationResults;
}

// Greenfield Optimization Types
export interface OptimalLocation {
  type: 'solar' | 'wind' | 'storage' | 'transmission';
  lat: number;
  lon: number;
  capacity_mw: number;
  lcoe: number | null;
  capacity_factor: number | null;
  grid_node: string;
  interconnection_cost: number;
  rationale: string;
}

export interface TransmissionUpgrade {
  from_node: string;
  to_node: string;
  from_lat: number;
  from_lon: number;
  to_lat: number;
  to_lon: number;
  capacity_add_mw: number;
  estimated_cost: number;
  rationale: string;
}

export interface OptimizationRecommendation {
  type: string;
  title: string;
  value: string;
  rationale: string;
}

export interface OptimizationResults {
  total_cost: number;
  total_capacity_mw: number;
  renewable_percentage: number;
  emissions_tons_co2: number;
  lcoe: number; // Levelized Cost of Energy
  capacity_factor: number;
  optimal_configurations?: ProjectConfiguration[];
  recommendations?: OptimizationRecommendation[];
  project_results?: Record<string, any>;
  optimal_locations?: OptimalLocation[];
  transmission_upgrades?: TransmissionUpgrade[];
  network_flows?: NetworkFlows;
  sensitivity_analysis?: SensitivityAnalysis;
}

export interface ProjectConfiguration {
  project_id: string;
  recommended_capacity_mw: number;
  annual_generation_mwh: number;
  capacity_factor: number;
  npv: number;
  irr: number;
}

export interface NetworkFlows {
  timestamp: string;
  flows: {
    line_id: string;
    power_mw: number;
    utilization_percentage: number;
  }[];
}

export interface SensitivityAnalysis {
  parameters: string[];
  ranges: number[][];
  results: number[][];
}

// Scenario Types
export interface Scenario {
  id: string;
  name: string;
  description?: string;
  projects: Project[];
  optimization_config?: OptimizationConfig;
  created_at: string;
  updated_at: string;
}

// Map State Types
export interface MapViewState {
  longitude: number;
  latitude: number;
  zoom: number;
  pitch?: number;
  bearing?: number;
}

export interface MapLayers {
  projects: boolean;
  grid: boolean;
  transmission: boolean;
  substations: boolean;
  terrain: boolean;
  satellite: boolean;
  optimalLocations: boolean;
  transmissionUpgrades: boolean;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Form Types
export interface ProjectFormData {
  name: string;
  type: ProjectType;
  latitude: number;
  longitude: number;
  capacity_mw: number;
  capex_per_mw: number;
  opex_per_mw: number;
}

export interface OptimizationFormData {
  name: string;
  objective: 'minimize_cost' | 'maximize_renewable' | 'minimize_emissions';
  max_budget?: number;
  min_renewable_percentage?: number;
  time_horizon_years: number;
  discount_rate: number;
}

// Utility Types
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
