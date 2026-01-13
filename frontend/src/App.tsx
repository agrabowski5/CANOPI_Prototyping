import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MapView } from './features/map/MapView';
import { ProjectList } from './features/projects/ProjectList';
import { ProjectForm } from './features/projects/ProjectForm';
import { OptimizationPanel } from './features/optimization/OptimizationPanel';
import { ResultsDashboard } from './features/optimization/ResultsDashboard';
import { ProgressIndicator } from './features/optimization/ProgressIndicator';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ErrorToast } from './components/ErrorToast';
import { useAppDispatch } from './store/hooks';
import { fetchProjects } from './store/projectsSlice';

function App() {
  const dispatch = useAppDispatch();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [clickCoordinates, setClickCoordinates] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

  // Load projects on mount
  useEffect(() => {
    dispatch(fetchProjects());
  }, [dispatch]);

  // Handle dark mode
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Listen for map clicks to add projects
  useEffect(() => {
    const handleMapClick = (e: any) => {
      const { longitude, latitude } = e.detail;
      setClickCoordinates({ longitude, latitude });
      setShowProjectForm(true);
    };

    window.addEventListener('mapClick', handleMapClick);
    return () => window.removeEventListener('mapClick', handleMapClick);
  }, []);

  return (
    <ErrorBoundary>
    <Router>
      <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm z-20">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🌿</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  CANOPI
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Energy Planning Platform
                </p>
              </div>
            </div>

            <nav className="flex items-center space-x-6">
              <a
                href="/"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                Dashboard
              </a>
              <a
                href="#"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                Scenarios
              </a>
              <a
                href="#"
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                Reports
              </a>

              {/* Dark Mode Toggle */}
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title={isDarkMode ? 'Light Mode' : 'Dark Mode'}
              >
                {isDarkMode ? (
                  <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>

              <div className="flex items-center space-x-2 pl-4 border-l border-gray-300 dark:border-gray-600">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
                  U
                </div>
              </div>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar - Projects */}
          <div className="w-80 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex flex-col overflow-hidden">
            <ProjectList />
          </div>

          {/* Center - Map */}
          <div className="flex-1 relative">
            <Routes>
              <Route path="/" element={<MapView />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>

          {/* Right Sidebar - Optimization & Results */}
          <div className="w-96 border-l border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <OptimizationPanel />
              <ResultsDashboard />
            </div>
          </div>
        </div>

        {/* Floating Components */}
        <ProgressIndicator />
        <ErrorToast />

        {/* Project Form Modal */}
        {showProjectForm && (
          <ProjectForm
            onClose={() => {
              setShowProjectForm(false);
              setClickCoordinates(null);
            }}
            initialCoordinates={clickCoordinates || undefined}
          />
        )}
      </div>
    </Router>
    </ErrorBoundary>
  );
}

export default App;
