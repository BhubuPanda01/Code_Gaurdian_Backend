"""
GitHub Repository Analysis Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, JobResponse
from app.controllers.analyze_controller import create_analysis_job, get_job_by_id
from typing import Optional

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"],
    responses={404: {"description": "Not found"}},
)


@router.post("/github", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
def analyze_github_repo(
    analyze_request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a GitHub repository
    
    This endpoint:
    1. Validates the GitHub URL
    2. Creates a job in the database
    3. Pushes the job to the queue
    4. Returns the job ID
    
    Args:
        analyze_request: Analysis request containing GitHub URL
        db: Database session
        
    Returns:
        AnalyzeResponse: Job ID and status
        
    Raises:
        HTTPException: If validation fails or job creation fails
    """
    try:
        success, job_id, message = create_analysis_job(db, analyze_request)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return AnalyzeResponse(
            job_id=job_id,
            status="pending",
            message="Analysis job created and queued for processing"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating analysis job: {str(e)}"
        )


@router.get("/job/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a GitHub analysis job
    
    Args:
        job_id: Job ID
        db: Database session
        
    Returns:
        JobResponse: Job details including status and results
        
    Raises:
        HTTPException: If job not found
    """
    try:
        result = get_job_by_id(db, job_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['message']
            )
        
        job = result['job']
        return JobResponse(**job)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job: {str(e)}"
        )
