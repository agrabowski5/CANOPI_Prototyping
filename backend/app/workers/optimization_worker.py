"""
Celery Worker for CANOPI Optimization
Handles background optimization jobs using Celery task queue
"""

from celery import Celery, Task
from datetime import datetime
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

from app.services.canopi.optimizer_service import (
    CANOPIOptimizerService,
    OptimizationRequest,
    OptimizationResult
)

# Initialize Celery app
celery_app = Celery(
    'canopi_optimization',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)


# In-memory job storage (in production, use Redis or database)
job_store: Dict[str, Dict[str, Any]] = {}


class OptimizationTask(Task):
    """Base task with shared state"""

    def __init__(self):
        self._service = None

    @property
    def service(self):
        """Lazy load optimizer service"""
        if self._service is None:
            self._service = CANOPIOptimizerService(time_periods=24)
        return self._service


@celery_app.task(bind=True, base=OptimizationTask, name='run_canopi_optimization')
def run_canopi_optimization(
    self,
    job_id: str,
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Celery task to run CANOPI optimization

    Args:
        job_id: Unique job identifier
        request_data: Optimization request parameters

    Returns:
        Dictionary with optimization results
    """
    try:
        # Update job status
        update_job_status(job_id, 'running', 0.0, 0)

        # Create optimization request
        request = OptimizationRequest(
            planning_horizon_start=request_data['planning_horizon']['start'],
            planning_horizon_end=request_data['planning_horizon']['end'],
            carbon_target=request_data['carbon_target'],
            budget_limit=request_data['budget_limit'],
            contingency_level=request_data['contingency_level'],
            temporal_resolution=request_data['temporal_resolution'],
            reserve_margin=request_data.get('reserve_margin', 0.15),
            transmission_limit=request_data.get('transmission_limit', True),
            state_policies=request_data.get('state_policies', [])
        )

        # Progress callback
        def progress_callback(iteration: int, progress: float, info: Dict):
            """Update job progress"""
            update_job_status(
                job_id,
                'running',
                progress,
                iteration,
                info=info
            )

            # Update Celery task state
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': iteration,
                    'total': 50,
                    'progress': progress,
                    'status': 'Running optimization...'
                }
            )

        # Run optimization
        print(f"Starting optimization for job {job_id}")
        result = self.service.run_optimization(
            request=request,
            progress_callback=progress_callback,
            max_iterations=50,
            simplified=True  # Use simplified for MVP
        )

        # Convert result to dict
        result_dict = result.to_dict()

        # Update job with results
        update_job_status(
            job_id,
            'completed',
            1.0,
            result.iterations,
            results=result_dict
        )

        print(f"Optimization complete for job {job_id}")

        return {
            'job_id': job_id,
            'status': 'completed',
            'results': result_dict
        }

    except Exception as e:
        # Handle errors
        error_msg = str(e)
        print(f"Optimization failed for job {job_id}: {error_msg}")

        update_job_status(
            job_id,
            'failed',
            0.0,
            0,
            error=error_msg
        )

        return {
            'job_id': job_id,
            'status': 'failed',
            'error': error_msg
        }


def update_job_status(
    job_id: str,
    status: str,
    progress: float,
    iteration: int,
    info: Dict = None,
    results: Dict = None,
    error: str = None
):
    """
    Update job status in storage

    Args:
        job_id: Job identifier
        status: Job status (queued, running, completed, failed)
        progress: Progress fraction (0-1)
        iteration: Current iteration
        info: Additional info (bounds, gap, etc)
        results: Optimization results (if completed)
        error: Error message (if failed)
    """
    if job_id not in job_store:
        job_store[job_id] = {
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'current_iteration': iteration,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    else:
        job_store[job_id].update({
            'status': status,
            'progress': progress,
            'current_iteration': iteration,
            'updated_at': datetime.utcnow()
        })

    if info:
        job_store[job_id]['info'] = info

    if results:
        job_store[job_id]['results'] = results
        job_store[job_id]['completed_at'] = datetime.utcnow()

    if error:
        job_store[job_id]['error'] = error
        job_store[job_id]['failed_at'] = datetime.utcnow()


def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get job status from storage

    Args:
        job_id: Job identifier

    Returns:
        Job status dictionary
    """
    return job_store.get(job_id)


def get_job_results(job_id: str) -> Dict[str, Any]:
    """
    Get job results from storage

    Args:
        job_id: Job identifier

    Returns:
        Job results dictionary
    """
    job = job_store.get(job_id)
    if job and job['status'] == 'completed':
        return job.get('results')
    return None


# Celery periodic tasks (optional)
@celery_app.task(name='cleanup_old_jobs')
def cleanup_old_jobs():
    """Clean up old completed jobs (runs periodically)"""
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=7)
    jobs_to_remove = []

    for job_id, job in job_store.items():
        if job['status'] in ['completed', 'failed']:
            completed_at = job.get('completed_at') or job.get('failed_at')
            if completed_at and completed_at < cutoff:
                jobs_to_remove.append(job_id)

    for job_id in jobs_to_remove:
        del job_store[job_id]

    print(f"Cleaned up {len(jobs_to_remove)} old jobs")


# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-jobs': {
        'task': 'cleanup_old_jobs',
        'schedule': 3600.0,  # Run every hour
    },
}


if __name__ == '__main__':
    # For testing: run a single optimization
    test_job_id = "test-job-123"
    test_request = {
        'planning_horizon': {'start': 2024, 'end': 2030},
        'carbon_target': 0.8,
        'budget_limit': 50e9,
        'contingency_level': 'n-1',
        'temporal_resolution': 'hourly',
        'reserve_margin': 0.15,
        'transmission_limit': True,
        'state_policies': []
    }

    print("Testing optimization worker...")
    result = run_canopi_optimization(test_job_id, test_request)
    print(f"Result: {result['status']}")
