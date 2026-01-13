import React from 'react';
import { Project, ProjectType } from '../../types';

interface ProjectCardProps {
  project: Project;
  onSelect: () => void;
  onDelete: () => void;
}

const getProjectIcon = (type: ProjectType): string => {
  switch (type) {
    case ProjectType.SOLAR:
      return '☀️';
    case ProjectType.WIND:
      return '💨';
    case ProjectType.STORAGE:
      return '⚡';
    case ProjectType.DATACENTER:
      return '🏢';
    default:
      return '📍';
  }
};

const getProjectColor = (type: ProjectType): string => {
  switch (type) {
    case ProjectType.SOLAR:
      return 'border-accent-500 bg-accent-50 dark:bg-accent-900/20';
    case ProjectType.WIND:
      return 'border-secondary-500 bg-secondary-50 dark:bg-secondary-900/20';
    case ProjectType.STORAGE:
      return 'border-purple-500 bg-purple-50 dark:bg-purple-900/20';
    case ProjectType.DATACENTER:
      return 'border-primary-500 bg-primary-50 dark:bg-primary-900/20';
    default:
      return 'border-gray-500 bg-gray-50 dark:bg-gray-900/20';
  }
};

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, onSelect, onDelete }) => {
  return (
    <div
      onClick={onSelect}
      className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-lg ${getProjectColor(
        project.type
      )}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getProjectIcon(project.type)}</span>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{project.name}</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400 capitalize">{project.type}</p>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="text-gray-400 hover:text-red-600 transition-colors"
          title="Delete project"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>

      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600 dark:text-gray-400">Capacity:</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {project.capacity_mw} MW
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600 dark:text-gray-400">Location:</span>
          <span className="font-mono text-xs text-gray-900 dark:text-white">
            {project.coordinates.latitude.toFixed(2)}, {project.coordinates.longitude.toFixed(2)}
          </span>
        </div>
        {project.status && (
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Status:</span>
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                project.status === 'active'
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : project.status === 'optimized'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'
              }`}
            >
              {project.status}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
