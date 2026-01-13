import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { setMapInstance, setViewState } from '../../store/mapSlice';
import { ProjectMarker } from './ProjectMarker';
import { GridTopologyLayer } from './GridTopologyLayer';
import { LayerControls } from './LayerControls';
import { OptimalLocationsLayer } from './OptimalLocationsLayer';
import { TransmissionUpgradesLayer } from './TransmissionUpgradesLayer';
import { TransmissionNetworkLayer } from './TransmissionNetworkLayer';

// Set Mapbox token
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN || '';

export const MapView: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const dispatch = useAppDispatch();
  const viewState = useAppSelector((state) => state.map.viewState);
  const layers = useAppSelector((state) => state.map.layers);
  const projects = useAppSelector((state) => state.projects.projects);
  const optimizationResults = useAppSelector((state) => state.optimization.results);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: layers.satellite
        ? 'mapbox://styles/mapbox/satellite-streets-v12'
        : layers.terrain
        ? 'mapbox://styles/mapbox/outdoors-v12'
        : 'mapbox://styles/mapbox/light-v11',
      center: [viewState.longitude, viewState.latitude],
      zoom: viewState.zoom,
      pitch: viewState.pitch || 0,
      bearing: viewState.bearing || 0,
      // Explicitly enable interactions
      interactive: true,
      dragPan: true,
      dragRotate: true,
      scrollZoom: true,
      touchZoomRotate: true,
      doubleClickZoom: true,
    });

    // Add navigation controls
    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    // Add scale control
    map.addControl(
      new mapboxgl.ScaleControl({
        maxWidth: 100,
        unit: 'imperial',
      }),
      'bottom-left'
    );

    // Add fullscreen control
    map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

    // Map loaded event
    map.on('load', () => {
      setMapLoaded(true);
      dispatch(setMapInstance(map));
    });

    // Update view state on move
    map.on('moveend', () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      const pitch = map.getPitch();
      const bearing = map.getBearing();

      dispatch(
        setViewState({
          longitude: center.lng,
          latitude: center.lat,
          zoom,
          pitch,
          bearing,
        })
      );
    });

    // Note: Map click handler removed to allow free dragging
    // Projects can be added via the "New Project" button in the sidebar

    mapRef.current = map;

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        dispatch(setMapInstance(null));
      }
    };
  }, []);

  // Update map style when layer toggles
  useEffect(() => {
    if (!mapRef.current) return;

    const newStyle = layers.satellite
      ? 'mapbox://styles/mapbox/satellite-streets-v12'
      : layers.terrain
      ? 'mapbox://styles/mapbox/outdoors-v12'
      : 'mapbox://styles/mapbox/light-v11';

    mapRef.current.setStyle(newStyle);
  }, [layers.satellite, layers.terrain]);

  // Note: Removed flyTo effect that was causing feedback loop with moveend
  // The map's moveend handler already updates Redux state
  // External programmatic navigation should use the flyTo action directly

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainerRef} className="w-full h-full" style={{ cursor: 'grab' }} />

      {mapLoaded && (
        <>
          {/* Layer Controls */}
          <LayerControls />

          {/* Full Transmission Network Layer */}
          {layers.transmission && <TransmissionNetworkLayer map={mapRef.current!} />}

          {/* Grid Topology Layer (substations) */}
          {layers.grid && <GridTopologyLayer map={mapRef.current!} />}

          {/* Project Markers */}
          {layers.projects &&
            projects.map((project) => (
              <ProjectMarker key={project.id} project={project} map={mapRef.current!} />
            ))}

          {/* Optimal Locations Layer (from greenfield optimization) */}
          {optimizationResults?.optimal_locations && (
            <OptimalLocationsLayer
              locations={optimizationResults.optimal_locations}
              map={mapRef.current!}
              visible={layers.optimalLocations !== false}
            />
          )}

          {/* Transmission Upgrades Layer */}
          {optimizationResults?.transmission_upgrades && (
            <TransmissionUpgradesLayer
              upgrades={optimizationResults.transmission_upgrades}
              map={mapRef.current!}
              visible={layers.transmissionUpgrades !== false}
            />
          )}
        </>
      )}

      {/* Loading indicator */}
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-900">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
};
