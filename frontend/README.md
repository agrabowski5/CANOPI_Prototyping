# CANOPI Energy Planning Platform - Frontend

A modern, interactive web application for renewable energy infrastructure planning and optimization built with React, TypeScript, and Mapbox GL JS.

## Features

### Interactive Map Interface
- **Mapbox GL JS Integration**: High-performance, interactive map centered on Western US
- **Project Markers**: Draggable pins with project type icons (solar, wind, storage, datacenter)
- **Grid Topology**: Visualize transmission lines and substations
- **Layer Controls**: Toggle different map layers (projects, grid, terrain, satellite)

### Project Management
- **Create/Edit/Delete Projects**: Full CRUD operations for energy projects
- **Project Types**: Solar, Wind, Storage, and Data Center support
- **Drag-and-Drop**: Reposition projects by dragging markers on map
- **Project Details**: View capacity, location, costs, and status

### Optimization Engine
- **Quick Optimization**: One-click optimization with default settings
- **Advanced Configuration**: Customize objectives, constraints, and time horizons
- **Real-time Progress**: Live progress tracking with percentage completion
- **Results Dashboard**: Comprehensive visualization of optimization results

### User Experience
- **Dark Mode**: Full dark mode support with system preference detection
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Loading States**: Smooth loading indicators and error handling
- **Accessibility**: WCAG 2.1 AA compliant

## Tech Stack

- **React 18.2** - UI framework
- **TypeScript 5.3** - Type safety
- **Redux Toolkit** - State management
- **React Router** - Navigation
- **Mapbox GL JS 3.1** - Mapping
- **Tailwind CSS 3.4** - Styling
- **Axios** - API client

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Mapbox API token (get one at https://www.mapbox.com/)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Add your Mapbox token to `.env`:
```
REACT_APP_MAPBOX_TOKEN=your_token_here
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm start
```

The app will open at http://localhost:3000

### Build

Create production build:
```bash
npm run build
```

### Testing

Run tests:
```bash
npm test
```

## Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── features/        # Feature modules
│   │   ├── map/        # Map components
│   │   ├── projects/   # Project management
│   │   └── optimization/ # Optimization features
│   ├── services/        # API services
│   ├── store/           # Redux store
│   ├── types/           # TypeScript types
│   ├── App.tsx          # Main app component
│   ├── index.tsx        # Entry point
│   └── index.css        # Global styles
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

## Key Features Implementation

### Adding Projects
1. Click anywhere on the map to open project form
2. Fill in project details (name, type, capacity, costs)
3. Project appears as marker on map
4. Drag marker to reposition

### Running Optimization
1. Select projects from left sidebar
2. Click "Run Quick Optimization" for default settings
3. Or expand "Advanced Settings" for custom configuration
4. View progress in bottom-right indicator
5. See results in right sidebar when complete

### Map Layers
- **Projects**: Show/hide project markers
- **Grid Network**: Display transmission infrastructure
- **Transmission Lines**: Color-coded by voltage and status
- **Substations**: Sized by voltage rating
- **Terrain**: 3D terrain visualization
- **Satellite**: Satellite imagery basemap

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` (configurable via `REACT_APP_API_BASE_URL`).

### API Endpoints Used
- `GET /api/v1/projects/` - Fetch all projects
- `POST /api/v1/projects/` - Create project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project
- `POST /api/v1/optimization/jobs` - Create optimization job
- `GET /api/v1/optimization/jobs/{id}/status` - Get job status
- `GET /api/v1/optimization/jobs/{id}/results` - Get results
- `GET /api/v1/grid/topology` - Get grid topology

## Styling

### Color Palette
- **Primary (Deep Blue)**: `#1E40AF` - Main actions, headers
- **Secondary (Electric Teal)**: `#06B6D4` - Accents, highlights
- **Accent (Solar Yellow)**: `#F59E0B` - Solar projects, warnings

### Project Type Colors
- Solar: Solar Yellow (#F59E0B)
- Wind: Electric Teal (#06B6D4)
- Storage: Purple (#8B5CF6)
- Data Center: Deep Blue (#1E40AF)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting with React.lazy
- Memoized components with React.memo
- Optimized Redux selectors
- Debounced map interactions
- Lazy loading for large datasets

## Accessibility

- Keyboard navigation support
- ARIA labels and roles
- Focus indicators
- Screen reader friendly
- Color contrast compliance

## Troubleshooting

### Mapbox not loading
- Check that `REACT_APP_MAPBOX_TOKEN` is set correctly
- Verify token has proper scopes (styles:read, tiles:read)

### API connection issues
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `REACT_APP_API_BASE_URL` is correct

### Build errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear build cache: `rm -rf build`

## Contributing

1. Follow TypeScript strict mode guidelines
2. Use ESLint and Prettier for code formatting
3. Write tests for new features
4. Update documentation

## License

Copyright 2026 CANOPI Energy Planning Platform
