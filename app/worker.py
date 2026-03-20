"""Worker process for handling analysis jobs from queue."""
import time
import json
import shutil
from app.utils.queue import job_queue
from app.controllers.analyze_controller import update_job_status
from app.utils.repository_analyzer import clone_repository, analyze_repository, generate_optimization_recommendations
from app.models.job import JobStatus
from app.database import SessionLocal


def process_next_job():
    job_data = job_queue.get_next_job()
    if not job_data:
        return False

    job_id = job_data.get("job_id")
    db_job_id = job_data.get("database_job_id")

    job_queue.mark_job_processing(job_id, job_data)

    repo_dir = None
    with SessionLocal() as db:
        try:
            update_job_status(db, db_job_id, JobStatus.PROCESSING)

            # Clone repository
            repo_dir = clone_repository(job_data["github_url"])

            # Static repository analysis
            analysis_summary = analyze_repository(repo_dir)

            # AI-like optimization suggestions
            suggestions = generate_optimization_recommendations(analysis_summary)

            result_payload = {
                "summary": analysis_summary,
                "suggestions": suggestions,
            }

            update_job_status(db, db_job_id, JobStatus.COMPLETED, result=json.dumps(result_payload))
            job_queue.mark_job_completed(job_id, result_payload)
            print(f"[worker] job {job_id} completed")

        except Exception as e:
            error_message = str(e)
            update_job_status(db, db_job_id, JobStatus.FAILED, error_message=error_message)
            job_queue.mark_job_failed(job_id, error_message)
            print(f"[worker] job {job_id} failed: {error_message}")

        finally:
            if repo_dir:
                shutil.rmtree(repo_dir, ignore_errors=True)

    return True


def run_worker(poll_interval: float = 5.0):
    print("[worker] Starting Code Guardian analysis worker...")
    try:
        while True:
            processed = process_next_job()
            if not processed:
                time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("[worker] Shutdown requested, exiting.")


if __name__ == "__main__":
    run_worker()
