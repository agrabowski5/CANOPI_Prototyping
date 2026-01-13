import React, { useEffect, useState, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { useAppSelector } from '../../store/hooks';
import gridService from '../../services/gridService';
import { GridTopology } from '../../types';

interface GridTopologyLayerProps {
  map: mapboxgl.Map;
}

// Helper to safely check if map is valid and has style loaded
const isMapReady = (map: mapboxgl.Map | null): boolean => {
  try {
    return !!(map && map.getStyle() && map.isStyleLoaded());
  } catch {
    return false;
  }
};

// Helper to safely get layer
const safeGetLayer = (map: mapboxgl.Map, layerId: string): mapboxgl.AnyLayer | undefined => {
  try {
    if (!isMapReady(map)) return undefined;
    return map.getLayer(layerId);
  } catch {
    return undefined;
  }
};

// Helper to safely get source
const safeGetSource = (map: mapboxgl.Map, sourceId: string): mapboxgl.AnySourceImpl | undefined => {
  try {
    if (!isMapReady(map)) return undefined;
    return map.getSource(sourceId);
  } catch {
    return undefined;
  }
};

export const GridTopologyLayer: React.FC<GridTopologyLayerProps> = ({ map }) => {
  const [topology, setTopology] = useState<GridTopology | null>(null);
  const layers = useAppSelector((state) => state.map.layers);
  const isMounted = useRef(true);
  const popupRef = useRef<mapboxgl.Popup | null>(null);
  const isHoveringPopup = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    // Fetch grid topology
    const fetchTopology = async () => {
      try {
        const data = await gridService.getGridTopology({
          min_lat: 14,    // Southern Mexico
          max_lat: 62,    // Northern Canada
          min_lon: -141,  // Alaska/Western Canada
          max_lon: -52,   // Eastern Canada/Atlantic
          voltage_threshold: 100,
          limit: 2000,    // Increase limit to get all nodes
        });
        if (isMounted.current) {
          setTopology(data);
        }
      } catch (error) {
        console.error('Failed to fetch grid topology:', error);
        // Use mock data for development
        if (isMounted.current) {
          setTopology({
            nodes: [],
            lines: [],
          });
        }
      }
    };

    fetchTopology();

    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (!map || !topology) return;

    // Wait for map style to load
    if (!isMapReady(map)) {
      const onStyleData = () => addGridLayers();
      map.once('styledata', onStyleData);
      return () => {
        try {
          map.off('styledata', onStyleData);
        } catch {
          // Map may be removed
        }
      };
    }

    addGridLayers();

    function addGridLayers() {
      if (!topology || !topology.lines || !topology.nodes) return;
      if (!isMapReady(map)) return;

      // Remove existing layers if they exist
      try {
        if (safeGetLayer(map, 'transmission-lines')) {
          map.removeLayer('transmission-lines');
        }
        if (safeGetLayer(map, 'substations')) {
          map.removeLayer('substations');
        }
        if (safeGetSource(map, 'transmission-lines')) {
          map.removeSource('transmission-lines');
        }
        if (safeGetSource(map, 'substations')) {
          map.removeSource('substations');
        }
      } catch (e) {
        console.warn('Error removing existing layers:', e);
        return;
      }

      // Add transmission lines
      if (topology.lines && topology.lines.length > 0 && layers.transmission) {
        const lineFeatures = topology.lines.map((line) => {
          const fromNode = topology.nodes.find((n) => n.id === line.from_node_id);
          const toNode = topology.nodes.find((n) => n.id === line.to_node_id);

          if (!fromNode || !toNode) return null;

          return {
            type: 'Feature' as const,
            properties: {
              id: line.id,
              capacity: line.capacity_mw,
              voltage: line.voltage_kv,
              status: line.status,
            },
            geometry: {
              type: 'LineString' as const,
              coordinates: [
                [fromNode.coordinates.longitude, fromNode.coordinates.latitude],
                [toNode.coordinates.longitude, toNode.coordinates.latitude],
              ],
            },
          };
        }).filter((f) => f !== null);

        map.addSource('transmission-lines', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: lineFeatures as any[],
          },
        });

        map.addLayer({
          id: 'transmission-lines',
          type: 'line',
          source: 'transmission-lines',
          paint: {
            'line-color': [
              'match',
              ['get', 'status'],
              'operational',
              '#06B6D4',
              'planned',
              '#F59E0B',
              'under_construction',
              '#8B5CF6',
              '#6B7280',
            ],
            'line-width': [
              'interpolate',
              ['linear'],
              ['get', 'voltage'],
              100,
              1,
              345,
              3,
              500,
              5,
            ],
            'line-opacity': 0.7,
          },
        });
      }

      // Add substations
      if (topology.nodes && topology.nodes.length > 0 && layers.substations) {
        const nodeFeatures = topology.nodes.map((node) => ({
          type: 'Feature' as const,
          properties: {
            id: node.id,
            name: node.name,
            voltage: node.voltage_kv,
            type: node.type,
          },
          geometry: {
            type: 'Point' as const,
            coordinates: [node.coordinates.longitude, node.coordinates.latitude],
          },
        }));

        map.addSource('substations', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: nodeFeatures,
          },
        });

        map.addLayer({
          id: 'substations',
          type: 'circle',
          source: 'substations',
          paint: {
            'circle-radius': [
              'interpolate',
              ['linear'],
              ['get', 'voltage'],
              100,
              4,
              345,
              8,
              500,
              12,
            ],
            'circle-color': '#1E40AF',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 0.8,
          },
        });

        // Add popup on hover with proper lifecycle management
        const showPopup = (e: mapboxgl.MapLayerMouseEvent) => {
          map.getCanvas().style.cursor = 'pointer';

          if (e.features && e.features[0]) {
            // Close existing popup if any
            if (popupRef.current) {
              popupRef.current.remove();
              popupRef.current = null;
            }

            const feature = e.features[0];
            const coordinates = (feature.geometry as any).coordinates.slice();
            const props = feature.properties;

            const popup = new mapboxgl.Popup({
              closeButton: true,
              closeOnClick: false,
              className: 'substation-popup',
            })
              .setLngLat(coordinates)
              .setHTML(`
                <div class="p-2" style="min-width: 150px;">
                  <h3 style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${props?.name || 'Substation'}</h3>
                  <p style="font-size: 12px; color: #666;">
                    Voltage: ${props?.voltage} kV<br/>
                    Type: ${props?.type}
                  </p>
                </div>
              `)
              .addTo(map);

            // Track when mouse enters/leaves the popup
            const popupElement = popup.getElement();
            if (popupElement) {
              popupElement.addEventListener('mouseenter', () => {
                isHoveringPopup.current = true;
              });
              popupElement.addEventListener('mouseleave', () => {
                isHoveringPopup.current = false;
                // Small delay to allow moving to another substation
                setTimeout(() => {
                  if (!isHoveringPopup.current && popupRef.current) {
                    popupRef.current.remove();
                    popupRef.current = null;
                  }
                }, 100);
              });
            }

            popupRef.current = popup;
          }
        };

        const hidePopup = () => {
          map.getCanvas().style.cursor = '';
          // Small delay to check if we're hovering the popup
          setTimeout(() => {
            if (!isHoveringPopup.current && popupRef.current) {
              popupRef.current.remove();
              popupRef.current = null;
            }
          }, 100);
        };

        map.on('mouseenter', 'substations', showPopup);
        map.on('mouseleave', 'substations', hidePopup);
      }
    }

    return () => {
      try {
        // Close any open popup
        if (popupRef.current) {
          popupRef.current.remove();
          popupRef.current = null;
        }
        if (safeGetLayer(map, 'transmission-lines')) {
          map.removeLayer('transmission-lines');
        }
        if (safeGetLayer(map, 'substations')) {
          map.removeLayer('substations');
        }
        if (safeGetSource(map, 'transmission-lines')) {
          map.removeSource('transmission-lines');
        }
        if (safeGetSource(map, 'substations')) {
          map.removeSource('substations');
        }
      } catch (e) {
        // Map may be removed, ignore cleanup errors
      }
    };
  }, [map, topology, layers.transmission, layers.substations]);

  return null;
};
