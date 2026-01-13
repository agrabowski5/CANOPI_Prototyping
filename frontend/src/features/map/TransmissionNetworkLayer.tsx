/**
 * Transmission Network Layer
 *
 * Displays the full North American transmission network on the map
 * with color-coded voltage levels and capacity information.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import mapboxgl from 'mapbox-gl';
import { useAppSelector } from '../../store/hooks';
import transmissionService, { TransmissionGeoJSON } from '../../services/transmissionService';

interface TransmissionNetworkLayerProps {
  map: mapboxgl.Map;
}

// Voltage class colors
const VOLTAGE_COLORS: Record<string, string> = {
  '765': '#FF0000',     // Ultra High Voltage - Red
  '500': '#FF6600',     // Extra High Voltage - Orange
  '345': '#FFCC00',     // Extra High Voltage - Yellow
  '230': '#00CC00',     // High Voltage - Green
  '138': '#0066CC',     // Transmission - Blue
  '115': '#6666CC',     // Sub-transmission - Purple
  '69': '#999999',      // Sub-transmission - Gray
  'default': '#06B6D4', // Default - Cyan
};

// Get color based on voltage
const getVoltageColor = (voltage: number): string => {
  if (voltage >= 765) return VOLTAGE_COLORS['765'];
  if (voltage >= 500) return VOLTAGE_COLORS['500'];
  if (voltage >= 345) return VOLTAGE_COLORS['345'];
  if (voltage >= 230) return VOLTAGE_COLORS['230'];
  if (voltage >= 138) return VOLTAGE_COLORS['138'];
  if (voltage >= 115) return VOLTAGE_COLORS['115'];
  if (voltage >= 69) return VOLTAGE_COLORS['69'];
  return VOLTAGE_COLORS['default'];
};

export const TransmissionNetworkLayer: React.FC<TransmissionNetworkLayerProps> = ({ map }) => {
  const [transmissionData, setTransmissionData] = useState<TransmissionGeoJSON | null>(null);
  const [, setIsLoading] = useState(false);
  const [, setError] = useState<string | null>(null);
  const layers = useAppSelector((state) => state.map.layers);

  const sourceIdRef = useRef<string>('transmission-network-source');
  const layerIdRef = useRef<string>('transmission-network-layer');
  const hoveredLineIdRef = useRef<string | null>(null);
  const popupRef = useRef<mapboxgl.Popup | null>(null);

  // Fetch transmission data based on current viewport
  const fetchTransmissionData = useCallback(async () => {
    if (!map) return;

    setIsLoading(true);
    setError(null);

    try {
      const bounds = map.getBounds();
      if (!bounds) {
        console.warn('Map bounds not available');
        return;
      }
      const zoom = map.getZoom();

      // Determine minimum voltage based on zoom level
      // At lower zoom, only show higher voltage lines
      let minVoltage = 69;
      if (zoom < 5) minVoltage = 345;
      else if (zoom < 6) minVoltage = 230;
      else if (zoom < 7) minVoltage = 138;
      else if (zoom < 8) minVoltage = 115;

      // Clamp coordinates to valid ranges to prevent API validation errors
      // when zooming out too far (map can report bounds beyond -180/180)
      const clampLon = (lon: number) => Math.max(-180, Math.min(180, lon));
      const clampLat = (lat: number) => Math.max(-90, Math.min(90, lat));

      const data = await transmissionService.getTransmissionGeoJSON({
        min_lat: clampLat(bounds.getSouth()),
        max_lat: clampLat(bounds.getNorth()),
        min_lon: clampLon(bounds.getWest()),
        max_lon: clampLon(bounds.getEast()),
        min_voltage: minVoltage,
        simplify: zoom < 8,
        limit: 15000,
      });

      setTransmissionData(data);
    } catch (err) {
      console.error('Failed to fetch transmission data:', err);
      setError('Failed to load transmission network data');
    } finally {
      setIsLoading(false);
    }
  }, [map]);

  // Initial load and on map move
  useEffect(() => {
    if (!map || !layers.transmission) return;

    // Fetch on initial load
    fetchTransmissionData();

    // Debounced fetch on map move
    let moveTimeout: NodeJS.Timeout;
    const handleMoveEnd = () => {
      clearTimeout(moveTimeout);
      moveTimeout = setTimeout(fetchTransmissionData, 300);
    };

    map.on('moveend', handleMoveEnd);

    return () => {
      map.off('moveend', handleMoveEnd);
      clearTimeout(moveTimeout);
    };
  }, [map, layers.transmission, fetchTransmissionData]);

  // Update map layers when data changes
  useEffect(() => {
    if (!map || !transmissionData) return;

    const sourceId = sourceIdRef.current;
    const layerId = layerIdRef.current;

    // Remove existing layer and source
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
    }

    if (!layers.transmission || transmissionData.features.length === 0) {
      return;
    }

    // Add source with transmission data
    map.addSource(sourceId, {
      type: 'geojson',
      data: transmissionData,
    });

    // Add transmission lines layer with data-driven styling
    map.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round',
      },
      paint: {
        // Color based on voltage
        'line-color': [
          'case',
          ['>=', ['get', 'voltage_kv'], 765], VOLTAGE_COLORS['765'],
          ['>=', ['get', 'voltage_kv'], 500], VOLTAGE_COLORS['500'],
          ['>=', ['get', 'voltage_kv'], 345], VOLTAGE_COLORS['345'],
          ['>=', ['get', 'voltage_kv'], 230], VOLTAGE_COLORS['230'],
          ['>=', ['get', 'voltage_kv'], 138], VOLTAGE_COLORS['138'],
          ['>=', ['get', 'voltage_kv'], 115], VOLTAGE_COLORS['115'],
          ['>=', ['get', 'voltage_kv'], 69], VOLTAGE_COLORS['69'],
          VOLTAGE_COLORS['default']
        ],
        // Width based on voltage
        'line-width': [
          'interpolate',
          ['linear'],
          ['get', 'voltage_kv'],
          69, 1,
          138, 1.5,
          230, 2,
          345, 2.5,
          500, 3,
          765, 4
        ],
        'line-opacity': [
          'case',
          ['boolean', ['feature-state', 'hover'], false],
          1,
          0.7
        ],
      },
    });

    // Add hover effect
    map.on('mouseenter', layerId, (e) => {
      map.getCanvas().style.cursor = 'pointer';

      if (e.features && e.features.length > 0) {
        const feature = e.features[0];
        const featureId = feature.id as string;

        // Clear previous hover state
        if (hoveredLineIdRef.current !== null) {
          map.setFeatureState(
            { source: sourceId, id: hoveredLineIdRef.current },
            { hover: false }
          );
        }

        hoveredLineIdRef.current = featureId;
        map.setFeatureState(
          { source: sourceId, id: featureId },
          { hover: true }
        );

        // Show popup
        const props = feature.properties;
        const coordinates = (e.lngLat);

        // Remove existing popup
        if (popupRef.current) {
          popupRef.current.remove();
        }

        const voltageClass =
          props?.voltage_kv >= 500 ? 'Extra High Voltage' :
          props?.voltage_kv >= 230 ? 'High Voltage' :
          props?.voltage_kv >= 115 ? 'Transmission' : 'Sub-transmission';

        popupRef.current = new mapboxgl.Popup({
          closeButton: false,
          closeOnClick: false,
          offset: 10,
        })
          .setLngLat(coordinates)
          .setHTML(`
            <div class="p-2 min-w-48">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-3 h-3 rounded-full" style="background-color: ${getVoltageColor(props?.voltage_kv || 0)}"></div>
                <span class="font-bold text-sm">${props?.voltage_kv} kV ${voltageClass}</span>
              </div>
              <div class="text-xs space-y-1">
                <div class="flex justify-between">
                  <span class="text-gray-500">Capacity:</span>
                  <span class="font-medium">${props?.capacity_mw?.toLocaleString()} MW</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Owner:</span>
                  <span class="font-medium">${props?.owner || 'Unknown'}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Status:</span>
                  <span class="font-medium capitalize">${props?.status || 'Unknown'}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">Country:</span>
                  <span class="font-medium">${props?.country || 'Unknown'}</span>
                </div>
              </div>
            </div>
          `)
          .addTo(map);
      }
    });

    map.on('mouseleave', layerId, () => {
      map.getCanvas().style.cursor = '';

      if (hoveredLineIdRef.current !== null) {
        map.setFeatureState(
          { source: sourceId, id: hoveredLineIdRef.current },
          { hover: false }
        );
        hoveredLineIdRef.current = null;
      }

      if (popupRef.current) {
        popupRef.current.remove();
        popupRef.current = null;
      }
    });

    return () => {
      if (map.getLayer(layerId)) {
        map.removeLayer(layerId);
      }
      if (map.getSource(sourceId)) {
        map.removeSource(sourceId);
      }
      if (popupRef.current) {
        popupRef.current.remove();
      }
    };
  }, [map, transmissionData, layers.transmission]);

  return null;
};

export default TransmissionNetworkLayer;
