# Quick Start Guide

Get the CANOPI frontend running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Mapbox account (free tier is fine)
- Backend running on port 8000

## Installation Steps

### 1. Install Dependencies (2 min)

```bash
cd frontend
npm install
```

### 2. Configure Mapbox (1 min)

Get your Mapbox token:
1. Go to https://account.mapbox.com/access-tokens/
2. Copy your default public token (starts with `pk.`)

Create `.env` file:
```bash
echo "REACT_APP_MAPBOX_TOKEN=YOUR_TOKEN_HERE" > .env
echo "REACT_APP_API_BASE_URL=http://localhost:8000" >> .env
```

Replace `YOUR_TOKEN_HERE` with your actual token.

### 3. Start the App (1 min)

```bash
npm start
```

The app opens automatically at http://localhost:3000

## First Steps

### Create Your First Project

1. **Click anywhere on the map** - A form appears
2. **Fill in the details**:
   - Name: "Solar Farm 1"
   - Type: Solar
   - Capacity: 100 MW
3. **Click "Create Project"**

Your project appears as a marker on the map!

### Run an Optimization

1. **Select projects** in the left sidebar (click checkboxes)
2. **Click "Run Quick Optimization"** in the right panel
3. **Watch the progress** indicator in bottom-right
4. **View results** in the right panel when complete

### Explore the Map

- **Drag markers** to move projects
- **Toggle layers** using the map controls (top-left)
- **Zoom/pan** with mouse or keyboard
- **Click markers** to see project details

## Features at a Glance

### Left Sidebar - Projects
- View all projects
- Search and filter
- Create new projects
- Delete projects
- See project stats

### Center - Map
- Interactive Mapbox map
- Draggable project markers
- Grid topology visualization
- Layer controls
- Click to add projects

### Right Sidebar - Optimization
- Select projects to optimize
- Configure settings
- Run optimization
- View results
- Export data

## Keyboard Shortcuts

- **Click map**: Add new project
- **Drag marker**: Move project
- **Escape**: Close modals
- **Tab**: Navigate between fields
- **Enter**: Submit forms

## Troubleshooting

### Mapbox not loading?
- Check your token in `.env`
- Restart the dev server: `Ctrl+C` then `npm start`

### Can't connect to API?
- Make sure backend is running: `cd backend && uvicorn app.main:app --reload`
- Check backend is on port 8000

### Port 3000 already in use?
```bash
npx kill-port 3000
npm start
```

## What's Next?

1. Read [README.md](./README.md) for full documentation
2. Check [SETUP.md](./SETUP.md) for detailed setup
3. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details

## Support

- Backend API docs: http://localhost:8000/docs
- Mapbox docs: https://docs.mapbox.com/
- React docs: https://react.dev/

## Development Tips

### Hot Reload
Changes to code automatically reload the page. No restart needed!

### Debug Mode
Open browser DevTools (F12) to see:
- Console logs
- Network requests
- Redux state (with Redux DevTools extension)
- React components (with React DevTools extension)

### Dark Mode
Toggle dark mode using the icon in the top-right header.

### Mock Data
If backend is not available, the app uses mock data (configurable in `.env`).

## Common Tasks

### Add a new project type
1. Update `ProjectType` enum in `src/types/index.ts`
2. Add icon in `getProjectIcon()` functions
3. Add color in `getProjectColor()` functions

### Change map style
In `src/features/map/MapView.tsx`, change the style URL:
```typescript
style: 'mapbox://styles/mapbox/satellite-v12'  // Satellite
style: 'mapbox://styles/mapbox/dark-v11'       // Dark
style: 'mapbox://styles/mapbox/outdoors-v12'   // Outdoors
```

### Modify API endpoints
Edit `src/services/api.ts` to change the base URL:
```typescript
const API_BASE_URL = 'https://your-api.com';
```

## Production Build

```bash
npm run build
```

Creates optimized production build in `build/` directory.

Serve it:
```bash
npx serve -s build
```

## Happy Coding!

You're all set! Start building amazing energy infrastructure plans with CANOPI.
