"""
Analyze Controller - Business Logic for GitHub Repository Analysis
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.job import Job, JobStatus
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.utils.github import validate_github_url, normalize_github_url
from app.utils.queue import job_queue
import json
import uuid


def create_analysis_job(db: Session, analyze_request: AnalyzeRequest) -> tuple[bool, str, str]:
    """
    Create a new GitHub repository analysis job
    
    Args:
        db: Database session
        analyze_request: Analysis request data
        
    Returns:
        tuple: (success, job_id, message)
    """
    try:
        github_url = analyze_request.github_url
        
        # Validate GitHub URL
        is_valid, repository_name, error_message = validate_github_url(github_url)
        if not is_valid:
            return False, "", error_message
        
        # Normalize GitHub URL
        normalized_url = normalize_github_url(github_url)
        
        job_id = str(uuid.uuid4())

        # Create job in database
        db_job = Job(
            job_id=job_id,
            github_url=normalized_url,
            repository_name=repository_name,
            status=JobStatus.PENDING
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        # Push job to queue with both db and external job identifiers
        job_data = {
            'github_url': normalized_url,
            'repository_name': repository_name,
            'database_job_id': db_job.id,
            'job_id': db_job.job_id
        }
        
        job_queue.push_job(job_data)
        
        return True, db_job.job_id, "Analysis job created successfully"
    
    except IntegrityError:
        db.rollback()
        return False, "", "Error creating analysis job - database constraint violation"
    except Exception as e:
        db.rollback()
        return False, "", f"Error creating analysis job: {str(e)}"


def get_job_by_id(db: Session, job_id: int) -> dict:
    """
    Get job details by ID
    
    Args:
        db: Database session
        job_id: Job ID
        
    Returns:
        dict: Job details or error message
    """
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return {
                'success': False,
                'message': f'Job with ID {job_id} not found'
            }
        
        return {
            'success': True,
            'job': {
                'job_id': job.job_id,
                'github_url': job.github_url,
                'repository_name': job.repository_name,
                'status': job.status.value,
                'result': job.result,
                'error_message': job.error_message,
                'created_at': job.created_at,
                'updated_at': job.updated_at
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving job: {str(e)}'
        }


def get_job_result(db: Session, job_id: int) -> dict:
    """Get only result payload for a job"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {'success': False, 'message': f'Job with ID {job_id} not found'}

        result_payload = None
        if job.result:
            try:
                result_payload = json.loads(job.result)
            except (ValueError, TypeError):
                result_payload = {'raw': job.result}

        return {
            'success': True,
            'data': {
                'job_id': job.job_id,
                'status': job.status.value,
                'result': result_payload,
                'error_message': job.error_message,
            }
        }
    except Exception as e:
        return {'success': False, 'message': f'Error retrieving job result: {str(e)}'}


def update_job_status(db: Session, job_id: int, status: JobStatus, result: str = None, error_message: str = None):
    """
    Update job status
    
    Args:
        db: Database session
        job_id: Job ID
        status: New status
        result: Optional result data (JSON string)
        error_message: Optional error message
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            if result:
                job.result = result
            if error_message:
                job.error_message = error_message
            db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error updating job status: {str(e)}")
