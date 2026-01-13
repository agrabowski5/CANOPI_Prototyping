# Frontend Architecture

## Overview

The CANOPI frontend is a modern single-page application (SPA) built with React and TypeScript. It follows a feature-based architecture with clear separation of concerns.

## Architecture Principles

1. **Feature-Based Organization**: Code organized by feature, not by type
2. **Unidirectional Data Flow**: Redux for predictable state management
3. **Type Safety**: Full TypeScript coverage with strict mode
4. **Separation of Concerns**: Clear boundaries between UI, state, and services
5. **Component Composition**: Small, reusable components
6. **Performance First**: Code splitting, memoization, and lazy loading

## Technology Stack

### Core
- **React 18.2**: UI library with concurrent features
- **TypeScript 5.3**: Type-safe JavaScript
- **Redux Toolkit**: State management with minimal boilerplate

### UI & Styling
- **Tailwind CSS 3.4**: Utility-first styling
- **Mapbox GL JS 3.1**: Interactive maps
- **Custom CSS**: Animations and special effects

### Routing & Navigation
- **React Router 6**: Client-side routing

### API Communication
- **Axios**: HTTP client with interceptors

### Build Tools
- **React Scripts**: Build configuration
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixes

## Directory Structure

```
src/
├── features/           # Feature modules (UI + logic)
├── services/           # API communication
├── store/              # Redux state management
├── types/              # TypeScript definitions
├── utils/              # Utility functions (future)
├── hooks/              # Custom React hooks (future)
└── components/         # Shared components (future)
```

## Data Flow

```
User Action
    ↓
Component Event Handler
    ↓
Redux Action/Thunk
    ↓
API Service Call
    ↓
Backend API
    ↓
Redux State Update
    ↓
Component Re-render
```

## State Management

### Redux Store Structure

```typescript
{
  projects: {
    projects: Project[],
    selectedProject: Project | null,
    isLoading: boolean,
    error: string | null,
    total: number
  },
  optimization: {
    jobs: OptimizationJob[],
    currentJob: OptimizationJob | null,
    results: OptimizationResults | null,
    isRunning: boolean,
    isLoading: boolean,
    error: string | null
  },
  map: {
    viewState: MapViewState,
    layers: MapLayers,
    mapInstance: mapboxgl.Map | null,
    isMapLoaded: boolean,
    hoveredFeature: string | null,
    selectedFeature: string | null
  }
}
```

### State Management Patterns

1. **Async Actions**: Use `createAsyncThunk` for API calls
2. **Optimistic Updates**: Update UI immediately, revert on error
3. **Normalized State**: Keep data flat to avoid nested updates
4. **Derived State**: Compute in selectors, not in state
5. **Middleware**: Use for side effects (logging, analytics)

## Component Architecture

### Component Types

1. **Feature Components**: Business logic + UI
   - Example: `ProjectList`, `OptimizationPanel`
   - Connected to Redux
   - Handle user interactions

2. **Presentational Components**: Pure UI
   - Example: `ProjectCard`, `LayerControls`
   - Receive props, emit events
   - No Redux connection

3. **Container Components**: Logic only
   - Wrap presentational components
   - Connect to Redux
   - Handle data fetching

### Component Patterns

```typescript
// Feature Component
export const ProjectList: React.FC = () => {
  const dispatch = useAppDispatch();
  const projects = useAppSelector(state => state.projects.projects);

  useEffect(() => {
    dispatch(fetchProjects());
  }, []);

  return <div>{/* UI */}</div>;
};

// Presentational Component
interface ProjectCardProps {
  project: Project;
  onSelect: () => void;
  onDelete: () => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onSelect,
  onDelete
}) => {
  return <div>{/* UI */}</div>;
};
```

## API Service Layer

### Service Structure

```typescript
export const projectsService = {
  async getProjects(params) {
    const response = await apiClient.get('/api/v1/projects/', { params });
    return response.data;
  },

  async createProject(data) {
    const response = await apiClient.post('/api/v1/projects/', data);
    return response.data;
  },

  // ... other methods
};
```

### Error Handling

```typescript
try {
  const data = await projectsService.getProjects();
  return data;
} catch (error) {
  // Error interceptor handles common errors
  // Service-specific errors handled here
  throw new Error(handleApiError(error));
}
```

### Request/Response Interceptors

```typescript
// Request Interceptor
apiClient.interceptors.request.use(config => {
  // Add auth token
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Handle 401, 403, 500, etc.
    return Promise.reject(error);
  }
);
```

## Map Integration

### Mapbox GL JS Architecture

```typescript
// Map initialization
const map = new mapboxgl.Map({
  container: mapContainerRef.current,
  style: 'mapbox://styles/mapbox/light-v11',
  center: [longitude, latitude],
  zoom: zoom
});

// Add layers
map.on('load', () => {
  map.addSource('projects', { /* ... */ });
  map.addLayer({ /* ... */ });
});

// Handle interactions
map.on('click', 'projects', (e) => {
  // Handle project click
});
```

### Custom Markers

```typescript
// Create marker element
const el = document.createElement('div');
el.className = 'project-marker';

// Create marker
const marker = new mapboxgl.Marker({
  element: el,
  draggable: true
});

// Handle events
marker.on('dragend', () => {
  const lngLat = marker.getLngLat();
  updateProjectCoordinates(lngLat);
});
```

## Styling Strategy

### Tailwind CSS

```typescript
// Utility classes
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">

// Responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

// State variants
<button className="hover:bg-primary-700 focus:ring-2 disabled:opacity-50">

// Dark mode
<div className="text-gray-900 dark:text-white">
```

### Custom CSS

```css
/* Animations */
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Custom components */
.btn-primary {
  @apply px-4 py-2 bg-primary-600 text-white rounded-lg;
}
```

## Performance Optimization

### Code Splitting

```typescript
// Route-based splitting
const OptimizationPanel = React.lazy(() =>
  import('./features/optimization/OptimizationPanel')
);

<Suspense fallback={<Loading />}>
  <OptimizationPanel />
</Suspense>
```

### Memoization

```typescript
// Memoize expensive components
export const ProjectCard = React.memo(({ project }) => {
  // Component code
});

// Memoize selectors
const selectFilteredProjects = createSelector(
  [state => state.projects.projects, state => state.filters],
  (projects, filters) => projects.filter(/* ... */)
);
```

### Debouncing

```typescript
const debouncedSearch = useCallback(
  debounce((query: string) => {
    dispatch(searchProjects(query));
  }, 300),
  []
);
```

## Type System

### Type Definitions

```typescript
// Entity types
export interface Project {
  id: string;
  name: string;
  type: ProjectType;
  coordinates: Coordinates;
  capacity_mw: number;
}

// Enum types
export enum ProjectType {
  SOLAR = 'solar',
  WIND = 'wind',
  STORAGE = 'storage',
  DATACENTER = 'datacenter'
}

// Form types
export interface ProjectFormData {
  name: string;
  type: ProjectType;
  latitude: number;
  longitude: number;
  capacity_mw: number;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}
```

### Type Guards

```typescript
function isProject(obj: any): obj is Project {
  return (
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    isProjectType(obj.type)
  );
}
```

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock Redux store and API calls
- Test utility functions

### Integration Tests
- Test feature workflows
- Test Redux state management
- Test API service calls

### E2E Tests
- Test critical user flows
- Test optimization workflow
- Test map interactions

## Security Considerations

1. **API Token Storage**: Store in environment variables
2. **Authentication**: JWT tokens in localStorage
3. **XSS Prevention**: React escapes by default
4. **CSRF Protection**: Backend CSRF tokens
5. **Input Validation**: Validate all user inputs
6. **HTTPS**: Enforce HTTPS in production

## Accessibility

1. **Keyboard Navigation**: All interactive elements keyboard-accessible
2. **ARIA Labels**: Proper ARIA labels and roles
3. **Focus Management**: Visible focus indicators
4. **Screen Readers**: Semantic HTML and ARIA
5. **Color Contrast**: WCAG 2.1 AA compliance

## Future Enhancements

### Planned Features
- [ ] Offline support with service workers
- [ ] Real-time collaboration with WebSockets
- [ ] Advanced analytics dashboard
- [ ] Export to PDF/Excel
- [ ] Scenario comparison
- [ ] 3D visualization mode
- [ ] Mobile app (React Native)

### Performance Improvements
- [ ] Virtual scrolling for large lists
- [ ] Web Workers for heavy computations
- [ ] GraphQL for efficient data fetching
- [ ] CDN for static assets
- [ ] Progressive Web App (PWA)

### Developer Experience
- [ ] Storybook for component documentation
- [ ] Chromatic for visual testing
- [ ] Husky for pre-commit hooks
- [ ] Conventional commits
- [ ] Automated releases

## Best Practices

### Code Style
- Use TypeScript strict mode
- Follow ESLint rules
- Use Prettier for formatting
- Write self-documenting code
- Add JSDoc comments for complex logic

### Component Design
- Keep components small and focused
- Use composition over inheritance
- Prefer functional components
- Use custom hooks for reusable logic
- Avoid prop drilling (use context/Redux)

### State Management
- Keep state minimal and derived
- Use Redux for global state
- Use useState for local state
- Avoid unnecessary re-renders
- Use selectors for computed values

### Performance
- Lazy load routes and components
- Memoize expensive computations
- Debounce/throttle event handlers
- Optimize images and assets
- Monitor bundle size

## Conclusion

This architecture provides a solid foundation for building a scalable, maintainable, and performant energy planning platform. The modular design allows for easy extension and modification as requirements evolve.
