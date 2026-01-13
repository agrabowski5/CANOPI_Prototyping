"""
Grid Data API endpoints - In-Memory Version

Provides access to transmission network topology without requiring PostgreSQL.
Uses JSON files loaded into memory.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.grid_data_memory import get_grid_service

router = APIRouter()

# Pydantic models for API responses


class Node(BaseModel):
    """Electrical node/bus in the transmission network"""
    id: str
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    voltage_kv: int
    iso_rto: Optional[str] = Field(None, description="ISO/RTO region (CAISO, PJM, ERCOT, etc.)")
    type: str = Field("substation", description="substation, generator, load")
    capacity_mw: Optional[float] = None
    owner: Optional[str] = None


class Branch(BaseModel):
    """Transmission line or transformer"""
    id: str
    name: Optional[str] = None
    from_node_id: str
    to_node_id: str
    capacity_mw: float
    voltage_kv: int
    is_hvdc: bool = False
    length_km: Optional[float] = None
    status: str = "operational"
    owner: Optional[str] = None


class NetworkTopology(BaseModel):
    """Complete network topology"""
    nodes: List[Node]
    branches: List[Branch]
    metadata: dict = Field(default_factory=dict)


@router.get("/topology", response_model=NetworkTopology)
async def get_network_topology(
    region: Optional[str] = Query(None, description="Filter by ISO/RTO region"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    min_lat: Optional[float] = Query(None, description="Minimum latitude for bounding box"),
    max_lat: Optional[float] = Query(None, description="Maximum latitude for bounding box"),
    min_lon: Optional[float] = Query(None, description="Minimum longitude for bounding box"),
    max_lon: Optional[float] = Query(None, description="Maximum longitude for bounding box"),
    voltage_threshold: Optional[int] = Query(None, description="Alias for voltage_min (for backward compatibility)"),
    limit: int = Query(1000, ge=1, le=10000),
):
    """
    Retrieve transmission network topology from in-memory data.

    Supports filtering by:
    - ISO/RTO region
    - Voltage level
    - Geographic bounding box (for map viewport queries)
    """
    # Handle backward compatibility with voltage_threshold parameter
    if voltage_threshold and not voltage_min:
        voltage_min = voltage_threshold

    grid_service = get_grid_service()

    topology_data = grid_service.get_topology(
        region=region,
        voltage_min=voltage_min,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        limit=limit
    )

    # Convert to response models
    nodes = [Node(**node) for node in topology_data['nodes']]
    branches = [Branch(**branch) for branch in topology_data['branches']]

    return NetworkTopology(
        nodes=nodes,
        branches=branches,
        metadata={
            "total_nodes": len(nodes),
            "total_branches": len(branches),
            "region": region or "all",
            "voltage_min_kv": voltage_min,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/nodes", response_model=List[Node])
async def get_network_nodes(
    node_type: Optional[str] = Query(None, description="Filter by type: substation, generator, load"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    iso_rto: Optional[str] = Query(None, description="Filter by ISO/RTO region"),
    limit: int = Query(1000, ge=1, le=10000),
):
    """Get network nodes (substations, generators, load centers)."""
    grid_service = get_grid_service()

    nodes_data = grid_service.get_nodes(
        node_type=node_type,
        voltage_min=voltage_min,
        iso_rto=iso_rto,
        limit=limit
    )

    return [Node(**node) for node in nodes_data]


@router.get("/lines", response_model=List[Branch])
async def get_transmission_lines(
    status: Optional[str] = Query(None, description="Filter by status: operational, planned, under_construction"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    limit: int = Query(1000, ge=1, le=10000),
):
    """Get transmission lines/branches."""
    grid_service = get_grid_service()

    branches_data = grid_service.get_branches(
        status=status,
        voltage_min=voltage_min,
        limit=limit
    )

    return [Branch(**branch) for branch in branches_data]


@router.get("/nearest-substation", response_model=Node)
async def find_nearest_substation(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
):
    """
    Find the nearest substation to a given location.
    Useful for project interconnection planning.
    """
    grid_service = get_grid_service()

    node_data = grid_service.find_nearest_substation(latitude, longitude)

    if not node_data:
        raise HTTPException(status_code=404, detail="No substations found")

    return Node(**node_data)


@router.get("/nodes/{node_id}", response_model=Node)
async def get_node_details(node_id: str):
    """Get detailed information about a specific node."""
    grid_service = get_grid_service()

    node_data = grid_service.get_node_by_id(node_id)

    if not node_data:
        raise HTTPException(status_code=404, detail="Node not found")

    return Node(**node_data)


@router.get("/branches/{branch_id}", response_model=Branch)
async def get_branch_details(branch_id: str):
    """Get detailed information about a specific transmission branch."""
    grid_service = get_grid_service()

    branch_data = grid_service.get_branch_by_id(branch_id)

    if not branch_data:
        raise HTTPException(status_code=404, detail="Branch not found")

    return Branch(**branch_data)
