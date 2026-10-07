from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def generate_certificate(
    recipient_name: str,
    course_name: str,
    event_name: str,
    output_path: str,
) -> str:

    output_file = Path(output_path)

    # Create the folder if it doesn't already exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(output_file),
        pagesize=landscape(A4),
    )

    # Certificate border
    pdf.setLineWidth(3)
    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60,
    )

    # Title
    title = "CERTIFICATE OF COMPLETION"

    pdf.setFont("Helvetica-Bold", 30)

    title_width = pdf.stringWidth(
        title,
        "Helvetica-Bold",
        30,
    )

    pdf.drawString(
        (page_width - title_width) / 2,
        page_height - 130,
        title,
    )

    # Introduction
    introduction = "This certificate is proudly presented to"

    pdf.setFont("Helvetica", 16)

    introduction_width = pdf.stringWidth(
        introduction,
        "Helvetica",
        16,
    )

    pdf.drawString(
        (page_width - introduction_width) / 2,
        page_height - 190,
        introduction,
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 26)

    name_width = pdf.stringWidth(
        recipient_name,
        "Helvetica-Bold",
        26,
    )

    pdf.drawString(
        (page_width - name_width) / 2,
        page_height - 240,
        recipient_name,
    )

    # Course
    course_text = f"for successfully completing {course_name}"

    pdf.setFont("Helvetica", 16)

    course_width = pdf.stringWidth(
        course_text,
        "Helvetica",
        16,
    )

    pdf.drawString(
        (page_width - course_width) / 2,
        page_height - 290,
        course_text,
    )

    # Event
    event_text = f"Event: {event_name}"

    pdf.setFont("Helvetica-Oblique", 14)

    event_width = pdf.stringWidth(
        event_text,
        "Helvetica-Oblique",
        14,
    )

    pdf.drawString(
        (page_width - event_width) / 2,
        page_height - 340,
        event_text,
    )

    # Footer
    footer = "Bulk Certificate Generator"

    pdf.setFont("Helvetica", 11)

    footer_width = pdf.stringWidth(
        footer,
        "Helvetica",
        11,
    )

    pdf.drawString(
        (page_width - footer_width) / 2,
        60,
        footer,
    )

    pdf.save()

    return str(output_file)