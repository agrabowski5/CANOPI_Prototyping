import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MapViewState, MapLayers } from '../types';

interface MapState {
  viewState: MapViewState;
  layers: MapLayers;
  mapInstance: any | null;
  isMapLoaded: boolean;
  hoveredFeature: string | null;
  selectedFeature: string | null;
}

const initialState: MapState = {
  viewState: {
    longitude: -114.0, // Center on Western US
    latitude: 39.0,
    zoom: 5,
    pitch: 0,
    bearing: 0,
  },
  layers: {
    projects: true,
    grid: true,
    transmission: true,
    substations: true,
    terrain: false,
    satellite: false,
    optimalLocations: true,
    transmissionUpgrades: true,
  },
  mapInstance: null,
  isMapLoaded: false,
  hoveredFeature: null,
  selectedFeature: null,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setViewState: (state, action: PayloadAction<Partial<MapViewState>>) => {
      state.viewState = { ...state.viewState, ...action.payload };
    },
    toggleLayer: (state, action: PayloadAction<keyof MapLayers>) => {
      state.layers[action.payload] = !state.layers[action.payload];
    },
    setLayerVisibility: (
      state,
      action: PayloadAction<{ layer: keyof MapLayers; visible: boolean }>
    ) => {
      state.layers[action.payload.layer] = action.payload.visible;
    },
    setMapInstance: (state, action: PayloadAction<any | null>) => {
      state.mapInstance = action.payload;
      state.isMapLoaded = action.payload !== null;
    },
    setHoveredFeature: (state, action: PayloadAction<string | null>) => {
      state.hoveredFeature = action.payload;
    },
    setSelectedFeature: (state, action: PayloadAction<string | null>) => {
      state.selectedFeature = action.payload;
    },
    flyTo: (state, action: PayloadAction<{ longitude: number; latitude: number; zoom?: number }>) => {
      state.viewState.longitude = action.payload.longitude;
      state.viewState.latitude = action.payload.latitude;
      if (action.payload.zoom !== undefined) {
        state.viewState.zoom = action.payload.zoom;
      }
    },
    resetView: (state) => {
      state.viewState = initialState.viewState;
    },
  },
});

export const {
  setViewState,
  toggleLayer,
  setLayerVisibility,
  setMapInstance,
  setHoveredFeature,
  setSelectedFeature,
  flyTo,
  resetView,
} = mapSlice.actions;

export default mapSlice.reducer;
