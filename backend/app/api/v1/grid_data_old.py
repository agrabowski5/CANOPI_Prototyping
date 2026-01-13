"""
Grid Data API endpoints
Provides access to transmission network topology, congestion data, and capacity information
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

router = APIRouter()

# Models


class Node(BaseModel):
    """Electrical node/bus in the transmission network"""
    id: UUID
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    voltage_kv: int
    iso_rto: str = Field(..., description="ISO/RTO region (CAISO, PJM, ERCOT, etc.)")
    type: str = Field("bus", description="bus, substation, generator")


class Branch(BaseModel):
    """Transmission line or transformer"""
    id: UUID
    from_node_id: UUID
    to_node_id: UUID
    capacity_mw: float
    impedance: float
    voltage_kv: int
    is_hvdc: bool = False
    length_km: Optional[float] = None


class NetworkTopology(BaseModel):
    """Complete network topology"""
    nodes: List[Node]
    branches: List[Branch]
    metadata: dict = Field(default_factory=dict)


class CongestionData(BaseModel):
    """Real-time or historical congestion information"""
    timestamp: datetime
    branch_id: UUID
    flow_mw: float
    capacity_mw: float
    utilization: float = Field(..., ge=0, le=1, description="Flow / Capacity")
    lmp_price: Optional[float] = Field(None, description="Locational Marginal Price ($/MWh)")
    shadow_price: Optional[float] = Field(None, description="Shadow price on transmission constraint")


class TransmissionCapacity(BaseModel):
    """Available transmission capacity and upgrade options"""
    branch_id: UUID
    current_capacity_mw: float
    available_capacity_mw: float
    upgrade_options: List[dict] = Field(default_factory=list, description="Possible upgrade capacities and costs")


# Sample data for Western Interconnection (subset)
# In production, this would come from database
SAMPLE_NODES = [
    Node(
        id=uuid4(),
        name="Palo Verde",
        latitude=33.3881,
        longitude=-112.8598,
        voltage_kv=500,
        iso_rto="WECC",
        type="generator"
    ),
    Node(
        id=uuid4(),
        name="Midway",
        latitude=34.8153,
        longitude=-118.8270,
        voltage_kv=500,
        iso_rto="CAISO",
        type="substation"
    ),
    Node(
        id=uuid4(),
        name="Malin",
        latitude=42.0095,
        longitude=-121.4197,
        voltage_kv=500,
        iso_rto="CAISO",
        type="substation"
    ),
]


@router.get("/topology", response_model=NetworkTopology)
async def get_network_topology(
    region: Optional[str] = Query(None, description="Filter by ISO/RTO region"),
    voltage_min: Optional[int] = Query(None, description="Minimum voltage level (kV)"),
    limit: int = Query(100, ge=1, le=10000)
):
    """
    Retrieve transmission network topology
    Returns nodes (buses/substations) and branches (transmission lines)
    """
    nodes = SAMPLE_NODES.copy()

    # Apply filters
    if region:
        nodes = [n for n in nodes if n.iso_rto == region]
    if voltage_min:
        nodes = [n for n in nodes if n.voltage_kv >= voltage_min]

    # Limit results
    nodes = nodes[:limit]

    # Create sample branches connecting nodes
    branches = []
    for i in range(len(nodes) - 1):
        branches.append(Branch(
            id=uuid4(),
            from_node_id=nodes[i].id,
            to_node_id=nodes[i + 1].id,
            capacity_mw=2000.0,
            impedance=0.025,
            voltage_kv=500,
            is_hvdc=False,
            length_km=150.0
        ))

    return NetworkTopology(
        nodes=nodes,
        branches=branches,
        metadata={
            "total_nodes": len(nodes),
            "total_branches": len(branches),
            "region": region or "all",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/congestion", response_model=List[CongestionData])
async def get_congestion_data(
    timestamp: Optional[datetime] = Query(None, description="Specific timestamp, defaults to latest"),
    branch_id: Optional[UUID] = Query(None, description="Filter by specific branch"),
    min_utilization: float = Query(0.0, ge=0, le=1, description="Minimum utilization to return")
):
    """
    Retrieve real-time or historical transmission congestion data
    Shows power flows, utilization, and prices
    """
    # TODO: Query from TimescaleDB
    # For now, return mock data

    timestamp = timestamp or datetime.utcnow()

    # Generate sample congestion data
    congestion_data = []
    for node in SAMPLE_NODES[:2]:
        congestion_data.append(CongestionData(
            timestamp=timestamp,
            branch_id=uuid4(),
            flow_mw=1650.0,
            capacity_mw=2000.0,
            utilization=0.825,
            lmp_price=45.50,
            shadow_price=12.30
        ))

    # Apply filters
    if branch_id:
        congestion_data = [c for c in congestion_data if c.branch_id == branch_id]
    if min_utilization:
        congestion_data = [c for c in congestion_data if c.utilization >= min_utilization]

    return congestion_data


@router.get("/transmission-capacity", response_model=List[TransmissionCapacity])
async def get_transmission_capacity(
    region: Optional[str] = Query(None, description="Filter by ISO/RTO region")
):
    """
    Retrieve available transmission capacity and potential upgrade options
    Useful for planning new project interconnections
    """
    # TODO: Calculate from optimization results and network topology

    return [
        TransmissionCapacity(
            branch_id=uuid4(),
            current_capacity_mw=2000.0,
            available_capacity_mw=350.0,
            upgrade_options=[
                {
                    "capacity_add_mw": 500,
                    "cost_usd": 75000000,
                    "timeline_months": 18,
                    "technology": "reconductoring"
                },
                {
                    "capacity_add_mw": 2000,
                    "cost_usd": 300000000,
                    "timeline_months": 36,
                    "technology": "new_line"
                }
            ]
        )
    ]


@router.get("/nodes/{node_id}", response_model=Node)
async def get_node_details(node_id: UUID):
    """Get detailed information about a specific node"""
    # TODO: Query from database
    node = next((n for n in SAMPLE_NODES if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.get("/branches/{branch_id}", response_model=Branch)
async def get_branch_details(branch_id: UUID):
    """Get detailed information about a specific transmission branch"""
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Branch not found")
