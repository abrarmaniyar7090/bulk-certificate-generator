from app.certificate_service import generate_certificate


output_path = "storage/certificates/test_certificate.pdf"


generate_certificate(
    recipient_name="Abrar Hussain",
    course_name="Python Fundamentals",
    event_name="Python Bootcamp 2026",
    output_path=output_path,
)


print(f"Certificate generated: {output_path}")