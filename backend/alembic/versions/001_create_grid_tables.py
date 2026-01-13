"""Create grid topology tables

Revision ID: 001_create_grid_tables
Revises:
Create Date: 2026-01-09

This migration creates the foundation for storing US electrical grid topology:
- Interconnections (Eastern, Western, Texas)
- Nodes (substations, generators, load centers)
- Branches (transmission lines)

Uses PostGIS for geospatial queries and visualization.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '001_create_grid_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create grid topology tables with PostGIS support."""

    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    # Create ENUM types
    op.execute("""
        CREATE TYPE interconnectiontype AS ENUM ('Eastern', 'Western', 'Texas')
    """)

    op.execute("""
        CREATE TYPE nodetype AS ENUM ('substation', 'generator', 'load')
    """)

    op.execute("""
        CREATE TYPE branchstatus AS ENUM ('operational', 'planned', 'under_construction', 'retired')
    """)

    # Create interconnections table
    op.create_table(
        'interconnections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', postgresql.ENUM('Eastern', 'Western', 'Texas', name='interconnectiontype'), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create nodes table
    op.create_table(
        'nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('geography', geoalchemy2.types.Geography(
            geometry_type='POINT',
            srid=4326,
            from_text='ST_GeogFromText',
            name='geography'
        ), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('voltage_kv', sa.Integer(), nullable=False),
        sa.Column('type', postgresql.ENUM('substation', 'generator', 'load', name='nodetype'), nullable=False),
        sa.Column('iso_rto', sa.String(length=50), nullable=True),
        sa.Column('interconnection_id', sa.String(), nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('capacity_mw', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(length=100), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['interconnection_id'], ['interconnections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create spatial index on nodes geography
    op.execute("""
        CREATE INDEX idx_nodes_geography ON nodes USING GIST (geography)
    """)

    # Create index on nodes voltage_kv for filtering
    op.create_index('idx_nodes_voltage_kv', 'nodes', ['voltage_kv'])

    # Create index on nodes type
    op.create_index('idx_nodes_type', 'nodes', ['type'])

    # Create index on nodes iso_rto
    op.create_index('idx_nodes_iso_rto', 'nodes', ['iso_rto'])

    # Create branches table
    op.create_table(
        'branches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('from_node_id', sa.String(), nullable=False),
        sa.Column('to_node_id', sa.String(), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(
            geometry_type='LINESTRING',
            srid=4326,
            from_text='ST_GeomFromEWKT',
            name='geometry'
        ), nullable=True),
        sa.Column('voltage_kv', sa.Integer(), nullable=False),
        sa.Column('capacity_mw', sa.Float(), nullable=False),
        sa.Column('length_km', sa.Float(), nullable=True),
        sa.Column('resistance_pu', sa.Float(), nullable=True),
        sa.Column('reactance_pu', sa.Float(), nullable=True),
        sa.Column('susceptance_pu', sa.Float(), nullable=True),
        sa.Column('status', postgresql.ENUM('operational', 'planned', 'under_construction', 'retired', name='branchstatus'), nullable=False),
        sa.Column('is_hvdc', sa.Boolean(), nullable=True),
        sa.Column('data_source', sa.String(length=100), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['from_node_id'], ['nodes.id'], ),
        sa.ForeignKeyConstraint(['to_node_id'], ['nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create spatial index on branches geometry
    op.execute("""
        CREATE INDEX idx_branches_geometry ON branches USING GIST (geometry)
    """)

    # Create index on branches voltage_kv
    op.create_index('idx_branches_voltage_kv', 'branches', ['voltage_kv'])

    # Create index on branches status
    op.create_index('idx_branches_status', 'branches', ['status'])

    # Create composite index for node connectivity queries
    op.create_index('idx_branches_from_to', 'branches', ['from_node_id', 'to_node_id'])


def downgrade() -> None:
    """Drop grid topology tables and PostGIS types."""

    # Drop tables
    op.drop_table('branches')
    op.drop_table('nodes')
    op.drop_table('interconnections')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS branchstatus')
    op.execute('DROP TYPE IF EXISTS nodetype')
    op.execute('DROP TYPE IF EXISTS interconnectiontype')

    # Note: We don't drop the PostGIS extension as other tables might use it
