import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { toggleLayer } from '../../store/mapSlice';
import { MapLayers } from '../../types';

export const LayerControls: React.FC = () => {
  const dispatch = useAppDispatch();
  const layers = useAppSelector((state) => state.map.layers);
  const [isExpanded, setIsExpanded] = useState(false);

  const layerConfig: { key: keyof MapLayers; label: string; icon: string }[] = [
    { key: 'projects', label: 'Projects', icon: '📍' },
    { key: 'grid', label: 'Grid Network', icon: '⚡' },
    { key: 'transmission', label: 'Transmission Lines', icon: '🔌' },
    { key: 'substations', label: 'Substations', icon: '🏭' },
    { key: 'optimalLocations', label: 'Optimal Sites', icon: '🎯' },
    { key: 'transmissionUpgrades', label: 'Tx Upgrades', icon: '📈' },
    { key: 'terrain', label: 'Terrain', icon: '⛰️' },
    { key: 'satellite', label: 'Satellite', icon: '🛰️' },
  ];

  // Voltage legend for transmission lines
  const voltageLegend = [
    { voltage: '765 kV', color: '#FF0000', label: 'Ultra High' },
    { voltage: '500 kV', color: '#FF6600', label: 'Extra High' },
    { voltage: '345 kV', color: '#FFCC00', label: 'Extra High' },
    { voltage: '230 kV', color: '#00CC00', label: 'High' },
    { voltage: '138 kV', color: '#0066CC', label: 'Transmission' },
    { voltage: '69 kV', color: '#999999', label: 'Sub-transmission' },
  ];

  return (
    <div className="absolute top-4 left-4 z-10">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <span className="text-lg">🗺️</span>
            <span className="font-semibold text-sm">Map Layers</span>
          </div>
          <svg
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Layer toggles */}
        {isExpanded && (
          <div className="border-t border-gray-200 dark:border-gray-700">
            {layerConfig.map(({ key, label, icon }) => (
              <div
                key={key}
                className="px-4 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <label className="flex items-center space-x-2 cursor-pointer flex-1">
                  <span className="text-lg">{icon}</span>
                  <span className="text-sm font-medium">{label}</span>
                </label>
                <button
                  onClick={() => dispatch(toggleLayer(key))}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    layers[key]
                      ? 'bg-primary-600'
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      layers[key] ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}

            {/* Voltage Legend */}
            {layers.transmission && (
              <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
                  Voltage Legend
                </div>
                <div className="space-y-1">
                  {voltageLegend.map(({ voltage, color }) => (
                    <div key={voltage} className="flex items-center space-x-2">
                      <div
                        className="w-4 h-1 rounded"
                        style={{ backgroundColor: color }}
                      />
                      <span className="text-xs text-gray-600 dark:text-gray-300">
                        {voltage}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
