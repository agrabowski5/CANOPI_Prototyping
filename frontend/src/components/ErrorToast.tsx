import React, { useEffect, useState } from 'react';

interface ErrorMessage {
  id: string;
  message: string;
  details?: string;
  timestamp: Date;
}

// Global error store
const errorListeners: Set<(errors: ErrorMessage[]) => void> = new Set();
let errors: ErrorMessage[] = [];

export const reportError = (message: string, details?: string) => {
  const error: ErrorMessage = {
    id: Math.random().toString(36).substr(2, 9),
    message,
    details,
    timestamp: new Date(),
  };
  errors = [...errors, error];
  errorListeners.forEach((listener) => listener(errors));

  // Also log to console for debugging
  console.error(`[CANOPI Error] ${message}`, details || '');

  // Auto-remove after 10 seconds
  setTimeout(() => {
    dismissError(error.id);
  }, 10000);
};

export const dismissError = (id: string) => {
  errors = errors.filter((e) => e.id !== id);
  errorListeners.forEach((listener) => listener(errors));
};

// Hook to subscribe to errors
const useErrors = () => {
  const [currentErrors, setCurrentErrors] = useState<ErrorMessage[]>(errors);

  useEffect(() => {
    const listener = (newErrors: ErrorMessage[]) => setCurrentErrors(newErrors);
    errorListeners.add(listener);
    return () => {
      errorListeners.delete(listener);
    };
  }, []);

  return currentErrors;
};

export const ErrorToast: React.FC = () => {
  const currentErrors = useErrors();

  if (currentErrors.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-md">
      {currentErrors.map((error) => (
        <div
          key={error.id}
          className="bg-red-600 text-white p-4 rounded-lg shadow-lg animate-slide-in"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <p className="font-semibold">{error.message}</p>
              {error.details && (
                <p className="text-sm text-red-200 mt-1">{error.details}</p>
              )}
              <p className="text-xs text-red-300 mt-2">
                {error.timestamp.toLocaleTimeString()}
              </p>
            </div>
            <button
              onClick={() => dismissError(error.id)}
              className="ml-4 text-red-200 hover:text-white"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
