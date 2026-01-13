"""
Grid topology models for electrical transmission network data.

Models represent the physical electrical grid infrastructure:
- Interconnections: Major grid synchronous regions (Eastern, Western, Texas)
- Nodes: Substations, generators, and load centers
- Branches: Transmission lines connecting nodes
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography, Geometry
import enum
import uuid

from .base import Base


class InterconnectionType(str, enum.Enum):
    """Three major US electrical interconnections."""
    EASTERN = "Eastern"
    WESTERN = "Western"
    TEXAS = "Texas"


class NodeType(str, enum.Enum):
    """Types of network nodes."""
    SUBSTATION = "substation"
    GENERATOR = "generator"
    LOAD = "load"


class BranchStatus(str, enum.Enum):
    """Transmission line operational status."""
    OPERATIONAL = "operational"
    PLANNED = "planned"
    UNDER_CONSTRUCTION = "under_construction"
    RETIRED = "retired"


class Interconnection(Base):
    """
    Major electrical interconnections in North America.

    The US has three major interconnections that operate asynchronously:
    - Eastern Interconnection: East of the Rocky Mountains
    - Western Interconnection: Western states + parts of Canada/Mexico
    - Texas Interconnection: Most of Texas (ERCOT)
    """
    __tablename__ = "interconnections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    type = Column(Enum(InterconnectionType), nullable=False)
    description = Column(String(500))

    # Relationships
    nodes = relationship("Node", back_populates="interconnection", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Node(Base):
    """
    Network nodes representing substations, generators, and load centers.

    Each node has:
    - Geographic location (stored as PostGIS Geography for spatial queries)
    - Voltage level (kV)
    - Type (substation, generator, load)
    - Interconnection membership
    """
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)

    # Geographic location - using Geography for accurate distance calculations
    # SRID 4326 = WGS84 (standard GPS coordinates)
    geography = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    # Separate lat/lon for convenience (auto-populated from geography)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Electrical characteristics
    voltage_kv = Column(Integer, nullable=False)  # Nominal voltage level
    type = Column(Enum(NodeType), nullable=False, default=NodeType.SUBSTATION)

    # ISO/RTO and interconnection
    iso_rto = Column(String(50))  # CAISO, PJM, ERCOT, MISO, NYISO, ISO-NE, SPP
    interconnection_id = Column(String, ForeignKey("interconnections.id"), nullable=False)

    # Optional attributes
    owner = Column(String(255))  # Utility or owner
    capacity_mw = Column(Float)  # For generators: nameplate capacity

    # Metadata
    data_source = Column(String(100))  # HIFLD, EIA-860, etc.
    external_id = Column(String(100))  # Original ID from data source

    # Relationships
    interconnection = relationship("Interconnection", back_populates="nodes")
    outgoing_branches = relationship("Branch", foreign_keys="Branch.from_node_id", back_populates="from_node")
    incoming_branches = relationship("Branch", foreign_keys="Branch.to_node_id", back_populates="to_node")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Node {self.name} ({self.voltage_kv}kV) at ({self.latitude:.4f}, {self.longitude:.4f})>"


class Branch(Base):
    """
    Transmission lines connecting network nodes.

    Each branch represents a physical transmission line with:
    - From/to nodes
    - Capacity (MW)
    - Voltage level (kV)
    - Geographic route (stored as LineString for visualization)
    - Electrical parameters (impedance, reactance)
    """
    __tablename__ = "branches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))

    # Connectivity
    from_node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    to_node_id = Column(String, ForeignKey("nodes.id"), nullable=False)

    # Geographic route - LineString connecting the nodes
    geometry = Column(Geometry(geometry_type='LINESTRING', srid=4326))

    # Electrical characteristics
    voltage_kv = Column(Integer, nullable=False)
    capacity_mw = Column(Float, nullable=False)  # Thermal capacity
    length_km = Column(Float)  # Physical length

    # Electrical parameters for power flow analysis
    resistance_pu = Column(Float)  # Per-unit resistance
    reactance_pu = Column(Float)   # Per-unit reactance
    susceptance_pu = Column(Float)  # Per-unit susceptance

    # Operational status
    status = Column(Enum(BranchStatus), nullable=False, default=BranchStatus.OPERATIONAL)
    is_hvdc = Column(Boolean, default=False)  # HVDC line vs AC

    # Metadata
    data_source = Column(String(100))
    external_id = Column(String(100))
    owner = Column(String(255))

    # Relationships
    from_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_branches")
    to_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_branches")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Branch {self.name} ({self.voltage_kv}kV, {self.capacity_mw}MW) {self.from_node_id} → {self.to_node_id}>"


# Spatial indices are created in the Alembic migration for optimal query performance
