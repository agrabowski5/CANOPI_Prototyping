import React from 'react';
import { useAppSelector } from '../../store/hooks';

export const ResultsDashboard: React.FC = () => {
  const { currentJob, isRunning } = useAppSelector((state) => state.optimization);

  // Results come from currentJob.results after quick optimization
  const results = currentJob?.results;

  if (!currentJob && !results) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No Results Yet
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Run an optimization to see results here
          </p>
        </div>
      </div>
    );
  }

  if (isRunning && !results) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Optimization Running
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            This may take a few minutes...
          </p>
          {currentJob?.progress_percentage !== undefined && (
            <div className="mt-4">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${currentJob.progress_percentage}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                {currentJob.progress_percentage}% complete
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!results) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-green-600 to-emerald-600">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <span>📊</span>
            <span>Optimization Results</span>
          </h2>
          <span className="px-3 py-1 bg-white/20 text-white text-sm rounded-full">
            Completed
          </span>
        </div>
        {currentJob && (
          <p className="text-sm text-white/80 mt-1">{currentJob.name}</p>
        )}
      </div>

      <div className="p-6 space-y-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 p-4 rounded-lg border border-primary-200 dark:border-primary-800">
            <div className="text-sm text-primary-600 dark:text-primary-400 font-medium mb-1">
              Total Cost
            </div>
            <div className="text-2xl font-bold text-primary-900 dark:text-primary-100">
              ${(results.total_cost / 1000000).toFixed(1)}M
            </div>
          </div>

          <div className="bg-gradient-to-br from-secondary-50 to-secondary-100 dark:from-secondary-900/20 dark:to-secondary-800/20 p-4 rounded-lg border border-secondary-200 dark:border-secondary-800">
            <div className="text-sm text-secondary-600 dark:text-secondary-400 font-medium mb-1">
              Total Capacity
            </div>
            <div className="text-2xl font-bold text-secondary-900 dark:text-secondary-100">
              {results.total_capacity_mw.toFixed(0)} MW
            </div>
          </div>

          <div className="bg-gradient-to-br from-accent-50 to-accent-100 dark:from-accent-900/20 dark:to-accent-800/20 p-4 rounded-lg border border-accent-200 dark:border-accent-800">
            <div className="text-sm text-accent-600 dark:text-accent-400 font-medium mb-1">
              Renewable %
            </div>
            <div className="text-2xl font-bold text-accent-900 dark:text-accent-100">
              {results.renewable_percentage.toFixed(1)}%
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
            <div className="text-sm text-green-600 dark:text-green-400 font-medium mb-1">
              LCOE
            </div>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              ${results.lcoe.toFixed(2)}/MWh
            </div>
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Emissions</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {(results.emissions_tons_co2 / 1000).toFixed(1)}k tons CO2
            </div>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Capacity Factor</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {(results.capacity_factor * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Optimal Locations (Greenfield Results) */}
        {results.optimal_locations && results.optimal_locations.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <span className="text-green-500">📍</span>
              Recommended Project Locations
              <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">
                {results.optimal_locations.length} sites
              </span>
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {results.optimal_locations.map((location, index) => (
                <div
                  key={index}
                  className="p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">
                        {location.type === 'solar' ? '🌞' : location.type === 'wind' ? '🌬️' : '🔋'}
                      </span>
                      <div className="font-medium text-gray-900 dark:text-white capitalize">
                        {location.type} Project
                      </div>
                    </div>
                    <div className="text-sm font-bold text-green-600 dark:text-green-400">
                      {location.capacity_mw.toFixed(0)} MW
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Capacity Factor:</span>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {location.capacity_factor ? `${(location.capacity_factor * 100).toFixed(0)}%` : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">LCOE:</span>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {location.lcoe ? `$${location.lcoe.toFixed(2)}/MWh` : 'N/A'}
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 italic">
                    {location.rationale}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Transmission Upgrades */}
        {results.transmission_upgrades && results.transmission_upgrades.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
              <span className="text-emerald-500">⚡</span>
              Recommended Transmission Upgrades
              <span className="text-xs bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded-full">
                {results.transmission_upgrades.length} corridors
              </span>
            </h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {results.transmission_upgrades.map((upgrade, index) => (
                <div
                  key={index}
                  className="p-3 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800"
                >
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">
                      {upgrade.from_node} → {upgrade.to_node}
                    </div>
                    <div className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
                      +{upgrade.capacity_add_mw.toFixed(0)} MW
                    </div>
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Est. Cost: ${(upgrade.estimated_cost / 1e6).toFixed(0)}M
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 italic">
                    {upgrade.rationale}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Project Configurations (for evaluate mode) */}
        {results.optimal_configurations && results.optimal_configurations.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
              Optimal Project Configurations
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {results.optimal_configurations.map((config, index) => (
                <div
                  key={config.project_id}
                  className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium text-gray-900 dark:text-white">
                      Project {index + 1}
                    </div>
                    <div className="text-sm font-semibold text-primary-600 dark:text-primary-400">
                      {config.recommended_capacity_mw.toFixed(0)} MW
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Generation:</span>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {(config.annual_generation_mwh / 1000).toFixed(0)}k MWh/yr
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">CF:</span>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {(config.capacity_factor * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">NPV:</span>
                      <div className="font-medium text-gray-900 dark:text-white">
                        ${(config.npv / 1000000).toFixed(1)}M
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
            Export Results
          </button>
          <button className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            Save Scenario
          </button>
        </div>
      </div>
    </div>
  );
};
