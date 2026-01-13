import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { OptimalLocation } from '../../types';

interface OptimalLocationsLayerProps {
  locations: OptimalLocation[];
  map: mapboxgl.Map;
  visible: boolean;
}

const getLocationIcon = (type: string): string => {
  switch (type) {
    case 'solar':
      return '🌞';
    case 'wind':
      return '🌬️';
    case 'storage':
      return '🔋';
    default:
      return '📍';
  }
};

const getLocationColor = (type: string): string => {
  switch (type) {
    case 'solar':
      return '#F97316'; // Orange
    case 'wind':
      return '#0EA5E9'; // Sky blue
    case 'storage':
      return '#A855F7'; // Purple
    default:
      return '#10B981'; // Green
  }
};

const formatCost = (cost: number): string => {
  if (cost >= 1e9) return `$${(cost / 1e9).toFixed(1)}B`;
  if (cost >= 1e6) return `$${(cost / 1e6).toFixed(1)}M`;
  if (cost >= 1e3) return `$${(cost / 1e3).toFixed(0)}K`;
  return `$${cost.toFixed(0)}`;
};

export const OptimalLocationsLayer: React.FC<OptimalLocationsLayerProps> = ({
  locations,
  map,
  visible,
}) => {
  const markersRef = useRef<mapboxgl.Marker[]>([]);

  useEffect(() => {
    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    if (!map || !visible || !locations || locations.length === 0) return;

    // Create markers for each optimal location
    locations.forEach((location) => {
      const el = document.createElement('div');
      el.className = 'optimal-location-marker';
      el.innerHTML = `
        <div class="flex flex-col items-center cursor-pointer transition-transform hover:scale-110 animate-pulse-slow">
          <div class="relative">
            <div class="absolute -inset-2 rounded-full opacity-30 animate-ping"
                 style="background-color: ${getLocationColor(location.type)};">
            </div>
            <div class="text-3xl relative z-10" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">
              ${getLocationIcon(location.type)}
            </div>
          </div>
          <div class="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-2 py-1 rounded-full shadow-lg text-xs font-bold mt-1 border-2 border-white">
            ${location.capacity_mw.toFixed(0)} MW
          </div>
        </div>
      `;

      const marker = new mapboxgl.Marker({
        element: el,
        anchor: 'bottom',
      })
        .setLngLat([location.lon, location.lat])
        .addTo(map);

      // Create detailed popup
      const capacityFactor = location.capacity_factor
        ? `${(location.capacity_factor * 100).toFixed(0)}%`
        : 'N/A';
      const lcoe = location.lcoe
        ? `$${location.lcoe.toFixed(2)}/MWh`
        : 'N/A';

      const popup = new mapboxgl.Popup({
        offset: 25,
        closeButton: true,
        closeOnClick: false,
        maxWidth: '300px',
      }).setHTML(`
        <div class="p-3">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-2xl">${getLocationIcon(location.type)}</span>
            <h3 class="font-bold text-lg capitalize" style="color: ${getLocationColor(location.type)}">
              ${location.type} Project
            </h3>
          </div>
          <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 mb-2">
            <p class="text-sm font-semibold text-green-700 dark:text-green-400">
              Recommended by CANOPI Optimization
            </p>
          </div>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500">Capacity:</span>
              <span class="font-semibold">${location.capacity_mw.toFixed(0)} MW</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Capacity Factor:</span>
              <span class="font-semibold">${capacityFactor}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">LCOE:</span>
              <span class="font-semibold">${lcoe}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Interconnection Cost:</span>
              <span class="font-semibold">${formatCost(location.interconnection_cost)}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">Grid Node:</span>
              <span class="font-semibold">${location.grid_node}</span>
            </div>
          </div>
          <div class="mt-3 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-600 dark:text-gray-400 italic">
              "${location.rationale}"
            </p>
          </div>
          <div class="mt-2 text-xs text-gray-400">
            Location: ${location.lat.toFixed(4)}, ${location.lon.toFixed(4)}
          </div>
        </div>
      `);

      // Show popup on click
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        marker.setPopup(popup);
        popup.addTo(map);
      });

      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach(marker => marker.remove());
      markersRef.current = [];
    };
  }, [map, locations, visible]);

  return null;
};

export default OptimalLocationsLayer;
