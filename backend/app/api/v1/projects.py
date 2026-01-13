"""
Projects API endpoints
Handles CRUD operations for energy projects (solar, wind, storage, data centers)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response


class ProjectLocation(BaseModel):
    """Geographic location of a project"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class ProjectParameters(BaseModel):
    """Project-specific parameters"""
    capex: float = Field(..., gt=0, description="Capital expenditure (USD)")
    opex: float = Field(..., gt=0, description="Annual operating expenditure (USD/year)")
    availability_factor: Optional[float] = Field(None, ge=0, le=1, description="Capacity factor (0-1)")
    lifetime_years: Optional[int] = Field(25, gt=0, description="Project lifetime in years")


class ProjectCreate(BaseModel):
    """Request model for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., description="solar, wind, storage, gas, nuclear, datacenter")
    capacity_mw: float = Field(..., gt=0, description="Capacity in MW")
    location: ProjectLocation
    parameters: ProjectParameters
    status: str = Field("proposed", description="proposed, planning, approved, construction, operational")


class Project(ProjectCreate):
    """Response model for a project"""
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# In-memory storage for MVP (will be replaced with database)
projects_db: dict[UUID, Project] = {}


@router.options("/")
async def options_projects():
    """Handle OPTIONS preflight for CORS"""
    return {}


@router.post("/", response_model=Project, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new energy project"""
    new_project = Project(**project.model_dump())
    projects_db[new_project.id] = new_project
    return new_project


@router.get("/", response_model=List[Project])
async def list_projects(
    type: Optional[str] = Query(None, description="Filter by project type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all projects with optional filtering"""
    projects = list(projects_db.values())

    # Apply filters
    if type:
        projects = [p for p in projects if p.type == type]
    if status:
        projects = [p for p in projects if p.status == status]

    # Apply pagination
    return projects[offset:offset + limit]


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: UUID):
    """Get a specific project by ID"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: UUID, project: ProjectCreate):
    """Update an existing project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    updated_project = Project(**project.model_dump(), id=project_id)
    updated_project.updated_at = datetime.utcnow()
    projects_db[project_id] = updated_project
    return updated_project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID):
    """Delete a project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[project_id]
    return None


@router.get("/{project_id}/optimization-impact")
async def get_optimization_impact(project_id: UUID):
    """
    Analyze the impact of this project on the grid
    Returns: Cost impact, grid integration requirements, optimal sizing
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # TODO: Run simplified optimization analysis
    # For now, return mock data
    return {
        "project_id": project_id,
        "system_cost_impact": {
            "baseline_cost": 18700000000,
            "with_project_cost": 18500000000,
            "savings": 200000000,
            "savings_percent": 1.07
        },
        "grid_integration": {
            "nearest_substation_km": 12.5,
            "transmission_upgrade_required": True,
            "estimated_interconnection_cost": 45000000,
            "estimated_interconnection_time_months": 24
        },
        "optimal_sizing": {
            "recommended_capacity_mw": project.capacity_mw * 1.2,
            "capacity_factor": 0.28,
            "annual_generation_gwh": project.capacity_mw * 1.2 * 8760 * 0.28 / 1000
        },
        "economics": {
            "lcoe_usd_per_mwh": 35.50,
            "npv_20yr": 150000000,
            "irr": 0.125
        }
    }
