# CANOPI Energy Planning Platform

A web-based tool for grid strategy planning for large-scale energy asset developers and consumers, powered by the CANOPI optimization algorithm.

## Overview

CANOPI (Contingency-Aware Nodal Optimal Power Investments) is a state-of-the-art optimization platform that helps:

- **Energy Asset Developers** (NextEra, Avangrid, etc.): Identify optimal locations for renewable energy projects and plan transmission expansion
- **Large Energy Consumers** (Google, Microsoft, AWS data centers): Site new facilities with reliable, clean energy access

### Key Features

- 🌍 **Interactive Earth Map**: Real-time visualization of transmission networks and optimization results
- ⚡ **Advanced Optimization**: CANOPI algorithm with full n-1 contingency analysis
- 📍 **Project Geotagging**: Drag-and-drop energy projects onto the map
- 📊 **Scenario Planning**: Compare multiple expansion strategies
- 🔄 **Real-time Updates**: Watch optimization progress live
- 📈 **Comprehensive Analytics**: Hourly operations, cost breakdowns, reliability metrics

## Technology Stack

- **Frontend**: React + TypeScript + Mapbox GL JS
- **Backend**: Python (FastAPI)
- **Optimization**: CANOPI algorithm (from MIT research paper)
- **Database**: PostgreSQL + PostGIS + TimescaleDB
- **Deployment**: Docker + Kubernetes (AWS/GCP)

## Project Structure

```
CANOPI_Prototyping/
├── frontend/              # React web application
├── backend/               # FastAPI backend server
├── canopi_engine/         # CANOPI optimization algorithm
├── data_pipelines/        # Data ingestion and processing
├── infrastructure/        # DevOps and deployment configs
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Docker Desktop
- Mapbox account (free tier available)
- Gurobi license (academic/trial available)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd CANOPI_Prototyping

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Mapbox API key and other configs

# Start databases with Docker
cd ..
docker-compose up -d

# Run migrations
cd backend
alembic upgrade head
```

### Running the Application

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm start
```

Navigate to http://localhost:3000 to see the application.

## Development Roadmap

### MVP Phase (Weeks 1-10)

- ✅ **Week 1-2**: Core map interface with project pins
- 🔄 **Week 3-6**: CANOPI algorithm implementation
- 📅 **Week 7-8**: API integration and real-time optimization
- 📅 **Week 9-10**: Polish and demo preparation

See [docs/architecture/implementation-plan.md](docs/architecture/implementation-plan.md) for detailed roadmap.

## Research Foundation

This platform implements the CANOPI algorithm from the research paper:

> Lee, T., & Sun, A. (2025). CANOPI: Contingency-Aware Nodal Optimal Power Investments with High Temporal Resolution. *arXiv preprint arXiv:2510.03484*.

Key algorithmic innovations:
- Bundle method with interleaved contingency generation
- Minimal cycle basis for efficient DC power flow
- Transmission correction via fixed-point iteration
- Handles 20 billion potential contingency constraints

## Data Sources

The platform integrates data from:
- **Grid Topology**: EIA-860, utility filings
- **Market Data**: CAISO, PJM, ERCOT (ISO/RTO APIs)
- **Weather & Renewables**: NOAA, NASA, NREL
- **Geospatial**: USGS, EPA

## Contributing

This is a research and development project. For questions or collaboration inquiries, please contact the development team.

## License

[To be determined]

## Citation

If you use this platform in your research, please cite:

```bibtex
@article{lee2025canopi,
  title={CANOPI: Contingency-Aware Nodal Optimal Power Investments with High Temporal Resolution},
  author={Lee, Thomas and Sun, Andy},
  journal={arXiv preprint arXiv:2510.03484},
  year={2025}
}
```

## Acknowledgments

- MIT Future Energy Systems Center for research support
- Original CANOPI algorithm developed by Thomas Lee and Andy Sun at MIT

---

**Status**: 🚧 Under Active Development

Last updated: January 2026
