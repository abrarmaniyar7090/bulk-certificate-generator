from pathlib import Path

from app import models
from app.certificate_service import generate_certificate
from app.database import SessionLocal


STORAGE_DIR = Path("storage/certificates")


def process_generation_job(job_id: int):
    db = SessionLocal()

    try:
        job = (
            db.query(models.GenerationJob)
            .filter(
                models.GenerationJob.id == job_id
            )
            .first()
        )

        if not job:
            return

        job.status = "processing"

        db.commit()

        certificates = (
            db.query(models.Certificate)
            .filter(
                models.Certificate.job_id == job_id
            )
            .all()
        )

        for certificate in certificates:

            certificate.status = "processing"

            db.commit()

            try:
                output_path = (
                    STORAGE_DIR
                    / f"certificate_{certificate.id}.pdf"
                )

                generate_certificate(
                    recipient_name=certificate.recipient_name,
                    course_name=certificate.course_name,
                    event_name=job.event_name,
                    output_path=str(output_path),
                )

                certificate.status = "completed"

                certificate.file_path = str(
                    output_path
                )

                job.success_count += 1

            except Exception as error:

                certificate.status = "failed"

                certificate.error_message = str(error)

                job.failure_count += 1

            db.commit()

        if job.failure_count == 0:

            job.status = "completed"

        elif job.success_count > 0:

            job.status = "completed_with_errors"

        else:

            job.status = "failed"

        db.commit()

    finally:
        db.close()