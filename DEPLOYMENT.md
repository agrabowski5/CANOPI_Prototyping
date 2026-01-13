# CANOPI Production Deployment Guide

## Quick Start

The CANOPI Energy Planning Platform is now configured for production deployment with Docker.

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB of RAM available
- Ports 80, 8000, 5432, 6379, and 5555 available

### Start Production Services

```bash
# Using the startup script
./start-production.sh

# Or manually
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Access Points

Once running, you can access:

- **Frontend (Web App)**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **Flower (Celery Monitor)**: http://localhost:5555

### Service Status

Check all services:
```bash
docker-compose -f docker-compose.prod.yml ps
```

View logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Stop Services

```bash
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose -f docker-compose.prod.yml down -v
```

## Configuration

### Environment Variables

Production environment variables are configured in:
- `.env.prod` - Backend/database configuration
- `frontend/.env.production` - Frontend configuration

**IMPORTANT:** Before deploying to production:

1. **Change default passwords** in `.env.prod`:
   ```
   POSTGRES_PASSWORD=your-secure-password
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

2. **Add Mapbox token** in `frontend/.env.production`:
   ```
   REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
   ```

3. **Update CORS origins** in `.env.prod` to match your domain:
   ```
   BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
   ```

## Architecture

The production deployment includes:

### Services

1. **Frontend (Nginx + React)**
   - Port: 80
   - Serves the React application
   - Proxies API requests to backend
   - Health check: http://localhost/health

2. **Backend (FastAPI + Uvicorn)**
   - Port: 8000
   - REST API with 4 workers
   - Health check: http://localhost:8000/health

3. **PostgreSQL + PostGIS**
   - Port: 5432
   - Main database for grid topology and spatial data
   - Data persisted in Docker volume

4. **Redis**
   - Port: 6379
   - Caching and Celery message broker
   - Data persisted in Docker volume

5. **Celery Worker** (MVP - needs dependencies)
   - Background task processing for optimization jobs
   - Note: Requires additional Python packages for CANOPI engine

6. **Flower** (MVP - needs dependencies)
   - Port: 5555
   - Celery monitoring dashboard
   - Note: Requires additional Python packages

### Volumes

Data is persisted in Docker volumes:
- `postgres_data` - Database data
- `redis_data` - Redis data

## Scaling

### Horizontal Scaling

Scale specific services:
```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale celery workers to 4 instances
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=4
```

### Production Deployment

For production deployment to cloud platforms:

1. **Kubernetes**: Convert to Kubernetes manifests using Kompose
2. **AWS ECS**: Use AWS ECS task definitions
3. **Google Cloud Run**: Deploy containers individually
4. **Azure Container Instances**: Use ACI deployment

## Monitoring

### Health Checks

All services include health checks:
- Frontend: HTTP check on port 80
- Backend: HTTP check on /health endpoint
- PostgreSQL: pg_isready command
- Redis: redis-cli ping command

### Logs

View real-time logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

Export logs:
```bash
docker-compose -f docker-compose.prod.yml logs > canopi-logs.txt
```

## Troubleshooting

### Frontend not accessible
```bash
# Check if frontend container is running
docker-compose -f docker-compose.prod.yml ps frontend

# Check frontend logs
docker-compose -f docker-compose.prod.yml logs frontend
```

### Backend API errors
```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
docker-compose -f docker-compose.prod.yml logs backend
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Connect to database
docker exec -it canopi_postgres_prod psql -U canopi -d canopi
```

### Celery worker not starting
The Celery worker requires additional dependencies for the CANOPI optimization engine. To fix:
1. Add `networkx`, `gurobipy`, and other CANOPI dependencies to `backend/requirements.txt`
2. Rebuild the images: `docker-compose -f docker-compose.prod.yml build`
3. Restart services: `docker-compose -f docker-compose.prod.yml up -d`

## Security Considerations

- [ ] Change all default passwords
- [ ] Use HTTPS in production (add SSL certificates to Nginx)
- [ ] Enable firewall rules to restrict access
- [ ] Use secrets management for sensitive credentials
- [ ] Regular security updates of Docker images
- [ ] Implement rate limiting on API endpoints
- [ ] Enable authentication and authorization

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker exec canopi_postgres_prod pg_dump -U canopi canopi > backup.sql

# Restore backup
docker exec -i canopi_postgres_prod psql -U canopi canopi < backup.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v canopi_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## Performance Tuning

### Backend
- Adjust worker count in Dockerfile CMD: `--workers 8`
- Configure Gunicorn for production workloads
- Enable caching for frequently accessed data

### Database
- Tune PostgreSQL settings for your workload
- Create indexes on frequently queried columns
- Enable connection pooling

### Frontend
- Enable Nginx gzip compression (already configured)
- Set appropriate cache headers for static assets
- Use CDN for global distribution

## Support

For issues and questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review documentation: http://localhost:8000/api/docs
- GitHub Issues: https://github.com/yourusername/CANOPI_Prototyping/issues
