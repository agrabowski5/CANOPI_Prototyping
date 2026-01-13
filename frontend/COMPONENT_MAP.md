# Component Architecture Map

Visual guide to the CANOPI frontend component structure and data flow.

## Application Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                          App.tsx (Root)                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                        Header                                  │  │
│  │  [Logo] CANOPI    [Nav: Dashboard, Scenarios, Reports] [Dark] │  │
│  └───────────────────────────────────────────────────────────────┘  │
│  ┌──────────────┬─────────────────────────────┬──────────────────┐  │
│  │              │                             │                  │  │
│  │  Left Panel  │       Center - Map          │   Right Panel    │  │
│  │  (320px)     │         (Flex)              │     (384px)      │  │
│  │              │                             │                  │  │
│  │  ┌────────┐  │  ┌───────────────────────┐  │  ┌────────────┐ │  │
│  │  │Project │  │  │                       │  │  │Optimization│ │  │
│  │  │  List  │  │  │      MapView          │  │  │   Panel    │ │  │
│  │  │        │  │  │                       │  │  │            │ │  │
│  │  │ ☀️ Sol │  │  │  🗺️ Mapbox GL JS     │  │  │ [Projects] │ │  │
│  │  │ 💨 Win │  │  │                       │  │  │ ☑️ Proj 1  │ │  │
│  │  │ ⚡ Sto │  │  │  • Project Markers    │  │  │ ☑️ Proj 2  │ │  │
│  │  │ 🏢 Dat │  │  │  • Grid Topology      │  │  │            │ │  │
│  │  │        │  │  │  • Layer Controls     │  │  │ [Settings] │ │  │
│  │  │ [+New] │  │  │                       │  │  │ [Run Opt]  │ │  │
│  │  │        │  │  │                       │  │  └────────────┘ │  │
│  │  │[Search]│  │  │                       │  │  ┌────────────┐ │  │
│  │  │[Filter]│  │  │                       │  │  │  Results   │ │  │
│  │  │        │  │  │                       │  │  │ Dashboard  │ │  │
│  │  │ Stats  │  │  │                       │  │  │            │ │  │
│  │  │ 12 Proj│  │  │                       │  │  │ 💰 Cost    │ │  │
│  │  │ 500 MW │  │  │                       │  │  │ ⚡ Cap     │ │  │
│  │  └────────┘  │  └───────────────────────┘  │  │ 🌱 Renew   │ │  │
│  │              │                             │  └────────────┘ │  │
│  └──────────────┴─────────────────────────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ (Floating)
         ▼
  ┌──────────────┐
  │  Progress    │
  │  Indicator   │
  │  🔄 85%      │
  └──────────────┘
```

## Component Hierarchy

```
App
├── Header (inline)
│   ├── Logo & Title
│   ├── Navigation Links
│   └── Dark Mode Toggle
│
├── Left Sidebar
│   └── ProjectList
│       ├── Search Input
│       ├── Filter Buttons
│       └── ProjectCard[] (mapped)
│           ├── Icon & Name
│           ├── Stats (capacity, location)
│           └── Delete Button
│
├── Center (Map)
│   └── Router
│       └── MapView
│           ├── Mapbox Map (ref)
│           ├── LayerControls (overlay)
│           │   └── Layer Toggles[]
│           ├── GridTopologyLayer
│           │   ├── Transmission Lines
│           │   └── Substations
│           └── ProjectMarker[] (mapped)
│               ├── Icon Element
│               └── Popup
│
├── Right Sidebar
│   ├── OptimizationPanel
│   │   ├── Project Selection
│   │   │   └── Checkboxes[]
│   │   ├── Quick Optimize Button
│   │   └── Advanced Settings (collapsible)
│   │       ├── Name Input
│   │       ├── Objective Select
│   │       ├── Time Horizon
│   │       ├── Discount Rate
│   │       ├── Budget Constraint
│   │       └── Renewable % Constraint
│   │
│   └── ResultsDashboard
│       ├── Key Metrics Grid
│       │   ├── Total Cost
│       │   ├── Total Capacity
│       │   ├── Renewable %
│       │   └── LCOE
│       ├── Additional Metrics
│       │   ├── Emissions
│       │   └── Capacity Factor
│       ├── Project Configurations[]
│       └── Action Buttons
│           ├── Export Results
│           └── Save Scenario
│
└── Floating Components
    ├── ProgressIndicator (bottom-right)
    │   ├── Spinner
    │   ├── Job Name
    │   └── Progress Bar
    │
    └── ProjectForm (modal, conditional)
        ├── Modal Overlay
        └── Form Content
            ├── Basic Info
            │   ├── Name Input
            │   └── Type Select
            ├── Location
            │   ├── Latitude Input
            │   └── Longitude Input
            ├── Technical Specs
            │   ├── Capacity Input
            │   ├── CAPEX Input
            │   └── OPEX Input
            └── Actions
                ├── Cancel Button
                └── Create Button
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Redux Store                              │
│  ┌──────────────┬──────────────────┬───────────────────────┐    │
│  │  projects    │  optimization    │       map             │    │
│  │  ────────    │  ────────────    │       ───             │    │
│  │  • projects[]│  • jobs[]        │  • viewState          │    │
│  │  • selected  │  • currentJob    │  • layers{}           │    │
│  │  • loading   │  • results       │  • mapInstance        │    │
│  │  • error     │  • isRunning     │  • isLoaded           │    │
│  └──────────────┴──────────────────┴───────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌──────────┐   ┌──────────┐   ┌──────────┐
     │useAppSel │   │useAppSel │   │useAppSel │
     │  ector   │   │  ector   │   │  ector   │
     └────┬─────┘   └────┬─────┘   └────┬─────┘
          │              │              │
          ▼              ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌─────────┐
    │ Project │    │Optimiz.  │   │   Map   │
    │  List   │    │  Panel   │   │  View   │
    └────┬────┘    └────┬─────┘   └────┬────┘
         │              │              │
         │    User      │    User      │   User
         │    Action    │    Action    │  Action
         ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │useAppDis │   │useAppDis │   │useAppDis │
    │  patch   │   │  patch   │   │  patch   │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌─────────┐
    │ Action/ │    │ Action/  │   │ Action  │
    │  Thunk  │    │  Thunk   │   │         │
    └────┬────┘    └────┬─────┘   └────┬────┘
         │              │              │
         ▼              ▼              │
    ┌─────────┐    ┌──────────┐      │
    │projects │    │optimiz.  │      │
    │ Service │    │ Service  │      │
    └────┬────┘    └────┬─────┘      │
         │              │             │
         ▼              ▼             │
    ┌────────────────────────────┐   │
    │     Backend API            │   │
    │  http://localhost:8000     │   │
    └────────────────────────────┘   │
                                     │
                                     │
         ┌───────────────────────────┘
         │
         ▼
    ┌─────────┐
    │  Redux  │
    │  State  │
    │ Update  │
    └─────────┘
```

## State Flow Examples

### Creating a Project

```
User clicks map
    ↓
MapView catches click event
    ↓
Dispatch custom DOM event 'mapClick'
    ↓
App.tsx catches event
    ↓
Set clickCoordinates state
    ↓
Open ProjectForm modal
    ↓
User fills form
    ↓
Form submit → dispatch(createProject())
    ↓
projectsService.createProject()
    ↓
POST /api/v1/projects/
    ↓
Backend returns new project
    ↓
Redux: projects.projects.push(newProject)
    ↓
ProjectList re-renders
    ↓
MapView re-renders
    ↓
New ProjectMarker appears
```

### Running Optimization

```
User selects projects in OptimizationPanel
    ↓
User clicks "Run Quick Optimization"
    ↓
dispatch(runQuickOptimization(projectIds))
    ↓
optimizationService.runQuickOptimization()
    ↓
POST /api/v1/optimization/quick
    ↓
Backend returns job object
    ↓
Redux: optimization.currentJob = job
    ↓
Redux: optimization.isRunning = true
    ↓
OptimizationPanel shows "Running" state
    ↓
ProgressIndicator appears (bottom-right)
    ↓
Poll for status every 2 seconds
    ↓
dispatch(fetchJobStatus(jobId))
    ↓
GET /api/v1/optimization/jobs/{id}/status
    ↓
Update progress percentage
    ↓
When status = "completed":
    ↓
dispatch(fetchJobResults(jobId))
    ↓
GET /api/v1/optimization/jobs/{id}/results
    ↓
Redux: optimization.results = results
    ↓
Redux: optimization.isRunning = false
    ↓
ResultsDashboard shows results
    ↓
ProgressIndicator disappears
```

### Dragging a Project Marker

```
User drags marker
    ↓
Mapbox fires 'dragend' event
    ↓
ProjectMarker catches event
    ↓
Get new LngLat from marker
    ↓
dispatch(updateProjectCoordinates({id, lat, lng}))
    ↓
projectsService.updateProjectCoordinates()
    ↓
PATCH /api/v1/projects/{id}/coordinates
    ↓
Backend returns updated project
    ↓
Redux: update project in projects array
    ↓
ProjectCard in sidebar updates
    ↓
(Marker already at new position visually)
```

## Component Props Flow

### ProjectCard

```typescript
ProjectList
    ↓ props
ProjectCard
    ├── project: Project          (from Redux)
    ├── onSelect: () => void      (dispatch setSelectedProject)
    └── onDelete: () => void      (dispatch deleteProject)
```

### ProjectMarker

```typescript
MapView
    ↓ props
ProjectMarker
    ├── project: Project          (from Redux)
    └── map: mapboxgl.Map         (from MapView ref)
        ↓ (creates marker on mount)
        ↓ (attaches event listeners)
        └── (updates marker on project change)
```

### OptimizationPanel

```typescript
OptimizationPanel
    ├── Uses Redux:
    │   ├── projects (for selection)
    │   ├── isRunning (to disable buttons)
    │   └── currentJob (to show status)
    │
    ├── Local State:
    │   ├── selectedProjects: string[]
    │   ├── isExpanded: boolean
    │   └── formData: OptimizationFormData
    │
    └── Dispatches:
        ├── runQuickOptimization()
        └── createOptimizationJob()
```

## Event Flow

### Map Click Event

```
User clicks map
    ↓
Mapbox 'click' event
    ↓
MapView handler
    ↓
window.dispatchEvent('mapClick')
    ↓
App.tsx window listener
    ↓
Set clickCoordinates
    ↓
Open ProjectForm
    ↓
Form pre-filled with coordinates
```

### Dark Mode Toggle

```
User clicks dark mode button
    ↓
setIsDarkMode(!isDarkMode)
    ↓
useEffect detects change
    ↓
document.documentElement.classList.toggle('dark')
    ↓
Tailwind dark: classes apply
    ↓
All components re-style
```

## API Service Architecture

```
Component
    ↓
Redux Thunk
    ↓
Service (projectsService, optimizationService, etc.)
    ↓
apiClient (Axios instance)
    ↓ Request Interceptor
    ├── Add auth token
    ├── Log request (dev)
    └── Return config
    ↓
HTTP Request → Backend API
    ↓
HTTP Response
    ↓ Response Interceptor
    ├── Log response (dev)
    ├── Handle 401 (redirect to login)
    ├── Handle 403 (show error)
    ├── Handle 404 (show error)
    └── Handle 500 (show error)
    ↓
Return to Service
    ↓
Return to Redux Thunk
    ↓
Update Redux State
    ↓
Component Re-renders
```

## Redux Middleware Flow

```
Component
    ↓
dispatch(action)
    ↓
Redux Store
    ↓ Middleware Pipeline
    ├── Redux DevTools (for debugging)
    ├── Redux Thunk (for async actions)
    └── Custom Middleware (future: logging, analytics)
    ↓
Reducer (projectsSlice, optimizationSlice, mapSlice)
    ↓
New State
    ↓
Notify Subscribers
    ↓
useSelector hooks update
    ↓
Components re-render
```

## Key Interactions

### 1. Create Project Flow
```
Map Click → ProjectForm → API → Redux → ProjectList & MapView Update
```

### 2. Optimize Projects Flow
```
OptimizationPanel → API → Redux → ProgressIndicator → ResultsDashboard
```

### 3. Move Project Flow
```
Drag Marker → API → Redux → ProjectList Update (coordinates)
```

### 4. Toggle Layer Flow
```
LayerControls → Redux (mapSlice) → MapView/GridTopologyLayer Re-render
```

### 5. Delete Project Flow
```
ProjectCard → Confirm → API → Redux → ProjectList & MapView Update
```

This component map provides a complete visual understanding of how the CANOPI frontend is structured and how data flows through the application.
