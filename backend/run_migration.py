"""
Run database migration to create grid topology tables.

This script manually executes the migration SQL without requiring Alembic.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Execute the grid topology migration."""
    print("Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("Enabling PostGIS extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()

        print("Creating ENUM types...")
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE interconnectiontype AS ENUM ('Eastern', 'Western', 'Texas');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))

        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE nodetype AS ENUM ('substation', 'generator', 'load');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))

        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE branchstatus AS ENUM ('operational', 'planned', 'under_construction', 'retired');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        conn.commit()

        print("Creating interconnections table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS interconnections (
                id VARCHAR PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                type interconnectiontype NOT NULL,
                description VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.commit()

        print("Creating nodes table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nodes (
                id VARCHAR PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                geography GEOGRAPHY(POINT, 4326) NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                voltage_kv INTEGER NOT NULL,
                type nodetype NOT NULL,
                iso_rto VARCHAR(50),
                interconnection_id VARCHAR NOT NULL REFERENCES interconnections(id),
                owner VARCHAR(255),
                capacity_mw FLOAT,
                data_source VARCHAR(100),
                external_id VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.commit()

        print("Creating spatial index on nodes...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_nodes_geography ON nodes USING GIST (geography)
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_nodes_voltage_kv ON nodes (voltage_kv)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes (type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_nodes_iso_rto ON nodes (iso_rto)"))
        conn.commit()

        print("Creating branches table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS branches (
                id VARCHAR PRIMARY KEY,
                name VARCHAR(255),
                from_node_id VARCHAR NOT NULL REFERENCES nodes(id),
                to_node_id VARCHAR NOT NULL REFERENCES nodes(id),
                geometry GEOMETRY(LINESTRING, 4326),
                voltage_kv INTEGER NOT NULL,
                capacity_mw FLOAT NOT NULL,
                length_km FLOAT,
                resistance_pu FLOAT,
                reactance_pu FLOAT,
                susceptance_pu FLOAT,
                status branchstatus NOT NULL,
                is_hvdc BOOLEAN,
                data_source VARCHAR(100),
                external_id VARCHAR(100),
                owner VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            )
        """))
        conn.commit()

        print("Creating spatial index on branches...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_branches_geometry ON branches USING GIST (geometry)
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_branches_voltage_kv ON branches (voltage_kv)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_branches_status ON branches (status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_branches_from_to ON branches (from_node_id, to_node_id)"))
        conn.commit()

        print("\n✅ Migration completed successfully!")
        print("Grid topology tables created:")
        print("  - interconnections")
        print("  - nodes (with spatial index)")
        print("  - branches (with spatial index)")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
