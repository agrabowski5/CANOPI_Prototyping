# Frontend Setup Guide

This guide will help you get the CANOPI frontend up and running.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install all required packages:
- React 18.2
- TypeScript 5.3
- Redux Toolkit 2.0
- Mapbox GL JS 3.1
- Tailwind CSS 3.4
- Axios 1.6
- React Router 6.21

### 2. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Mapbox token:
```env
REACT_APP_MAPBOX_TOKEN=your_actual_mapbox_token_here
REACT_APP_API_BASE_URL=http://localhost:8000
```

**Getting a Mapbox Token:**
1. Go to https://www.mapbox.com/
2. Sign up for a free account
3. Go to Account > Access Tokens
4. Create a new token with these scopes:
   - styles:read
   - tiles:read
5. Copy the token to your `.env` file

### 3. Start Development Server

```bash
npm start
```

The app will open at http://localhost:3000

### 4. Verify Backend Connection

Make sure the backend API is running:
```bash
# In a separate terminal, from the project root:
cd backend
uvicorn app.main:app --reload
```

The backend should be accessible at http://localhost:8000

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template
│   └── manifest.json       # PWA manifest
│
├── src/
│   ├── features/           # Feature modules
│   │   ├── map/           # Map components
│   │   │   ├── MapView.tsx            # Main map component
│   │   │   ├── ProjectMarker.tsx      # Project markers
│   │   │   ├── GridTopologyLayer.tsx  # Grid visualization
│   │   │   └── LayerControls.tsx      # Layer toggle controls
│   │   │
│   │   ├── projects/      # Project management
│   │   │   ├── ProjectList.tsx        # Project list sidebar
│   │   │   ├── ProjectCard.tsx        # Individual project card
│   │   │   └── ProjectForm.tsx        # Create/edit form
│   │   │
│   │   └── optimization/  # Optimization features
│   │       ├── OptimizationPanel.tsx  # Control panel
│   │       ├── ResultsDashboard.tsx   # Results display
│   │       └── ProgressIndicator.tsx  # Progress tracking
│   │
│   ├── services/          # API services
│   │   ├── api.ts                     # Base API client
│   │   ├── projectsService.ts         # Projects API
│   │   ├── optimizationService.ts     # Optimization API
│   │   └── gridService.ts             # Grid data API
│   │
│   ├── store/             # Redux state management
│   │   ├── store.ts                   # Redux store config
│   │   ├── hooks.ts                   # Typed hooks
│   │   ├── projectsSlice.ts           # Projects state
│   │   ├── optimizationSlice.ts       # Optimization state
│   │   └── mapSlice.ts                # Map state
│   │
│   ├── types/             # TypeScript definitions
│   │   └── index.ts                   # All type definitions
│   │
│   ├── App.tsx            # Main app component
│   ├── index.tsx          # Entry point
│   ├── index.css          # Global styles
│   └── reportWebVitals.ts # Performance monitoring
│
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind CSS config
├── postcss.config.js      # PostCSS config
└── README.md              # Documentation
```

## Key Technologies

### React + TypeScript
- Functional components with hooks
- Strict TypeScript for type safety
- React 18 features (concurrent rendering, automatic batching)

### Redux Toolkit
- Centralized state management
- Redux DevTools integration
- Async thunks for API calls
- Slices: `projects`, `optimization`, `map`

### Mapbox GL JS
- Interactive mapping
- Custom markers and layers
- Drag-and-drop functionality
- GeoJSON support

### Tailwind CSS
- Utility-first styling
- Dark mode support
- Custom color palette
- Responsive design

## Development Workflow

### Adding a New Feature

1. **Create Types** (if needed)
   ```typescript
   // src/types/index.ts
   export interface NewFeature {
     id: string;
     name: string;
   }
   ```

2. **Create Service** (if API needed)
   ```typescript
   // src/services/newService.ts
   import { apiClient } from './api';

   export const newService = {
     async getData() {
       const response = await apiClient.get('/api/v1/new');
       return response.data;
     }
   };
   ```

3. **Create Redux Slice** (if state needed)
   ```typescript
   // src/store/newSlice.ts
   import { createSlice } from '@reduxjs/toolkit';

   const newSlice = createSlice({
     name: 'new',
     initialState: {},
     reducers: {}
   });
   ```

4. **Create Component**
   ```typescript
   // src/features/new/NewComponent.tsx
   import React from 'react';

   export const NewComponent: React.FC = () => {
     return <div>New Feature</div>;
   };
   ```

5. **Add to App**
   ```typescript
   // src/App.tsx
   import { NewComponent } from './features/new/NewComponent';
   ```

## Common Tasks

### Running Tests
```bash
npm test
```

### Building for Production
```bash
npm run build
```

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npx tsc --noEmit
```

## Troubleshooting

### Port 3000 Already in Use
```bash
# Kill process on port 3000
npx kill-port 3000

# Or specify different port
PORT=3001 npm start
```

### Module Not Found Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Mapbox Token Issues
- Ensure token is in `.env` file (not `.env.example`)
- Token must start with `pk.`
- Restart dev server after adding token
- Check token hasn't expired

### TypeScript Errors
```bash
# Clear TypeScript cache
rm -rf node_modules/.cache
npm start
```

### Hot Reload Not Working
```bash
# Create/edit .env.local
echo "FAST_REFRESH=true" > .env.local
```

## API Endpoints

The frontend expects these backend endpoints:

### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Optimization
- `POST /api/v1/optimization/jobs` - Create job
- `GET /api/v1/optimization/jobs/{id}` - Get job
- `GET /api/v1/optimization/jobs/{id}/status` - Get status
- `GET /api/v1/optimization/jobs/{id}/results` - Get results
- `POST /api/v1/optimization/quick` - Quick optimize

### Grid
- `GET /api/v1/grid/topology` - Get grid topology
- `GET /api/v1/grid/nodes` - Get network nodes
- `GET /api/v1/grid/lines` - Get transmission lines

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_MAPBOX_TOKEN` | Mapbox API token | Required |
| `REACT_APP_API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `REACT_APP_ENABLE_MOCK_DATA` | Use mock data | `true` |
| `REACT_APP_ENABLE_DARK_MODE` | Enable dark mode | `true` |

## Performance Tips

1. **Code Splitting**: Use React.lazy() for large components
2. **Memoization**: Use React.memo() for expensive renders
3. **Debouncing**: Debounce map interactions
4. **Virtual Lists**: Use virtual scrolling for long lists
5. **Image Optimization**: Compress and lazy-load images

## Browser DevTools

### Redux DevTools
- Install: https://github.com/reduxjs/redux-devtools
- View state changes in real-time
- Time-travel debugging

### React DevTools
- Install: https://react.dev/learn/react-developer-tools
- Inspect component tree
- Profile performance

## Next Steps

1. Add your Mapbox token
2. Start the backend server
3. Run `npm start`
4. Create your first project
5. Run an optimization
6. View results on the map

## Support

For issues or questions:
- Check the main README.md
- Review the API documentation
- Check browser console for errors
- Verify backend is running
