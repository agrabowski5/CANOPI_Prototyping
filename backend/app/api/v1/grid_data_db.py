"""
Grid Data API endpoints
Provides access to transmission network topology, congestion data, and capacity information
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import to_shape

from app.core.database import get_db
from app.models import grid as grid_models

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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class NetworkTopology(BaseModel):
    """Complete network topology"""
    nodes: List[Node]
    branches: List[Branch]
    metadata: dict = Field(default_factory=dict)


class CongestionData(BaseModel):
    """Real-time or historical congestion information"""
    timestamp: datetime
    branch_id: str
    flow_mw: float
    capacity_mw: float
    utilization: float = Field(..., ge=0, le=1, description="Flow / Capacity")
    lmp_price: Optional[float] = Field(None, description="Locational Marginal Price ($/MWh)")
    shadow_price: Optional[float] = Field(None, description="Shadow price on transmission constraint")


class TransmissionCapacity(BaseModel):
    """Available transmission capacity and upgrade options"""
    branch_id: str
    current_capacity_mw: float
    available_capacity_mw: float
    upgrade_options: List[dict] = Field(default_factory=list, description="Possible upgrade capacities and costs")


@router.get("/topology", response_model=NetworkTopology)
async def get_network_topology(
    region: Optional[str] = Query(None, description="Filter by ISO/RTO region"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    min_lat: Optional[float] = Query(None, description="Minimum latitude for bounding box"),
    max_lat: Optional[float] = Query(None, description="Maximum latitude for bounding box"),
    min_lon: Optional[float] = Query(None, description="Minimum longitude for bounding box"),
    max_lon: Optional[float] = Query(None, description="Maximum longitude for bounding box"),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """
    Retrieve transmission network topology.
    Returns nodes (buses/substations) and branches (transmission lines) from database.

    Supports filtering by:
    - ISO/RTO region
    - Voltage level
    - Geographic bounding box (for map viewport queries)
    """
    # Query nodes with filters
    node_query = db.query(grid_models.Node)

    if region:
        node_query = node_query.filter(grid_models.Node.iso_rto == region)
    if voltage_min:
        node_query = node_query.filter(grid_models.Node.voltage_kv >= voltage_min)
    if min_lat and max_lat and min_lon and max_lon:
        # Filter by bounding box
        node_query = node_query.filter(
            grid_models.Node.latitude >= min_lat,
            grid_models.Node.latitude <= max_lat,
            grid_models.Node.longitude >= min_lon,
            grid_models.Node.longitude <= max_lon
        )

    node_query = node_query.limit(limit)
    nodes_db = node_query.all()

    # Convert to response models
    nodes = []
    for node_db in nodes_db:
        nodes.append(Node(
            id=node_db.id,
            name=node_db.name,
            latitude=node_db.latitude,
            longitude=node_db.longitude,
            voltage_kv=node_db.voltage_kv,
            iso_rto=node_db.iso_rto,
            type=node_db.type.value,
            capacity_mw=node_db.capacity_mw,
            owner=node_db.owner
        ))

    # Query branches that connect the returned nodes
    node_ids = [n.id for n in nodes_db]
    if node_ids:
        branches_db = db.query(grid_models.Branch).filter(
            grid_models.Branch.from_node_id.in_(node_ids),
            grid_models.Branch.to_node_id.in_(node_ids)
        ).limit(limit).all()

        branches = []
        for branch_db in branches_db:
            branches.append(Branch(
                id=branch_db.id,
                name=branch_db.name,
                from_node_id=branch_db.from_node_id,
                to_node_id=branch_db.to_node_id,
                capacity_mw=branch_db.capacity_mw,
                voltage_kv=branch_db.voltage_kv,
                is_hvdc=branch_db.is_hvdc or False,
                length_km=branch_db.length_km,
                status=branch_db.status.value,
                owner=branch_db.owner
            ))
    else:
        branches = []

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
    db: Session = Depends(get_db)
):
    """
    Get network nodes (substations, generators, load centers).
    """
    query = db.query(grid_models.Node)

    if node_type:
        try:
            node_type_enum = grid_models.NodeType[node_type.upper()]
            query = query.filter(grid_models.Node.type == node_type_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid node_type: {node_type}")

    if voltage_min:
        query = query.filter(grid_models.Node.voltage_kv >= voltage_min)

    if iso_rto:
        query = query.filter(grid_models.Node.iso_rto == iso_rto)

    nodes_db = query.limit(limit).all()

    return [Node(
        id=node.id,
        name=node.name,
        latitude=node.latitude,
        longitude=node.longitude,
        voltage_kv=node.voltage_kv,
        iso_rto=node.iso_rto,
        type=node.type.value,
        capacity_mw=node.capacity_mw,
        owner=node.owner
    ) for node in nodes_db]


@router.get("/lines", response_model=List[Branch])
async def get_transmission_lines(
    status: Optional[str] = Query(None, description="Filter by status: operational, planned, under_construction"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """
    Get transmission lines/branches.
    """
    query = db.query(grid_models.Branch)

    if status:
        try:
            status_enum = grid_models.BranchStatus[status.upper()]
            query = query.filter(grid_models.Branch.status == status_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if voltage_min:
        query = query.filter(grid_models.Branch.voltage_kv >= voltage_min)

    branches_db = query.limit(limit).all()

    return [Branch(
        id=branch.id,
        name=branch.name,
        from_node_id=branch.from_node_id,
        to_node_id=branch.to_node_id,
        capacity_mw=branch.capacity_mw,
        voltage_kv=branch.voltage_kv,
        is_hvdc=branch.is_hvdc or False,
        length_km=branch.length_km,
        status=branch.status.value,
        owner=branch.owner
    ) for branch in branches_db]


@router.get("/nearest-substation", response_model=Node)
async def find_nearest_substation(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db)
):
    """
    Find the nearest substation to a given location using PostGIS spatial query.
    Useful for project interconnection planning.
    """
    # Use PostGIS ST_Distance function to find nearest substation
    from sqlalchemy import text

    query = text("""
        SELECT id, name, latitude, longitude, voltage_kv, iso_rto, type, capacity_mw, owner,
               ST_Distance(geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) as distance_m
        FROM nodes
        WHERE type = 'substation'
        ORDER BY distance_m
        LIMIT 1
    """)

    result = db.execute(query, {"lat": latitude, "lon": longitude}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="No substations found in database")

    return Node(
        id=result[0],
        name=result[1],
        latitude=result[2],
        longitude=result[3],
        voltage_kv=result[4],
        iso_rto=result[5],
        type=result[6],
        capacity_mw=result[7],
        owner=result[8]
    )


@router.get("/congestion", response_model=List[CongestionData])
async def get_congestion_data(
    timestamp: Optional[datetime] = Query(None, description="Specific timestamp, defaults to latest"),
    branch_id: Optional[str] = Query(None, description="Filter by specific branch"),
    min_utilization: float = Query(0.0, ge=0, le=1, description="Minimum utilization to return")
):
    """
    Retrieve real-time or historical transmission congestion data.

    Note: This endpoint requires TimescaleDB integration for time-series data.
    Currently returns placeholder response. Will be implemented in Phase B.
    """
    # TODO: Query from TimescaleDB congestion_data table
    return []


@router.get("/transmission-capacity", response_model=List[TransmissionCapacity])
async def get_transmission_capacity(
    region: Optional[str] = Query(None, description="Filter by ISO/RTO region")
):
    """
    Retrieve available transmission capacity and potential upgrade options.

    Note: This endpoint requires optimization results integration.
    Currently returns placeholder response. Will be implemented in Phase B.
    """
    # TODO: Calculate from optimization results and network topology
    return []


@router.get("/nodes/{node_id}", response_model=Node)
async def get_node_details(
    node_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific node."""
    node = db.query(grid_models.Node).filter(grid_models.Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return Node(
        id=node.id,
        name=node.name,
        latitude=node.latitude,
        longitude=node.longitude,
        voltage_kv=node.voltage_kv,
        iso_rto=node.iso_rto,
        type=node.type.value,
        capacity_mw=node.capacity_mw,
        owner=node.owner
    )


@router.get("/branches/{branch_id}", response_model=Branch)
async def get_branch_details(
    branch_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific transmission branch."""
    branch = db.query(grid_models.Branch).filter(grid_models.Branch.id == branch_id).first()

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    return Branch(
        id=branch.id,
        name=branch.name,
        from_node_id=branch.from_node_id,
        to_node_id=branch.to_node_id,
        capacity_mw=branch.capacity_mw,
        voltage_kv=branch.voltage_kv,
        is_hvdc=branch.is_hvdc or False,
        length_km=branch.length_km,
        status=branch.status.value,
        owner=branch.owner
    )
