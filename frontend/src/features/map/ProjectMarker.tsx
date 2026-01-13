import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { Project, ProjectType } from '../../types';
import { useAppDispatch } from '../../store/hooks';
import { setSelectedProject } from '../../store/projectsSlice';
import { updateProjectCoordinates } from '../../store/projectsSlice';

interface ProjectMarkerProps {
  project: Project;
  map: mapboxgl.Map;
}

const getProjectIcon = (type: ProjectType): string => {
  switch (type) {
    case ProjectType.SOLAR:
      return '☀️';
    case ProjectType.WIND:
      return '💨';
    case ProjectType.STORAGE:
      return '⚡';
    case ProjectType.DATACENTER:
      return '🏢';
    default:
      return '📍';
  }
};

const getProjectColor = (type: ProjectType): string => {
  switch (type) {
    case ProjectType.SOLAR:
      return '#F59E0B'; // Solar Yellow
    case ProjectType.WIND:
      return '#06B6D4'; // Electric Teal
    case ProjectType.STORAGE:
      return '#8B5CF6'; // Purple
    case ProjectType.DATACENTER:
      return '#1E40AF'; // Deep Blue
    default:
      return '#6B7280';
  }
};

export const ProjectMarker: React.FC<ProjectMarkerProps> = ({ project, map }) => {
  const markerRef = useRef<mapboxgl.Marker | null>(null);
  const dispatch = useAppDispatch();

  useEffect(() => {
    if (!map || markerRef.current) return;

    // Create marker element
    const el = document.createElement('div');
    el.className = 'project-marker';
    el.innerHTML = `
      <div class="flex flex-col items-center cursor-pointer transition-transform hover:scale-110">
        <div class="text-3xl" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
          ${getProjectIcon(project.type)}
        </div>
        <div class="bg-white dark:bg-gray-800 px-2 py-1 rounded shadow-lg text-xs font-semibold mt-1 border-2"
             style="border-color: ${getProjectColor(project.type)};">
          ${project.name}
        </div>
      </div>
    `;

    // Create marker
    const marker = new mapboxgl.Marker({
      element: el,
      draggable: true,
      anchor: 'bottom',
    })
      .setLngLat([project.coordinates.longitude, project.coordinates.latitude])
      .addTo(map);

    // Handle marker click
    el.addEventListener('click', () => {
      dispatch(setSelectedProject(project));
    });

    // Handle marker drag
    marker.on('dragend', () => {
      const lngLat = marker.getLngLat();
      dispatch(
        updateProjectCoordinates({
          id: project.id,
          latitude: lngLat.lat,
          longitude: lngLat.lng,
        })
      );
    });

    // Create popup
    const popup = new mapboxgl.Popup({
      offset: 25,
      closeButton: false,
      closeOnClick: false,
    }).setHTML(`
      <div class="p-2">
        <h3 class="font-bold text-sm mb-1">${project.name}</h3>
        <p class="text-xs text-gray-600 dark:text-gray-400">
          Type: ${project.type}<br/>
          Capacity: ${project.capacity_mw} MW<br/>
          Location: ${project.coordinates.latitude.toFixed(4)}, ${project.coordinates.longitude.toFixed(4)}
        </p>
      </div>
    `);

    // Show popup on hover
    el.addEventListener('mouseenter', () => {
      marker.setPopup(popup);
      popup.addTo(map);
    });

    el.addEventListener('mouseleave', () => {
      popup.remove();
    });

    markerRef.current = marker;

    return () => {
      if (markerRef.current) {
        markerRef.current.remove();
        markerRef.current = null;
      }
    };
  }, [map, project, dispatch]);

  // Update marker position if project coordinates change
  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.setLngLat([
        project.coordinates.longitude,
        project.coordinates.latitude,
      ]);
    }
  }, [project.coordinates]);

  return null;
};
