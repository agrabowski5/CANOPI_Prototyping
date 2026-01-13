import { configureStore } from '@reduxjs/toolkit';
import projectsReducer from './projectsSlice';
import optimizationReducer from './optimizationSlice';
import mapReducer from './mapSlice';

export const store = configureStore({
  reducer: {
    projects: projectsReducer,
    optimization: optimizationReducer,
    map: mapReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['map/setMapInstance'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['payload.mapInstance'],
        // Ignore these paths in the state
        ignoredPaths: ['map.mapInstance'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
