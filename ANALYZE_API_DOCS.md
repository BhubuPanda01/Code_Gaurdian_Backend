# GitHub Repository Analysis API

## Overview
The GitHub Repository Analysis API provides endpoints to analyze GitHub repositories. This API validates GitHub URLs, creates analysis jobs in the database, queues them for processing, and tracks job status.

## API Endpoints

### 1. Analyze GitHub Repository
**Endpoint:** `POST /analyze/github`

**Description:** Submit a GitHub repository URL for analysis

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repository"
}
```

**Response (201 Created):**
```json
{
  "job_id": "1",
  "status": "pending",
  "message": "Analysis job created and queued for processing"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "URL must be a GitHub repository URL"
}
```

**Validation Rules:**
- URL must start with `http://` or `https://`
- URL must contain `github.com`
- Must follow GitHub URL format: `https://github.com/owner/repo`
- Owner and repository names must contain only alphanumeric characters, hyphens, and underscores

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/analyze/github" \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/facebook/react"}'
```

---

### 2. Get Job Status
**Endpoint:** `GET /analyze/job/{job_id}`

**Description:** Retrieve the status and details of an analysis job

**Path Parameters:**
- `job_id` (integer): The unique job identifier returned from the analyze endpoint

**Response (200 OK):**
```json
{
  "job_id": 1,
  "github_url": "https://github.com/facebook/react",
  "repository_name": "facebook/react",
  "status": "pending",
  "result": null,
  "error_message": null,
  "created_at": "2024-03-16T10:30:00",
  "updated_at": "2024-03-16T10:30:00"
}
```

**Job Status Values:**
- `pending` - Job is waiting to be processed
- `processing` - Job is currently being analyzed
- `completed` - Analysis completed successfully
- `failed` - Analysis failed with an error

**Error Response (404 Not Found):**
```json
{
  "detail": "Job with ID 999 not found"
}
```

**Example Usage:**
```bash
curl -X GET "http://localhost:8000/analyze/job/1"
```

---

## Workflow

### Client-Side Flow
1. User clicks "Analyze" button on frontend UI
2. Frontend calls `POST /analyze/github` with GitHub URL
3. Backend validates URL, creates job in database, queues job, returns job_id
4. Frontend receives job_id and displays it to user
5. Frontend periodically calls `GET /analyze/job/{job_id}` to check status
6. When status changes to "completed" or "failed", display results to user

### Backend Flow
```
GitHub URL → Validation → Database Creation → Queue → Return job_id
                                    ↓
                            Job Processing Worker
                                    ↓
                            Update Database Status
```

---

## Technical Details

### Job Model
The Job model stores:
- `id`: Primary key
- `github_url`: Normalized GitHub repository URL
- `repository_name`: Extracted owner/repo format
- `status`: Current job status (enum)
- `result`: Analysis results (JSON string)
- `error_message`: Error details if failed
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Queue System
Jobs are queued using an in-memory queue system:
- Jobs are pushed to the queue after database creation
- Workers consume jobs from the queue
- In production, consider replacing with Celery, RabbitMQ, or Redis

### GitHub URL Validation
The validation process:
1. Checks for http/https protocol
2. Verifies github.com domain
3. Extracts owner and repository names
4. Validates naming conventions
5. Normalizes URL format

---

## Environment Setup

### Database
Ensure your PostgreSQL database URL is set in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/code_guardian
```

### Running the Backend
```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate

# Run the FastAPI server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

---

## Future Enhancements

1. **Job Queue Workers**: Implement background workers using Celery to process jobs
2. **GitHub Integration**: Clone and analyze actual repositories
3. **Analysis Reports**: Generate detailed code analysis reports
4. **Status Polling**: WebSocket support for real-time job status updates
5. **Job History**: Implement pagination and filtering for job lists
6. **Error Handling**: Enhanced error messages and retry logic

---

## Error Codes

| Status Code | Meaning |
|-------------|---------|
| 201 | Job created successfully |
| 400 | Invalid GitHub URL format |
| 404 | Job not found |
| 500 | Internal server error |

---

## File Structure
```
app/
├── models/
│   ├── job.py          # Job database model
│   └── __init__.py
├── schemas/
│   ├── analyze.py      # Request/Response schemas
│   └── __init__.py
├── controllers/
│   ├── analyze_controller.py  # Business logic
│   └── __init__.py
├── routes/
│   ├── analyze_routes.py      # API endpoints
│   └── __init__.py
├── utils/
│   ├── github.py       # GitHub URL validation
│   ├── queue.py        # Job queue system
│   └── __init__.py
└── main.py             # Application entry point
```
