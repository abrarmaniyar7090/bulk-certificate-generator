# Bulk Certificate Generator

A backend API for generating completion certificates in bulk using Python, FastAPI, SQLite, SQLAlchemy, and ReportLab.

## Overview

The Bulk Certificate Generator allows a client to submit a single request containing multiple recipients.

The application:

1. Validates the request data.
2. Creates a generation job.
3. Creates a certificate record for each recipient.
4. Processes certificates in the background.
5. Generates an individual PDF certificate for each valid recipient.
6. Tracks the status and progress of the generation job.
7. Continues processing if one certificate fails.
8. Provides a download endpoint for successfully generated certificates.

## Technology Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* ReportLab
* Pytest
* Uvicorn

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── certificate_service.py
│   └── processing_services.py
│
├── storage/
│   └── certificates/
│
├── tests/
│   └── tests/
│       └── test_generation_job.py
│
├── venv/
├── certificates.db
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone or create the project

Open the project directory in VS Code.

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## Run the Application

Start the FastAPI server using:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Health Check

### Request

```http
GET /health
```

### Response

```json
{
  "status": "ok"
}
```

## Create a Generation Job

A single request can contain multiple recipients.

### Request

```http
POST /api/v1/generation-jobs
```

Example request body:

```json
{
  "event_name": "Python Bootcamp 2026",
  "recipients": [
    {
      "name": "Abrar Hussain",
      "email": "abrar@example.com",
      "course_name": "Python Fundamentals"
    },
    {
      "name": "John Doe",
      "email": "john@example.com",
      "course_name": "Python Fundamentals"
    },
    {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "course_name": "Python Fundamentals"
    }
  ]
}
```

### Response

```json
{
  "job_id": 1,
  "status": "pending",
  "total_count": 3
}
```

The API accepts all recipients in one request instead of requiring one API request per certificate.

## Check Generation Job Status

### Request

```http
GET /api/v1/generation-jobs/{job_id}
```

Example:

```http
GET /api/v1/generation-jobs/1
```

### Response

```json
{
  "job_id": 1,
  "event_name": "Python Bootcamp 2026",
  "status": "completed",
  "total_count": 3,
  "success_count": 3,
  "failure_count": 0,
  "completed_count": 3,
  "certificates": [
    {
      "id": 1,
      "recipient_name": "Abrar Hussain",
      "recipient_email": "abrar@example.com",
      "course_name": "Python Fundamentals",
      "status": "completed",
      "error_message": null,
      "download_url": "/api/v1/certificates/1/download"
    }
  ]
}
```

### Job Statuses

The application supports the following job states:

* `pending` — Job has been created but processing has not started.
* `processing` — Certificates are currently being generated.
* `completed` — All certificates were generated successfully.
* `completed_with_errors` — Some certificates succeeded and some failed.
* `failed` — All certificate generations failed.

## Certificate Statuses

Each certificate is tracked independently.

Possible statuses are:

* `pending`
* `processing`
* `completed`
* `failed`

This allows the application to identify exactly which recipients succeeded or failed.

## Download a Certificate

After a certificate has been successfully generated, it can be downloaded using:

```http
GET /api/v1/certificates/{certificate_id}/download
```

Example:

```http
GET /api/v1/certificates/1/download
```

The API returns the generated PDF file.

## Validation

The API validates recipient information using Pydantic.

For example, an invalid email address:

```json
{
  "name": "Test User",
  "email": "invalid-email",
  "course_name": "Python Fundamentals"
}
```

returns HTTP:

```text
422 Unprocessable Entity
```

The API also validates minimum and maximum lengths for recipient names, course names, and event names.

At least one recipient is required for a generation job.

## Error Handling

Certificate generation is handled independently for each recipient.

If one certificate fails, the exception is captured and stored against that certificate.

Processing then continues with the remaining recipients.

For example:

```text
Recipient 1 → completed
Recipient 2 → failed
Recipient 3 → completed
```

The final job status becomes:

```text
completed_with_errors
```

The job counters would be:

```text
total_count     = 3
success_count   = 2
failure_count   = 1
completed_count = 3
```

This prevents a single failed certificate from stopping the entire bulk operation.

## Certificate Storage

Generated PDF files are stored in:

```text
storage/certificates/
```

Files are named using their certificate database ID:

```text
certificate_1.pdf
certificate_2.pdf
certificate_3.pdf
```

The generated file path is stored in the database so that the download endpoint can locate the certificate.

## Database Design

The application uses two main tables.

### GenerationJob

Stores information about the bulk generation request.

Important fields include:

* `id`
* `event_name`
* `status`
* `total_count`
* `success_count`
* `failure_count`
* `created_at`

### Certificate

Stores information about each individual certificate.

Important fields include:

* `id`
* `job_id`
* `recipient_name`
* `recipient_email`
* `course_name`
* `status`
* `file_path`
* `error_message`
* `created_at`

The relationship is:

```text
GenerationJob
      │
      ├── Certificate
      ├── Certificate
      └── Certificate
```

One generation job can therefore contain many certificates.

## Background Processing

The API uses FastAPI `BackgroundTasks` to process certificate generation after the generation job is created.

The flow is:

```text
Client
   │
   │ POST generation request
   ▼
FastAPI API
   │
   ├── Validate request
   ├── Create generation job
   ├── Create certificate records
   │
   ▼
Background Processing
   │
   ├── Generate Certificate 1
   ├── Generate Certificate 2
   ├── Generate Certificate 3
   │
   ▼
Update Database
   │
   ▼
Client checks job status
```

For this assignment, FastAPI BackgroundTasks keeps the implementation simple.

For a production-scale system with very large workloads, a dedicated task queue such as Celery with Redis or another message broker could be introduced.

## Testing

The project uses Pytest.

Run all tests using:

```powershell
pytest
```

The test suite covers:

1. Generation job creation
2. Invalid recipient email validation
3. Certificate generation and job completion
4. Individual certificate failure handling
5. Certificate retrieval/download

Expected result:

```text
5 passed
```

## Design Decisions

### Bulk API

The API accepts multiple recipients in one request.

This avoids making a separate API call for every certificate.

### Relational Database

SQLite was selected for the assignment because it is lightweight and requires no separate database server.

SQLAlchemy provides the ORM layer and keeps database operations separate from API logic.

For production, PostgreSQL or another enterprise relational database could be used.

### Separate Job and Certificate Records

A generation job represents the complete bulk request, while each certificate represents an individual recipient.

This makes it possible to track individual success and failure states.

### Failure Isolation

Each certificate is generated inside its own `try/except` block.

Therefore, a failure for one recipient does not terminate the entire job.

### PDF Generation

ReportLab is used to generate PDF certificates from a predefined certificate layout.

The certificate generation logic is isolated in:

```text
app/certificate_service.py
```

This makes the PDF generation logic easier to modify independently from the API layer.

## Future Improvements

For a production-ready implementation, the following improvements could be considered:

* PostgreSQL instead of SQLite
* Celery/RQ or another distributed task queue
* Redis or another message broker
* Object storage such as Amazon S3 for generated PDFs
* Authentication and authorization
* API rate limiting
* Structured logging
* Retry mechanism for transient certificate-generation failures
* Database migrations using Alembic
* More comprehensive integration tests
* Email notification after bulk generation
* Pagination for large certificate lists
* Monitoring and metrics
* Docker containerization

## Summary

The application provides a complete bulk certificate generation workflow:

```text
Submit recipients
       ↓
Validate input
       ↓
Create generation job
       ↓
Create certificate records
       ↓
Background processing
       ↓
Generate individual PDFs
       ↓
Track success/failure
       ↓
Check job progress
       ↓
Download completed certificates
```

The implementation is designed to be simple enough for the assignment while demonstrating important backend concepts such as API design, validation, relational data modeling, background processing, error isolation, file generation, and automated testing.
