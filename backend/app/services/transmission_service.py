"""
Transmission Line Data Service

Serves transmission line data from GeoJSON files with spatial filtering
and aggregation capabilities for the North American grid.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
import math


class TransmissionService:
    """Service for loading and querying transmission line data."""

    def __init__(self):
        self.lines: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self._loaded = False
        self._spatial_index: Dict[str, List[int]] = {}  # Grid-based spatial index

    def load_from_geojson(self, filepath: Path):
        """Load transmission data from a GeoJSON file."""
        if not filepath.exists():
            print(f"Warning: Transmission data file not found: {filepath}")
            return

        print(f"Loading transmission data from {filepath}...")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        features = data.get("features", [])

        for feature in features:
            props = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            if geometry:
                line_data = {
                    "id": props.get("id"),
                    "voltage_kv": props.get("voltage_kv", 0),
                    "voltage_class": props.get("voltage_class", "Unknown"),
                    "owner": props.get("owner", "Unknown"),
                    "sub_1": props.get("sub_1", "Unknown"),
                    "sub_2": props.get("sub_2", "Unknown"),
                    "status": props.get("status", "operational"),
                    "length_km": props.get("length_km", 0),
                    "capacity_mw": props.get("capacity_mw", 0),
                    "country": props.get("country", "Unknown"),
                    "state_province": props.get("state_province", "Unknown"),
                    "geometry": geometry,
                }
                self.lines.append(line_data)

        self._loaded = True
        self._build_spatial_index()
        print(f"Loaded {len(self.lines)} transmission lines")

    def load_from_directory(self, data_dir: Path):
        """Load all transmission GeoJSON files from a directory."""
        if not data_dir.exists():
            print(f"Warning: Data directory not found: {data_dir}")
            return

        geojson_files = list(data_dir.glob("*.geojson"))
        if not geojson_files:
            print(f"No GeoJSON files found in {data_dir}")
            return

        for filepath in geojson_files:
            self.load_from_geojson(filepath)

    def _build_spatial_index(self):
        """Build a simple grid-based spatial index for fast bbox queries."""
        # Use 5-degree grid cells
        grid_size = 5.0
        self._spatial_index = {}

        for idx, line in enumerate(self.lines):
            geometry = line.get("geometry", {})
            if geometry.get("type") != "LineString":
                continue

            coords = geometry.get("coordinates", [])
            if not coords:
                continue

            # Add line to all grid cells it intersects
            cells_added = set()
            for coord in coords:
                lon, lat = coord[0], coord[1]
                cell_x = int(lon // grid_size)
                cell_y = int(lat // grid_size)
                cell_key = f"{cell_x},{cell_y}"

                if cell_key not in cells_added:
                    if cell_key not in self._spatial_index:
                        self._spatial_index[cell_key] = []
                    self._spatial_index[cell_key].append(idx)
                    cells_added.add(cell_key)

    def _get_cells_for_bbox(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float
    ) -> List[str]:
        """Get all grid cells that intersect with a bounding box."""
        grid_size = 5.0
        cells = []

        min_cell_x = int(min_lon // grid_size)
        max_cell_x = int(max_lon // grid_size)
        min_cell_y = int(min_lat // grid_size)
        max_cell_y = int(max_lat // grid_size)

        for x in range(min_cell_x, max_cell_x + 1):
            for y in range(min_cell_y, max_cell_y + 1):
                cells.append(f"{x},{y}")

        return cells

    def _line_intersects_bbox(
        self,
        geometry: Dict,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float
    ) -> bool:
        """Check if a line geometry intersects with a bounding box."""
        if geometry.get("type") != "LineString":
            return False

        coords = geometry.get("coordinates", [])
        for coord in coords:
            lon, lat = coord[0], coord[1]
            if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                return True

        return False

    def get_lines(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        min_voltage: Optional[int] = None,
        max_voltage: Optional[int] = None,
        country: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Get transmission lines with filtering.

        Args:
            min_lat, max_lat, min_lon, max_lon: Bounding box
            min_voltage: Minimum voltage in kV
            max_voltage: Maximum voltage in kV
            country: Filter by country (USA, Canada)
            status: Filter by status (operational, planned, etc.)
            limit: Maximum number of results

        Returns:
            List of transmission line dictionaries
        """
        result = []

        # Use spatial index if bbox provided
        if all(v is not None for v in [min_lat, max_lat, min_lon, max_lon]):
            cells = self._get_cells_for_bbox(min_lon, min_lat, max_lon, max_lat)
            candidate_indices = set()
            for cell in cells:
                if cell in self._spatial_index:
                    candidate_indices.update(self._spatial_index[cell])

            candidates = [self.lines[i] for i in candidate_indices]
        else:
            candidates = self.lines

        for line in candidates:
            # Bounding box filter
            if all(v is not None for v in [min_lat, max_lat, min_lon, max_lon]):
                if not self._line_intersects_bbox(
                    line["geometry"], min_lon, min_lat, max_lon, max_lat
                ):
                    continue

            # Voltage filter
            if min_voltage is not None and line["voltage_kv"] < min_voltage:
                continue
            if max_voltage is not None and line["voltage_kv"] > max_voltage:
                continue

            # Country filter
            if country is not None and line["country"] != country:
                continue

            # Status filter
            if status is not None and line["status"] != status:
                continue

            result.append(line)

            if len(result) >= limit:
                break

        return result

    def get_lines_geojson(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        min_voltage: Optional[int] = None,
        simplify: bool = True,
        limit: int = 10000
    ) -> Dict[str, Any]:
        """
        Get transmission lines as GeoJSON FeatureCollection.

        Args:
            min_lat, max_lat, min_lon, max_lon: Bounding box
            min_voltage: Minimum voltage threshold
            simplify: Whether to simplify geometries for smaller payload
            limit: Maximum features

        Returns:
            GeoJSON FeatureCollection
        """
        lines = self.get_lines(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            min_voltage=min_voltage,
            limit=limit
        )

        features = []
        for line in lines:
            geometry = line["geometry"]

            # Optionally simplify geometry for large datasets
            if simplify and geometry.get("type") == "LineString":
                coords = geometry.get("coordinates", [])
                if len(coords) > 10:
                    # Keep every nth point plus first and last
                    step = max(1, len(coords) // 10)
                    simplified_coords = [coords[0]]
                    for i in range(step, len(coords) - 1, step):
                        simplified_coords.append(coords[i])
                    simplified_coords.append(coords[-1])
                    geometry = {"type": "LineString", "coordinates": simplified_coords}

            feature = {
                "type": "Feature",
                "properties": {
                    "id": line["id"],
                    "voltage_kv": line["voltage_kv"],
                    "capacity_mw": line["capacity_mw"],
                    "owner": line["owner"],
                    "status": line["status"],
                    "country": line["country"],
                },
                "geometry": geometry
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total_count": len(features),
                "filtered": True if any([min_lat, min_voltage]) else False
            }
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for loaded transmission data."""
        if not self.lines:
            return {"error": "No data loaded"}

        stats = {
            "total_lines": len(self.lines),
            "total_length_km": sum(l["length_km"] for l in self.lines),
            "total_capacity_mw": sum(l["capacity_mw"] for l in self.lines),
            "by_country": {},
            "by_voltage_class": {},
            "by_status": {},
            "voltage_range": {
                "min": min(l["voltage_kv"] for l in self.lines),
                "max": max(l["voltage_kv"] for l in self.lines),
            }
        }

        for line in self.lines:
            # By country
            country = line["country"]
            if country not in stats["by_country"]:
                stats["by_country"][country] = {
                    "count": 0,
                    "length_km": 0,
                    "capacity_mw": 0
                }
            stats["by_country"][country]["count"] += 1
            stats["by_country"][country]["length_km"] += line["length_km"]
            stats["by_country"][country]["capacity_mw"] += line["capacity_mw"]

            # By voltage class
            v_class = line["voltage_class"]
            if v_class not in stats["by_voltage_class"]:
                stats["by_voltage_class"][v_class] = {"count": 0, "length_km": 0}
            stats["by_voltage_class"][v_class]["count"] += 1
            stats["by_voltage_class"][v_class]["length_km"] += line["length_km"]

            # By status
            status = line["status"]
            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += 1

        return stats

    def find_lines_near_point(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50.0,
        min_voltage: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find transmission lines within a radius of a point."""
        results = []

        for line in self.lines:
            if min_voltage and line["voltage_kv"] < min_voltage:
                continue

            geometry = line.get("geometry", {})
            if geometry.get("type") != "LineString":
                continue

            # Find minimum distance from point to line
            min_distance = float("inf")
            for coord in geometry.get("coordinates", []):
                lon, lat = coord[0], coord[1]
                distance = self._haversine_distance(latitude, longitude, lat, lon)
                min_distance = min(min_distance, distance)

            if min_distance <= radius_km:
                result = line.copy()
                result["distance_km"] = round(min_distance, 2)
                results.append(result)

        # Sort by distance
        results.sort(key=lambda x: x["distance_km"])
        return results

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points in km using Haversine formula."""
        R = 6371  # Earth radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c


# Global instance
_transmission_service: Optional[TransmissionService] = None


def get_transmission_service() -> TransmissionService:
    """Get or create the global transmission service instance."""
    global _transmission_service

    if _transmission_service is None:
        _transmission_service = TransmissionService()

        # Look for transmission data in multiple locations
        project_root = Path(__file__).parent.parent.parent.parent
        data_locations = [
            project_root / "data_pipelines" / "transmission_data",
            project_root / "data" / "transmission",
            project_root / "backend" / "data" / "transmission",
        ]

        for data_dir in data_locations:
            if data_dir.exists():
                _transmission_service.load_from_directory(data_dir)
                break
        else:
            print("Note: No transmission data directory found. Run transmission_downloader.py to fetch data.")

    return _transmission_service
