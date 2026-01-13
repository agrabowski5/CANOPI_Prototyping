import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { fetchJobStatus } from '../../store/optimizationSlice';

export const ProgressIndicator: React.FC = () => {
  const dispatch = useAppDispatch();
  const { currentJob, isRunning } = useAppSelector((state) => state.optimization);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Poll for job status when running
  useEffect(() => {
    if (!isRunning || !currentJob) return;

    const pollInterval = setInterval(() => {
      dispatch(fetchJobStatus(currentJob.id));
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [isRunning, currentJob, dispatch]);

  // Track elapsed time
  useEffect(() => {
    if (!isRunning) {
      setElapsedTime(0);
      return;
    }

    const startTime = Date.now();
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [isRunning]);

  if (!isRunning || !currentJob) return null;

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-sm">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="p-4">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <span className="font-semibold text-gray-900 dark:text-white">
                Optimizing...
              </span>
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {formatTime(elapsedTime)}
            </span>
          </div>

          {/* Job Name */}
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {currentJob.name}
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-700 dark:text-gray-300">Progress</span>
              <span className="font-semibold text-primary-600 dark:text-primary-400">
                {currentJob.progress_percentage?.toFixed(0) || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-primary-600 to-secondary-600 h-3 rounded-full transition-all duration-500 relative overflow-hidden"
                style={{ width: `${currentJob.progress_percentage || 0}%` }}
              >
                {/* Animated shine effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
              </div>
            </div>
          </div>

          {/* Status Message */}
          {currentJob.status === 'running' && (
            <div className="mt-3 flex items-center space-x-2 text-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-secondary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-secondary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-secondary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-gray-600 dark:text-gray-400">
                Running optimization engine
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
