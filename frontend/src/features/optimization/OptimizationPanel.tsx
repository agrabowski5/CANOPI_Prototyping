import React, { useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { createOptimizationJob, runQuickOptimization, runGreenfieldOptimization } from '../../store/optimizationSlice';
import { OptimizationFormData } from '../../types';

export const OptimizationPanel: React.FC = () => {
  const dispatch = useAppDispatch();
  const projects = useAppSelector((state) => state.projects.projects);
  const { isRunning, currentJob, isLoading } = useAppSelector((state) => state.optimization);
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [formData, setFormData] = useState<OptimizationFormData>({
    name: 'Optimization Run',
    objective: 'minimize_cost',
    time_horizon_years: 25,
    discount_rate: 0.07,
  });

  const handleQuickOptimize = async () => {
    if (selectedProjects.length === 0) {
      alert('Please select at least one project');
      return;
    }
    await dispatch(runQuickOptimization(selectedProjects));
  };

  const handleGreenfieldOptimize = async () => {
    await dispatch(runGreenfieldOptimization());
  };

  const handleAdvancedOptimize = async () => {
    if (selectedProjects.length === 0) {
      alert('Please select at least one project');
      return;
    }

    await dispatch(
      createOptimizationJob({
        name: formData.name,
        config: {
          objective: formData.objective,
          constraints: {
            max_budget: formData.max_budget,
            min_renewable_percentage: formData.min_renewable_percentage,
          },
          time_horizon_years: formData.time_horizon_years,
          discount_rate: formData.discount_rate,
        },
        project_ids: selectedProjects,
      })
    );
  };

  const toggleProjectSelection = (projectId: string) => {
    setSelectedProjects((prev) =>
      prev.includes(projectId)
        ? prev.filter((id) => id !== projectId)
        : [...prev, projectId]
    );
  };

  const selectAllProjects = () => {
    setSelectedProjects(projects.map((p) => p.id));
  };

  const clearSelection = () => {
    setSelectedProjects([]);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-primary-600 to-secondary-600">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <span>🎯</span>
            <span>Optimization</span>
          </h2>
          {isRunning && currentJob && (
            <span className="px-3 py-1 bg-white/20 text-white text-sm rounded-full flex items-center space-x-2">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
              <span>Running</span>
            </span>
          )}
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Greenfield Optimization - Find Best Locations */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
          <h3 className="font-semibold text-green-700 dark:text-green-400 mb-2 flex items-center gap-2">
            <span>🌍</span>
            Find Optimal Locations
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            Let CANOPI analyze the grid and recommend the best locations for new renewable projects.
          </p>
          <button
            onClick={handleGreenfieldOptimize}
            disabled={isRunning || isLoading}
            className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-semibold rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <span>🔍</span>
            <span>Run Greenfield Optimization</span>
          </button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200 dark:border-gray-700"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">or evaluate specific sites</span>
          </div>
        </div>

        {/* Project Selection */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Select Projects to Evaluate
            </label>
            <div className="flex space-x-2 text-xs">
              <button
                onClick={selectAllProjects}
                className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
              >
                Select All
              </button>
              <span className="text-gray-400">|</span>
              <button
                onClick={clearSelection}
                className="text-gray-600 hover:text-gray-700 dark:text-gray-400"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="max-h-48 overflow-y-auto space-y-2 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
            {(projects || []).length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
                No projects available. Create projects first.
              </p>
            ) : (
              (projects || []).map((project) => (
                <label
                  key={project.id}
                  className="flex items-center space-x-3 cursor-pointer hover:bg-white dark:hover:bg-gray-800 p-2 rounded transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedProjects.includes(project.id)}
                    onChange={() => toggleProjectSelection(project.id)}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {project.name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {project.type} - {project.capacity_mw} MW
                    </div>
                  </div>
                </label>
              ))
            )}
          </div>

          <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
            {selectedProjects.length} of {(projects || []).length} selected
          </div>
        </div>

        {/* Quick Optimize Button */}
        <button
          onClick={handleQuickOptimize}
          disabled={isRunning || isLoading || selectedProjects.length === 0}
          className="w-full py-3 bg-gradient-to-r from-primary-600 to-secondary-600 text-white font-semibold rounded-lg hover:from-primary-700 hover:to-secondary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          <span>🚀</span>
          <span>Run Quick Optimization</span>
        </button>

        {/* Advanced Settings Toggle */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full py-2 text-sm text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded transition-colors flex items-center justify-center space-x-2"
        >
          <span>{isExpanded ? 'Hide' : 'Show'} Advanced Settings</span>
          <svg
            className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Advanced Settings */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Optimization Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Objective
              </label>
              <select
                value={formData.objective}
                onChange={(e) => setFormData({ ...formData, objective: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="minimize_cost">Minimize Cost</option>
                <option value="maximize_renewable">Maximize Renewable %</option>
                <option value="minimize_emissions">Minimize Emissions</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Time Horizon (years)
                </label>
                <input
                  type="number"
                  value={formData.time_horizon_years}
                  onChange={(e) =>
                    setFormData({ ...formData, time_horizon_years: parseInt(e.target.value) })
                  }
                  min="1"
                  max="50"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Discount Rate
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.discount_rate}
                  onChange={(e) =>
                    setFormData({ ...formData, discount_rate: parseFloat(e.target.value) })
                  }
                  min="0"
                  max="1"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Budget ($M)
              </label>
              <input
                type="number"
                step="1"
                value={formData.max_budget || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    max_budget: e.target.value ? parseFloat(e.target.value) : undefined,
                  })
                }
                placeholder="No limit"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Min Renewable % (0-100)
              </label>
              <input
                type="number"
                step="1"
                value={formData.min_renewable_percentage || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    min_renewable_percentage: e.target.value
                      ? parseFloat(e.target.value)
                      : undefined,
                  })
                }
                min="0"
                max="100"
                placeholder="No minimum"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <button
              onClick={handleAdvancedOptimize}
              disabled={isRunning || isLoading || selectedProjects.length === 0}
              className="w-full py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Run Advanced Optimization
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
