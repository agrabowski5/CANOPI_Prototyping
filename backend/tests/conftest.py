"""
Pytest configuration and fixtures for CANOPI backend tests
"""
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Solar Farm",
        "type": "solar",
        "latitude": 34.05,
        "longitude": -118.25,
        "capacity_mw": 100,
        "capex_per_mw": 1500000,
        "opex_per_mw": 20000,
    }


@pytest.fixture
def sample_grid_node_data():
    """Sample grid node data for testing"""
    return {
        "name": "Test Substation",
        "latitude": 34.10,
        "longitude": -118.30,
        "voltage_kv": 230,
        "type": "substation",
    }


@pytest.fixture
def sample_optimization_config():
    """Sample optimization configuration for testing"""
    return {
        "horizon_years": 10,
        "discount_rate": 0.07,
        "reserve_margin": 0.15,
        "carbon_price": 50.0,
        "transmission_cost_per_mw_km": 1000.0,
        "renewable_target": 0.5,
        "contingency_analysis": True,
    }
