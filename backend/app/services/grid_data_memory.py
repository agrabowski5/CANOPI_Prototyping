"""
In-memory Grid Data Service

Loads grid topology data from JSON files and provides it in memory without requiring a database.
This is useful for development/testing without PostgreSQL.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class InMemoryGridDataService:
    """Service for loading and querying grid data from JSON files in memory."""

    def __init__(self):
        """Initialize with empty data."""
        self.interconnection: Optional[Dict[str, Any]] = None
        self.nodes: List[Dict[str, Any]] = []
        self.branches: List[Dict[str, Any]] = []
        self._loaded = False

    def load_from_files(self, nodes_file: Path, branches_file: Path):
        """Load grid data from JSON files (appends to existing data)."""
        with open(nodes_file, 'r') as f:
            nodes_data = json.load(f)

        with open(branches_file, 'r') as f:
            branches_data = json.load(f)

        # Store interconnection info (will be last one loaded if multiple)
        interconnection = nodes_data.get('interconnection')
        if self.interconnection is None:
            self.interconnection = interconnection

        # Append nodes and branches
        new_nodes = nodes_data.get('nodes', [])
        new_branches = branches_data.get('branches', [])

        self.nodes.extend(new_nodes)
        self.branches.extend(new_branches)
        self._loaded = True

        print(f"Loaded {len(new_nodes)} nodes and {len(new_branches)} branches from {nodes_file.name}")

    def get_topology(
        self,
        region: Optional[str] = None,
        voltage_min: Optional[int] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get network topology with filtering.

        Args:
            region: Filter by ISO/RTO
            voltage_min: Minimum voltage level
            min_lat, max_lat, min_lon, max_lon: Bounding box
            limit: Maximum results

        Returns:
            Dict with 'nodes' and 'branches' lists
        """
        nodes = self.nodes.copy()

        # Apply filters
        if region:
            nodes = [n for n in nodes if n.get('iso_rto') == region]
        if voltage_min:
            nodes = [n for n in nodes if n.get('voltage_kv', 0) >= voltage_min]
        if min_lat and max_lat and min_lon and max_lon:
            nodes = [
                n for n in nodes
                if min_lat <= n.get('latitude', 0) <= max_lat
                and min_lon <= n.get('longitude', 0) <= max_lon
            ]

        # Limit results
        nodes = nodes[:limit]

        # Filter branches to only include those connecting visible nodes
        node_ids = {n['id'] for n in nodes}
        branches = [
            b for b in self.branches
            if b.get('from_node_id') in node_ids and b.get('to_node_id') in node_ids
        ][:limit]

        return {
            'nodes': nodes,
            'branches': branches
        }

    def get_nodes(
        self,
        node_type: Optional[str] = None,
        voltage_min: Optional[int] = None,
        iso_rto: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get nodes with filtering."""
        nodes = self.nodes.copy()

        if node_type:
            nodes = [n for n in nodes if n.get('type') == node_type]
        if voltage_min:
            nodes = [n for n in nodes if n.get('voltage_kv', 0) >= voltage_min]
        if iso_rto:
            nodes = [n for n in nodes if n.get('iso_rto') == iso_rto]

        return nodes[:limit]

    def get_branches(
        self,
        status: Optional[str] = None,
        voltage_min: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get branches with filtering."""
        branches = self.branches.copy()

        if status:
            branches = [b for b in branches if b.get('status') == status]
        if voltage_min:
            branches = [b for b in branches if b.get('voltage_kv', 0) >= voltage_min]

        return branches[:limit]

    def find_nearest_substation(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, Any]]:
        """Find the nearest substation to a location."""
        substations = [n for n in self.nodes if n.get('type') == 'substation']

        if not substations:
            return None

        # Simple Euclidean distance (not geodesic, but good enough for rough approximation)
        def distance(node):
            dlat = node['latitude'] - latitude
            dlon = node['longitude'] - longitude
            return dlat**2 + dlon**2

        return min(substations, key=distance)

    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node by ID."""
        return next((n for n in self.nodes if n['id'] == node_id), None)

    def get_branch_by_id(self, branch_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific branch by ID."""
        return next((b for b in self.branches if b['id'] == branch_id), None)


# Global instance
_grid_service: Optional[InMemoryGridDataService] = None


def get_grid_service() -> InMemoryGridDataService:
    """Get or create the global grid data service instance."""
    global _grid_service

    if _grid_service is None:
        _grid_service = InMemoryGridDataService()

        # In Docker: /app/app/services/grid_data_memory.py
        # .parent.parent.parent = /app (the working directory)
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data_pipelines" / "grid_data"

        # Load all available interconnections (US, Canada, Mexico)
        interconnections = [
            ("western_interconnection", "Western Interconnection"),
            ("eastern_interconnection", "Eastern Interconnection"),
            ("texas_interconnection", "Texas (ERCOT) Interconnection"),
            ("canadian_grid", "Canadian Grid"),
            ("mexico_grid", "Mexican Grid"),
        ]

        loaded_count = 0

        # First try to load sample data (from load_sample_data.py)
        sample_nodes_file = data_dir / "sample_nodes.json"
        sample_branches_file = data_dir / "sample_branches.json"

        if sample_nodes_file.exists() and sample_branches_file.exists():
            _grid_service.load_from_files(sample_nodes_file, sample_branches_file)
            print(f"✓ Loaded sample grid data from CSV conversion")
            loaded_count += 1

        # Then load interconnection data
        for prefix, name in interconnections:
            nodes_file = data_dir / f"{prefix}_nodes.json"
            branches_file = data_dir / f"{prefix}_branches.json"

            if nodes_file.exists() and branches_file.exists():
                _grid_service.load_from_files(nodes_file, branches_file)
                loaded_count += 1
            else:
                print(f"Note: {name} data not found, skipping")

        # Load cross-regional DC ties
        dc_ties_file = data_dir / "cross_regional_dc_ties.json"
        if dc_ties_file.exists():
            with open(dc_ties_file, 'r') as f:
                dc_data = json.load(f)
            dc_nodes = dc_data.get('dc_tie_nodes', [])
            dc_branches = dc_data.get('dc_tie_branches', [])
            _grid_service.nodes.extend(dc_nodes)
            _grid_service.branches.extend(dc_branches)
            print(f"Loaded {len(dc_nodes)} DC tie nodes and {len(dc_branches)} DC tie branches")

        # Load Mexico-US interconnections
        mx_us_file = data_dir / "mexico_us_interconnections.json"
        if mx_us_file.exists():
            with open(mx_us_file, 'r') as f:
                mx_us_data = json.load(f)
            us_border_nodes = mx_us_data.get('us_border_nodes', [])
            cross_border = mx_us_data.get('cross_border_interconnections', [])
            _grid_service.nodes.extend(us_border_nodes)
            _grid_service.branches.extend(cross_border)
            print(f"Loaded {len(us_border_nodes)} US border nodes and {len(cross_border)} cross-border interconnections")

        if loaded_count == 0:
            print(f"Warning: No grid data files found at {data_dir}")
        else:
            print(f"Total grid data: {len(_grid_service.nodes)} nodes, {len(_grid_service.branches)} branches")

    return _grid_service
