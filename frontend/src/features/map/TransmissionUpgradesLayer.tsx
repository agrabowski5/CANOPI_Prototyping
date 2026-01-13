import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { TransmissionUpgrade } from '../../types';

interface TransmissionUpgradesLayerProps {
  upgrades: TransmissionUpgrade[];
  map: mapboxgl.Map;
  visible: boolean;
}

const formatCost = (cost: number): string => {
  if (cost >= 1e9) return `$${(cost / 1e9).toFixed(1)}B`;
  if (cost >= 1e6) return `$${(cost / 1e6).toFixed(1)}M`;
  if (cost >= 1e3) return `$${(cost / 1e3).toFixed(0)}K`;
  return `$${cost.toFixed(0)}`;
};

export const TransmissionUpgradesLayer: React.FC<TransmissionUpgradesLayerProps> = ({
  upgrades,
  map,
  visible,
}) => {
  const sourceIdRef = useRef<string>('transmission-upgrades-source');
  const layerIdRef = useRef<string>('transmission-upgrades-layer');
  const animationLayerIdRef = useRef<string>('transmission-upgrades-animation');
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  useEffect(() => {
    if (!map) return;

    // Capture ref values for cleanup
    const sourceId = sourceIdRef.current;
    const layerId = layerIdRef.current;
    const animationLayerId = animationLayerIdRef.current;

    // Remove existing layers and source
    if (map.getLayer(animationLayerId)) {
      map.removeLayer(animationLayerId);
    }
    if (map.getLayer(layerId)) {
      map.removeLayer(layerId);
    }
    if (map.getSource(sourceId)) {
      map.removeSource(sourceId);
    }

    // Clear markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    if (!visible || !upgrades || upgrades.length === 0) return;

    // Create GeoJSON for the transmission lines
    const geojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: upgrades.map((upgrade, index) => ({
        type: 'Feature',
        properties: {
          id: index,
          from_node: upgrade.from_node,
          to_node: upgrade.to_node,
          capacity_add_mw: upgrade.capacity_add_mw,
          estimated_cost: upgrade.estimated_cost,
          rationale: upgrade.rationale,
        },
        geometry: {
          type: 'LineString',
          coordinates: [
            [upgrade.from_lon, upgrade.from_lat],
            [upgrade.to_lon, upgrade.to_lat],
          ],
        },
      })),
    };

    // Add source
    map.addSource(sourceId, {
      type: 'geojson',
      data: geojson,
    });

    // Add main transmission line layer (dashed green)
    map.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round',
      },
      paint: {
        'line-color': '#10B981', // Emerald green
        'line-width': 4,
        'line-dasharray': [2, 2],
        'line-opacity': 0.8,
      },
    });

    // Add animated glow layer
    map.addLayer({
      id: animationLayerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round',
      },
      paint: {
        'line-color': '#34D399', // Lighter green
        'line-width': 8,
        'line-opacity': 0.3,
        'line-blur': 3,
      },
    });

    // Add markers at midpoints with capacity info
    upgrades.forEach((upgrade) => {
      const midLat = (upgrade.from_lat + upgrade.to_lat) / 2;
      const midLon = (upgrade.from_lon + upgrade.to_lon) / 2;

      const el = document.createElement('div');
      el.className = 'transmission-upgrade-marker';
      el.innerHTML = `
        <div class="bg-emerald-500 text-white px-2 py-1 rounded-lg shadow-lg text-xs font-bold
                    border-2 border-white cursor-pointer hover:bg-emerald-600 transition-colors">
          ⚡ +${upgrade.capacity_add_mw.toFixed(0)} MW
        </div>
      `;

      const marker = new mapboxgl.Marker({
        element: el,
        anchor: 'center',
      })
        .setLngLat([midLon, midLat])
        .addTo(map);

      // Create popup
      const popup = new mapboxgl.Popup({
        offset: 15,
        closeButton: true,
        closeOnClick: false,
        maxWidth: '280px',
      }).setHTML(`
        <div class="p-3">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xl">⚡</span>
            <h3 class="font-bold text-emerald-600">Transmission Upgrade</h3>
          </div>
          <div class="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-2 mb-2">
            <p class="text-sm font-semibold text-emerald-700 dark:text-emerald-400">
              Recommended by CANOPI Optimization
            </p>
          </div>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">From:</span>
              <span class="font-semibold">${upgrade.from_node}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">To:</span>
              <span class="font-semibold">${upgrade.to_node}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Capacity Addition:</span>
              <span class="font-semibold text-emerald-600">+${upgrade.capacity_add_mw.toFixed(0)} MW</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Estimated Cost:</span>
              <span class="font-semibold">${formatCost(upgrade.estimated_cost)}</span>
            </div>
          </div>
          <div class="mt-3 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-600 dark:text-gray-400 italic">
              "${upgrade.rationale}"
            </p>
          </div>
        </div>
      `);

      el.addEventListener('click', (e) => {
        e.stopPropagation();
        marker.setPopup(popup);
        popup.addTo(map);
      });

      markersRef.current.push(marker);
    });

    return () => {
      if (map.getLayer(animationLayerId)) {
        map.removeLayer(animationLayerId);
      }
      if (map.getLayer(layerId)) {
        map.removeLayer(layerId);
      }
      if (map.getSource(sourceId)) {
        map.removeSource(sourceId);
      }
      markersRef.current.forEach(marker => marker.remove());
      markersRef.current = [];
    };
  }, [map, upgrades, visible]);

  return null;
};

export default TransmissionUpgradesLayer;
