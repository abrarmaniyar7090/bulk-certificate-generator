from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.schemas import GenerationJobCreate, GenerationJobResponse
from app.processing_services import process_generation_job


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/generation-jobs")
def create_generation_job(
    request: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = models.GenerationJob(
        event_name=request.event_name,
        status="pending",
        total_count=len(request.recipients),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in request.recipients:
        certificate = models.Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            course_name=recipient.course_name,
            status="pending",
        )

        db.add(certificate)

    db.commit()

    background_tasks.add_task(
        process_generation_job,
        job.id,
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_count": job.total_count,
    }


@app.get(
    "/api/v1/generation-jobs/{job_id}",
    response_model=GenerationJobResponse,
)
def get_generation_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(models.GenerationJob)
        .filter(
            models.GenerationJob.id == job_id
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    certificates = []

    for certificate in job.certificates:
        certificates.append(
            {
                "id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "course_name": certificate.course_name,
                "status": certificate.status,
                "error_message": certificate.error_message,
                "download_url": (
                    f"/api/v1/certificates/"
                    f"{certificate.id}/download"
                    if certificate.status == "completed"
                    else None
                ),
            }
        )

    completed_count = (
        job.success_count + job.failure_count
    )

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "status": job.status,
        "total_count": job.total_count,
        "success_count": job.success_count,
        "failure_count": job.failure_count,
        "completed_count": completed_count,
        "certificates": certificates,
    }


@app.get(
    "/api/v1/certificates/{certificate_id}/download"
)
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(models.Certificate)
        .filter(
            models.Certificate.id == certificate_id
        )
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if certificate.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Certificate is not available for download",
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    return FileResponse(
        path=certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf",
    )