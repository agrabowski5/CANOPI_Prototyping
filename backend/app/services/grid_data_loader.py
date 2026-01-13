"""
Grid Data Loader Service

Loads US electrical grid topology data from JSON files into the PostgreSQL database.
Handles interconnections, nodes (substations/generators), and branches (transmission lines).
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point, LineString

from app.models import Interconnection, Node, Branch, InterconnectionType, NodeType, BranchStatus
from app.core.config import settings


class GridDataLoader:
    """Service for loading grid topology data from JSON files into database."""

    def __init__(self, database_url: str = None):
        """
        Initialize the data loader.

        Args:
            database_url: Optional database URL override. Uses settings if not provided.
        """
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def load_from_files(
        self,
        nodes_file: Path,
        branches_file: Path,
        clear_existing: bool = False
    ) -> Dict[str, int]:
        """
        Load grid data from JSON files.

        Args:
            nodes_file: Path to nodes JSON file
            branches_file: Path to branches JSON file
            clear_existing: If True, delete all existing data before loading

        Returns:
            Dictionary with counts: {'interconnections': 1, 'nodes': 42, 'branches': 38}
        """
        with self.SessionLocal() as session:
            if clear_existing:
                self._clear_existing_data(session)

            # Load and parse files
            with open(nodes_file, 'r') as f:
                nodes_data = json.load(f)

            with open(branches_file, 'r') as f:
                branches_data = json.load(f)

            # Load interconnection
            interconnection = self._load_interconnection(session, nodes_data.get('interconnection'))

            # Load nodes
            node_count = self._load_nodes(session, nodes_data.get('nodes', []), interconnection.id)

            # Load branches
            branch_count = self._load_branches(session, branches_data.get('branches', []))

            session.commit()

            return {
                'interconnections': 1,
                'nodes': node_count,
                'branches': branch_count
            }

    def _clear_existing_data(self, session: Session) -> None:
        """Delete all existing grid data."""
        session.query(Branch).delete()
        session.query(Node).delete()
        session.query(Interconnection).delete()
        session.commit()
        print("Cleared existing grid data")

    def _load_interconnection(self, session: Session, interconnection_data: Dict[str, Any]) -> Interconnection:
        """
        Load or update an interconnection.

        Args:
            session: Database session
            interconnection_data: Interconnection data from JSON

        Returns:
            Interconnection model instance
        """
        interconnection_id = interconnection_data['id']

        # Check if exists
        existing = session.query(Interconnection).filter_by(id=interconnection_id).first()
        if existing:
            print(f"Interconnection '{interconnection_data['name']}' already exists, skipping")
            return existing

        interconnection = Interconnection(
            id=interconnection_id,
            name=interconnection_data['name'],
            type=InterconnectionType[interconnection_data['type'].upper()],
            description=interconnection_data.get('description')
        )
        session.add(interconnection)
        session.flush()

        print(f"Loaded interconnection: {interconnection.name}")
        return interconnection

    def _load_nodes(self, session: Session, nodes_data: List[Dict[str, Any]], interconnection_id: str) -> int:
        """
        Load network nodes.

        Args:
            session: Database session
            nodes_data: List of node data from JSON
            interconnection_id: ID of parent interconnection

        Returns:
            Number of nodes loaded
        """
        count = 0

        for node_data in nodes_data:
            # Check if exists
            existing = session.query(Node).filter_by(id=node_data['id']).first()
            if existing:
                print(f"Node '{node_data['name']}' already exists, skipping")
                continue

            # Create geography point from coordinates
            lat = node_data['latitude']
            lon = node_data['longitude']
            point = Point(lon, lat)  # Note: PostGIS uses (lon, lat) order
            geography = from_shape(point, srid=4326)

            node = Node(
                id=node_data['id'],
                name=node_data['name'],
                geography=geography,
                latitude=lat,
                longitude=lon,
                voltage_kv=node_data['voltage_kv'],
                type=NodeType[node_data['type'].upper()],
                iso_rto=node_data.get('iso_rto'),
                interconnection_id=interconnection_id,
                owner=node_data.get('owner'),
                capacity_mw=node_data.get('capacity_mw'),
                data_source=node_data.get('data_source'),
                external_id=node_data.get('external_id')
            )
            session.add(node)
            count += 1

        session.flush()
        print(f"Loaded {count} nodes")
        return count

    def _load_branches(self, session: Session, branches_data: List[Dict[str, Any]]) -> int:
        """
        Load transmission branches.

        Args:
            session: Database session
            branches_data: List of branch data from JSON

        Returns:
            Number of branches loaded
        """
        count = 0

        for branch_data in branches_data:
            # Check if exists
            existing = session.query(Branch).filter_by(id=branch_data['id']).first()
            if existing:
                print(f"Branch '{branch_data['name']}' already exists, skipping")
                continue

            # Get from and to nodes to create LineString geometry
            from_node = session.query(Node).filter_by(id=branch_data['from_node_id']).first()
            to_node = session.query(Node).filter_by(id=branch_data['to_node_id']).first()

            if not from_node or not to_node:
                print(f"Warning: Branch '{branch_data['name']}' references non-existent nodes, skipping")
                continue

            # Create LineString from node coordinates
            line = LineString([
                (from_node.longitude, from_node.latitude),
                (to_node.longitude, to_node.latitude)
            ])
            geometry = from_shape(line, srid=4326)

            branch = Branch(
                id=branch_data['id'],
                name=branch_data.get('name'),
                from_node_id=branch_data['from_node_id'],
                to_node_id=branch_data['to_node_id'],
                geometry=geometry,
                voltage_kv=branch_data['voltage_kv'],
                capacity_mw=branch_data['capacity_mw'],
                length_km=branch_data.get('length_km'),
                resistance_pu=branch_data.get('resistance_pu'),
                reactance_pu=branch_data.get('reactance_pu'),
                susceptance_pu=branch_data.get('susceptance_pu'),
                status=BranchStatus[branch_data.get('status', 'operational').upper()],
                is_hvdc=branch_data.get('is_hvdc', False),
                data_source=branch_data.get('data_source'),
                external_id=branch_data.get('external_id'),
                owner=branch_data.get('owner')
            )
            session.add(branch)
            count += 1

        session.flush()
        print(f"Loaded {count} branches")
        return count


def load_western_interconnection(clear_existing: bool = False) -> Dict[str, int]:
    """
    Convenience function to load Western Interconnection data.

    Args:
        clear_existing: If True, delete all existing data before loading

    Returns:
        Dictionary with counts of loaded entities
    """
    # Get paths to data files
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "data_pipelines" / "grid_data"

    nodes_file = data_dir / "western_interconnection_nodes.json"
    branches_file = data_dir / "western_interconnection_branches.json"

    if not nodes_file.exists():
        raise FileNotFoundError(f"Nodes file not found: {nodes_file}")
    if not branches_file.exists():
        raise FileNotFoundError(f"Branches file not found: {branches_file}")

    loader = GridDataLoader()
    return loader.load_from_files(nodes_file, branches_file, clear_existing=clear_existing)


if __name__ == "__main__":
    """Load Western Interconnection data when run as script."""
    print("Loading Western Interconnection grid data...")
    results = load_western_interconnection(clear_existing=True)
    print(f"\nData loaded successfully:")
    print(f"  Interconnections: {results['interconnections']}")
    print(f"  Nodes: {results['nodes']}")
    print(f"  Branches: {results['branches']}")
