# Bulk Certificate Generator

A backend API for generating completion certificates in bulk using **Python, FastAPI, SQLAlchemy, SQLite, and ReportLab**.

The application accepts multiple recipients in a single request, validates the input, creates a generation job, processes certificates independently in the background, tracks generation status, handles individual failures, and provides PDF download endpoints.

## Features

* Bulk certificate generation through a single API request
* Request validation using Pydantic
* Background certificate processing using FastAPI `BackgroundTasks`
* Individual certificate status tracking
* Job-level progress and success/failure counters
* Failure isolation — one failed certificate does not stop the remaining certificates
* PDF certificate generation using ReportLab
* Generated certificate download endpoint
* SQLite relational database using SQLAlchemy ORM
* Automated API and service-level tests using Pytest
* Interactive API documentation using Swagger/OpenAPI

## Technology Stack

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Backend programming language            |
| FastAPI    | REST API framework                      |
| SQLAlchemy | ORM and database operations             |
| SQLite     | Relational database                     |
| Pydantic   | Request validation and response schemas |
| ReportLab  | PDF certificate generation              |
| Pytest     | Automated testing                       |
| Uvicorn    | ASGI server                             |

## Architecture

```text
Client
  |
  | POST /api/v1/generation-jobs
  | Multiple recipients
  v
FastAPI
  |
  +-- Validate request
  |
  +-- Create GenerationJob
  |
  +-- Create Certificate records
  |
  +-- Start background processing
  |
  v
Background Processing
  |
  +-- Generate Certificate 1
  +-- Generate Certificate 2
  +-- Generate Certificate 3
  |
  v
SQLite Database
  |
  +-- Update job status
  +-- Update certificate status
  +-- Store file paths/errors
  |
  v
Client
  |
  +-- Check job status
  |
  +-- Download completed certificates
```

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
├── tests/
│   └── tests/
│       └── test_generation_job.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── test_certificate.py
```

Generated PDFs are stored locally under:

```text
storage/certificates/
```

The virtual environment and local SQLite database are intentionally excluded from Git using `.gitignore`.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/abrarmaniyar7090/bulk-certificate-generator.git
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## Run the Application

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint                                         | Purpose                                     |
| ------ | ------------------------------------------------ | ------------------------------------------- |
| `GET`  | `/health`                                        | Check API health                            |
| `POST` | `/api/v1/generation-jobs`                        | Create a bulk certificate generation job    |
| `GET`  | `/api/v1/generation-jobs/{job_id}`               | Check job progress and certificate statuses |
| `GET`  | `/api/v1/certificates/{certificate_id}/download` | Download a generated certificate            |

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

Example:

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

The API accepts all recipients in one request instead of requiring one API call per certificate.

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

| Status                  | Meaning                                             |
| ----------------------- | --------------------------------------------------- |
| `pending`               | Job has been created but processing has not started |
| `processing`            | Certificates are currently being generated          |
| `completed`             | All certificates were generated successfully        |
| `completed_with_errors` | Some certificates succeeded and some failed         |
| `failed`                | All certificate generations failed                  |

## Certificate Statuses

Each certificate is tracked independently.

Possible statuses:

```text
pending
processing
completed
failed
```

This allows the application to identify exactly which recipients succeeded or failed.

## Download a Certificate

After a certificate has been successfully generated:

```http
GET /api/v1/certificates/{certificate_id}/download
```

Example:

```http
GET /api/v1/certificates/1/download
```

The API returns the generated PDF file.

## Input Validation

Recipient information is validated using Pydantic.

For example, an invalid email:

```json
{
  "name": "Test User",
  "email": "invalid-email",
  "course_name": "Python Fundamentals"
}
```

returns:

```text
422 Unprocessable Entity
```

The API also validates:

* Minimum and maximum name length
* Minimum and maximum course name length
* Minimum and maximum event name length
* Valid email format
* At least one recipient per generation job

## Error Handling

Certificate generation is handled independently for each recipient.

If one certificate fails, the exception is captured and stored against that certificate. Processing then continues with the remaining recipients.

Example:

```text
Recipient 1 → completed
Recipient 2 → failed
Recipient 3 → completed
```

The final job status becomes:

```text
completed_with_errors
```

Example counters:

```text
total_count     = 3
success_count   = 2
failure_count   = 1
completed_count = 3
```

This prevents a single failed certificate from stopping the entire bulk operation.

## Certificate Storage

Generated PDF files are stored locally in:

```text
storage/certificates/
```

Files are named using the certificate database ID:

```text
certificate_1.pdf
certificate_2.pdf
certificate_3.pdf
```

The generated file path is stored in the database so that the download endpoint can locate the certificate.

## Database Design

The application uses two main tables.

### GenerationJob

Stores information about the complete bulk generation request.

Important fields:

* `id`
* `event_name`
* `status`
* `total_count`
* `success_count`
* `failure_count`
* `created_at`

### Certificate

Stores information about each individual certificate.

Important fields:

* `id`
* `job_id`
* `recipient_name`
* `recipient_email`
* `course_name`
* `status`
* `file_path`
* `error_message`
* `created_at`

### Relationship

```text
GenerationJob
      |
      +── Certificate
      |
      +── Certificate
      |
      +── Certificate
```

One generation job can therefore contain many certificates.

## Background Processing

The API uses FastAPI `BackgroundTasks` to process certificate generation after the generation job has been created.

The processing flow is:

```text
Client
   |
   | POST generation request
   v
FastAPI
   |
   +-- Validate request
   +-- Create generation job
   +-- Create certificate records
   |
   v
Background Processing
   |
   +-- Generate Certificate 1
   +-- Generate Certificate 2
   +-- Generate Certificate 3
   |
   v
Update Database
   |
   v
Client checks job status
```

For this assignment, FastAPI `BackgroundTasks` keeps the implementation simple while demonstrating asynchronous-style job processing.

For a production-scale system with very large workloads, a dedicated task queue such as Celery with Redis or another message broker could be introduced.

## Testing

The project uses Pytest.

Run all tests:

```powershell
pytest
```

The test suite covers:

1. Generation job creation
2. Invalid recipient email validation
3. Certificate generation and job completion
4. Individual certificate failure handling
5. Certificate retrieval/download

Current test result:

```text
5 passed
```

The failure-handling test verifies that if one certificate fails, the remaining certificates continue processing successfully.

## Design Decisions

### Bulk API

The API accepts multiple recipients in a single request.

This avoids requiring a separate API request for every certificate.

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

The PDF generation logic is isolated in:

```text
app/certificate_service.py
```

This makes the certificate-generation logic easier to modify independently from the API layer.

## Future Improvements

For a production-ready implementation, the following improvements could be considered:

* PostgreSQL instead of SQLite
* Celery/RQ or another distributed task queue
* Redis or another message broker
* Object storage such as Amazon S3 for generated PDFs
* Authentication and authorization
* API rate limiting
* Structured logging
* Retry mechanisms for transient failures
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

The implementation demonstrates practical backend development concepts including:

* REST API design
* Request validation
* Relational data modeling
* SQLAlchemy ORM
* Background processing
* Error isolation
* PDF generation
* File handling
* Automated testing
* API documentation
