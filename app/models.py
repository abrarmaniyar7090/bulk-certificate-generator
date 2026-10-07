from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(200), nullable=False)

    status = Column(String(50), nullable=False, default="pending")

    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("generation_jobs.id"),
        nullable=False,
    )

    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(320), nullable=False)
    course_name = Column(String(200), nullable=False)

    status = Column(String(50), nullable=False, default="pending")

    file_path = Column(String(500), nullable=True)
    error_message = Column(String(1000), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    job = relationship(
        "GenerationJob",
        back_populates="certificates",
    )