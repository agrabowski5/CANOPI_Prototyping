"""
Transmission Lines API Endpoints

Provides access to North American transmission line data including:
- Transmission line geometry and attributes
- Filtering by voltage, location, country
- Capacity and infrastructure statistics
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from ...services.transmission_service import get_transmission_service


router = APIRouter(prefix="/transmission", tags=["Transmission"])


class TransmissionLineResponse(BaseModel):
    """Response model for a single transmission line."""
    id: str
    voltage_kv: int
    voltage_class: str
    owner: str
    sub_1: str
    sub_2: str
    status: str
    length_km: float
    capacity_mw: float
    country: str
    state_province: str


class TransmissionStatsResponse(BaseModel):
    """Response model for transmission statistics."""
    total_lines: int
    total_length_km: float
    total_capacity_mw: float
    by_country: Dict[str, Dict[str, Any]]
    by_voltage_class: Dict[str, Dict[str, Any]]
    by_status: Dict[str, int]
    voltage_range: Dict[str, int]


class NearbyLinesRequest(BaseModel):
    """Request model for finding nearby transmission lines."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(default=50.0, ge=1, le=500)
    min_voltage: Optional[int] = Field(default=None, ge=69)


@router.get("/lines", response_model=Dict[str, Any])
async def get_transmission_lines(
    min_lat: Optional[float] = Query(None, ge=-90, le=90, description="Minimum latitude"),
    max_lat: Optional[float] = Query(None, ge=-90, le=90, description="Maximum latitude"),
    min_lon: Optional[float] = Query(None, ge=-180, le=180, description="Minimum longitude"),
    max_lon: Optional[float] = Query(None, ge=-180, le=180, description="Maximum longitude"),
    min_voltage: Optional[int] = Query(None, ge=69, description="Minimum voltage in kV"),
    max_voltage: Optional[int] = Query(None, le=1000, description="Maximum voltage in kV"),
    country: Optional[str] = Query(None, description="Filter by country (USA, Canada)"),
    status: Optional[str] = Query(None, description="Filter by status (operational, planned)"),
    format: str = Query("geojson", description="Response format: geojson or list"),
    simplify: bool = Query(True, description="Simplify geometries for smaller payload"),
    limit: int = Query(10000, ge=1, le=50000, description="Maximum number of results"),
):
    """
    Get transmission lines with optional filtering.

    Returns transmission lines as GeoJSON FeatureCollection or list of objects.
    Use bounding box parameters to filter by geographic area.
    """
    service = get_transmission_service()

    if format == "geojson":
        return service.get_lines_geojson(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            min_voltage=min_voltage,
            simplify=simplify,
            limit=limit
        )
    else:
        lines = service.get_lines(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            min_voltage=min_voltage,
            max_voltage=max_voltage,
            country=country,
            status=status,
            limit=limit
        )
        # Remove geometry for list format (smaller payload)
        for line in lines:
            if "geometry" in line:
                del line["geometry"]
        return {"lines": lines, "count": len(lines)}


@router.get("/lines/geojson")
async def get_transmission_geojson(
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lat: Optional[float] = Query(None, ge=-90, le=90),
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    min_voltage: Optional[int] = Query(69, ge=69, description="Minimum voltage in kV"),
    simplify: bool = Query(True, description="Simplify geometries"),
    limit: int = Query(10000, ge=1, le=50000),
):
    """
    Get transmission lines as GeoJSON FeatureCollection.

    Optimized endpoint for map visualization.
    """
    service = get_transmission_service()

    return service.get_lines_geojson(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        min_voltage=min_voltage,
        simplify=simplify,
        limit=limit
    )


@router.get("/stats", response_model=TransmissionStatsResponse)
async def get_transmission_statistics():
    """
    Get summary statistics for all loaded transmission data.

    Returns counts, lengths, and capacities grouped by country,
    voltage class, and status.
    """
    service = get_transmission_service()
    stats = service.get_statistics()

    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])

    return stats


@router.post("/nearby")
async def find_nearby_lines(request: NearbyLinesRequest):
    """
    Find transmission lines near a specific point.

    Returns lines within the specified radius, sorted by distance.
    Useful for interconnection analysis.
    """
    service = get_transmission_service()

    lines = service.find_lines_near_point(
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        min_voltage=request.min_voltage
    )

    # Remove full geometry for response (keep first/last coords for reference)
    for line in lines:
        if "geometry" in line:
            coords = line["geometry"].get("coordinates", [])
            if coords:
                line["start_coord"] = coords[0]
                line["end_coord"] = coords[-1]
            del line["geometry"]

    return {
        "center": {"latitude": request.latitude, "longitude": request.longitude},
        "radius_km": request.radius_km,
        "lines": lines,
        "count": len(lines)
    }


@router.get("/voltage-classes")
async def get_voltage_classes():
    """
    Get available voltage classes and their typical capacities.

    Returns reference data for transmission voltage levels.
    """
    return {
        "voltage_classes": [
            {"voltage_kv": 69, "class": "Sub-transmission", "typical_capacity_mw": 75},
            {"voltage_kv": 115, "class": "Sub-transmission", "typical_capacity_mw": 150},
            {"voltage_kv": 138, "class": "Transmission", "typical_capacity_mw": 200},
            {"voltage_kv": 161, "class": "Transmission", "typical_capacity_mw": 250},
            {"voltage_kv": 230, "class": "High Voltage", "typical_capacity_mw": 400},
            {"voltage_kv": 287, "class": "High Voltage", "typical_capacity_mw": 500},
            {"voltage_kv": 345, "class": "Extra High Voltage", "typical_capacity_mw": 900},
            {"voltage_kv": 500, "class": "Extra High Voltage", "typical_capacity_mw": 2000},
            {"voltage_kv": 765, "class": "Ultra High Voltage", "typical_capacity_mw": 3500},
        ],
        "notes": [
            "Capacity values are typical ratings and vary by conductor type and configuration",
            "HVDC lines may have different characteristics",
            "Thermal limits, stability limits, and contractual limits may differ"
        ]
    }


@router.get("/coverage")
async def get_coverage_info():
    """
    Get information about data coverage and sources.

    Returns metadata about the transmission data including sources,
    coverage areas, and data freshness.
    """
    service = get_transmission_service()
    stats = service.get_statistics()

    coverage = {
        "data_sources": [
            {
                "name": "HIFLD",
                "full_name": "Homeland Infrastructure Foundation-Level Data",
                "coverage": "United States",
                "url": "https://hifld-geoplatform.hub.arcgis.com/",
                "fields": ["voltage", "owner", "status", "substations"]
            },
            {
                "name": "NRCan",
                "full_name": "Natural Resources Canada",
                "coverage": "Canada",
                "url": "https://open.canada.ca/",
                "fields": ["voltage", "owner"]
            }
        ],
        "geographic_coverage": {
            "countries": list(stats.get("by_country", {}).keys()) if stats else [],
            "bbox": {
                "min_lat": 24.0,
                "max_lat": 72.0,
                "min_lon": -170.0,
                "max_lon": -50.0
            }
        },
        "voltage_coverage": stats.get("voltage_range", {}) if stats else {},
        "total_lines": stats.get("total_lines", 0) if stats else 0,
        "total_length_km": stats.get("total_length_km", 0) if stats else 0,
    }

    return coverage
