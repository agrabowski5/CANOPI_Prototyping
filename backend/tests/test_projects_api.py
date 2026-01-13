"""
Test cases for Projects API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestProjectsAPI:
    """Test suite for /api/v1/projects endpoints"""

    def test_create_project(self, client: TestClient, sample_project_data):
        """Test creating a new project"""
        response = client.post("/api/v1/projects/", json=sample_project_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_project_data["name"]
        assert data["type"] == sample_project_data["type"]
        assert data["capacity_mw"] == sample_project_data["capacity_mw"]
        assert "id" in data
        assert "created_at" in data

    def test_get_projects_empty(self, client: TestClient):
        """Test getting projects when none exist"""
        response = client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_projects_list(self, client: TestClient, sample_project_data):
        """Test getting list of projects"""
        # Create a project first
        client.post("/api/v1/projects/", json=sample_project_data)

        # Get all projects
        response = client.get("/api/v1/projects/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == sample_project_data["name"]

    def test_get_project_by_id(self, client: TestClient, sample_project_data):
        """Test getting a specific project by ID"""
        # Create a project
        create_response = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == sample_project_data["name"]

    def test_get_project_not_found(self, client: TestClient):
        """Test getting a non-existent project"""
        response = client.get("/api/v1/projects/999999")

        assert response.status_code == 404

    def test_update_project(self, client: TestClient, sample_project_data):
        """Test updating a project"""
        # Create a project
        create_response = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]

        # Update the project
        update_data = {"capacity_mw": 150, "name": "Updated Solar Farm"}
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["capacity_mw"] == 150
        assert data["name"] == "Updated Solar Farm"

    def test_delete_project(self, client: TestClient, sample_project_data):
        """Test deleting a project"""
        # Create a project
        create_response = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]

        # Delete the project
        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404

    def test_update_project_coordinates(self, client: TestClient, sample_project_data):
        """Test updating project coordinates"""
        # Create a project
        create_response = client.post("/api/v1/projects/", json=sample_project_data)
        project_id = create_response.json()["id"]

        # Update coordinates
        new_coords = {"latitude": 35.0, "longitude": -119.0}
        response = client.patch(
            f"/api/v1/projects/{project_id}/coordinates",
            json=new_coords
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location"]["lat"] == 35.0
        assert data["location"]["lon"] == -119.0

    def test_bulk_create_projects(self, client: TestClient, sample_project_data):
        """Test bulk creating multiple projects"""
        projects = [
            sample_project_data,
            {**sample_project_data, "name": "Solar Farm 2", "latitude": 35.0},
            {**sample_project_data, "name": "Solar Farm 3", "latitude": 36.0},
        ]

        response = client.post("/api/v1/projects/bulk", json={"projects": projects})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["name"] == "Test Solar Farm"
        assert data[1]["name"] == "Solar Farm 2"
        assert data[2]["name"] == "Solar Farm 3"

    def test_filter_projects_by_type(self, client: TestClient, sample_project_data):
        """Test filtering projects by type"""
        # Create solar project
        client.post("/api/v1/projects/", json=sample_project_data)

        # Create wind project
        wind_project = {**sample_project_data, "name": "Wind Farm", "type": "wind"}
        client.post("/api/v1/projects/", json=wind_project)

        # Filter by solar
        response = client.get("/api/v1/projects/?type=solar")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "solar"

    def test_pagination(self, client: TestClient, sample_project_data):
        """Test pagination of projects list"""
        # Create 5 projects
        for i in range(5):
            project = {**sample_project_data, "name": f"Project {i}"}
            client.post("/api/v1/projects/", json=project)

        # Get first page (limit 2)
        response = client.get("/api/v1/projects/?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Get second page
        response = client.get("/api/v1/projects/?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_create_project_invalid_data(self, client: TestClient):
        """Test creating project with invalid data"""
        invalid_data = {
            "name": "Test",
            # Missing required fields
        }

        response = client.post("/api/v1/projects/", json=invalid_data)

        assert response.status_code == 422  # Validation error
