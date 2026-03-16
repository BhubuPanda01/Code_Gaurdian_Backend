"""
Job Queue Management System
In production, consider using Celery, RabbitMQ, or Redis
This is a simple in-memory queue implementation for development
"""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque


class JobQueue:
    """Simple in-memory job queue"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobQueue, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.queue = deque()
        self.jobs_in_progress: Dict[str, Any] = {}
        self._initialized = True
    
    def push_job(self, job_data: Dict[str, Any]) -> str:
        """
        Add a job to the queue
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            str: Unique job ID
        """
        job_id = str(uuid.uuid4())
        job_entry = {
            'job_id': job_id,
            **job_data,
            'enqueued_at': datetime.now()
        }
        self.queue.append(job_entry)
        return job_id
    
    def get_next_job(self) -> Optional[Dict[str, Any]]:
        """
        Get the next job from the queue
        
        Returns:
            dict: Job data or None if queue is empty
        """
        if self.queue:
            return self.queue.popleft()
        return None
    
    def get_job_status(self, job_id: str) -> Optional[str]:
        """
        Get job status from in-memory tracking
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            str: Job status or None if not found
        """
        if job_id in self.jobs_in_progress:
            return self.jobs_in_progress[job_id].get('status')
        return None
    
    def mark_job_processing(self, job_id: str, job_data: Dict[str, Any]):
        """
        Mark a job as being processed
        
        Args:
            job_id: Unique job identifier
            job_data: Job information
        """
        self.jobs_in_progress[job_id] = {
            **job_data,
            'status': 'processing',
            'started_at': datetime.now()
        }
    
    def mark_job_completed(self, job_id: str, result: Any):
        """
        Mark a job as completed
        
        Args:
            job_id: Unique job identifier
            result: Job result data
        """
        if job_id in self.jobs_in_progress:
            self.jobs_in_progress[job_id]['status'] = 'completed'
            self.jobs_in_progress[job_id]['result'] = result
            self.jobs_in_progress[job_id]['completed_at'] = datetime.now()
    
    def mark_job_failed(self, job_id: str, error: str):
        """
        Mark a job as failed
        
        Args:
            job_id: Unique job identifier
            error: Error message
        """
        if job_id in self.jobs_in_progress:
            self.jobs_in_progress[job_id]['status'] = 'failed'
            self.jobs_in_progress[job_id]['error'] = error
            self.jobs_in_progress[job_id]['failed_at'] = datetime.now()
    
    def queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)


# Global queue instance
job_queue = JobQueue()
