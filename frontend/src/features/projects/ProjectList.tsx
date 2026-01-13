import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { fetchProjects, setSelectedProject, deleteProject } from '../../store/projectsSlice';
import { ProjectCard } from './ProjectCard';
import { ProjectForm } from './ProjectForm';
import { ProjectType } from '../../types';

export const ProjectList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { projects, isLoading, error } = useAppSelector((state) => state.projects);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filterType, setFilterType] = useState<ProjectType | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    dispatch(fetchProjects());
  }, [dispatch]);

  const filteredProjects = (projects || []).filter((project) => {
    const matchesType = filterType === 'all' || project.type === filterType;
    const matchesSearch =
      searchQuery === '' ||
      project.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const handleDeleteProject = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      await dispatch(deleteProject(id));
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Projects</h2>
          <button
            onClick={() => setIsFormOpen(true)}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center space-x-2"
          >
            <span>+</span>
            <span>New Project</span>
          </button>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        />

        {/* Filter */}
        <div className="flex space-x-2 mt-3 overflow-x-auto pb-2">
          {['all', 'solar', 'wind', 'storage', 'datacenter'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type as ProjectType | 'all')}
              className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                filterType === type
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Project List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200">
            {error}
          </div>
        )}

        {!isLoading && !error && filteredProjects.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            {(projects || []).length === 0 ? (
              <div>
                <p className="mb-2">No projects yet</p>
                <p className="text-sm">Click "New Project" to get started</p>
              </div>
            ) : (
              <p>No projects match your filters</p>
            )}
          </div>
        )}

        {!isLoading &&
          !error &&
          filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onSelect={() => dispatch(setSelectedProject(project))}
              onDelete={() => handleDeleteProject(project.id)}
            />
          ))}
      </div>

      {/* Stats */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-primary-600">
              {filteredProjects.length}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Projects</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-secondary-600">
              {filteredProjects.reduce((sum, p) => sum + p.capacity_mw, 0).toFixed(0)}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Total MW</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-accent-600">
              {new Set(filteredProjects.map((p) => p.type)).size}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Types</div>
          </div>
        </div>
      </div>

      {/* Project Form Modal */}
      {isFormOpen && (
        <ProjectForm onClose={() => setIsFormOpen(false)} />
      )}
    </div>
  );
};
