from pydantic import BaseModel, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    course_name: str = Field(min_length=2, max_length=200)


class GenerationJobCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    recipients: list[RecipientCreate] = Field(min_length=1)


class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    course_name: str
    status: str
    error_message: str | None = None
    download_url: str | None = None


class GenerationJobResponse(BaseModel):
    job_id: int
    event_name: str
    status: str

    total_count: int
    success_count: int
    failure_count: int
    completed_count: int

    certificates: list[CertificateResponse]