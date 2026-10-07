from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_generation_job():
    response = client.post(
        "/api/v1/generation-jobs",
        json={
            "event_name": "Test Event",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "course_name": "Python Fundamentals",
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["total_count"] == 1


def test_invalid_recipient_email():
    response = client.post(
        "/api/v1/generation-jobs",
        json={
            "event_name": "Test Event",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "invalid-email",
                    "course_name": "Python Fundamentals",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_generation_job_completes():
    response = client.post(
        "/api/v1/generation-jobs",
        json={
            "event_name": "Certificate Test Event",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                    "course_name": "Python Fundamentals",
                }
            ],
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/v1/generation-jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["total_count"] == 1
    assert data["success_count"] == 1
    assert data["failure_count"] == 0
    assert data["completed_count"] == 1
    assert data["status"] == "completed"

    assert len(data["certificates"]) == 1

    certificate = data["certificates"][0]

    assert certificate["status"] == "completed"
    assert certificate["download_url"] is not None


def test_one_certificate_failure_does_not_stop_others():
    with patch(
        "app.processing_services.generate_certificate"
    ) as mock_generate:

        def generate_certificate_side_effect(
            recipient_name,
            course_name,
            event_name,
            output_path,
        ):
            if recipient_name == "Failed User":
                raise Exception(
                    "Simulated certificate generation failure"
                )

            from app.certificate_service import (
                generate_certificate,
            )

            return generate_certificate(
                recipient_name=recipient_name,
                course_name=course_name,
                event_name=event_name,
                output_path=output_path,
            )

        mock_generate.side_effect = (
            generate_certificate_side_effect
        )

        response = client.post(
            "/api/v1/generation-jobs",
            json={
                "event_name": "Failure Test Event",
                "recipients": [
                    {
                        "name": "Successful User",
                        "email": "success@example.com",
                        "course_name": "Python Fundamentals",
                    },
                    {
                        "name": "Failed User",
                        "email": "failed@example.com",
                        "course_name": "Python Fundamentals",
                    },
                    {
                        "name": "Another Successful User",
                        "email": "another@example.com",
                        "course_name": "Python Fundamentals",
                    },
                ],
            },
        )

        assert response.status_code == 200

        job_id = response.json()["job_id"]

        status_response = client.get(
            f"/api/v1/generation-jobs/{job_id}"
        )

        assert status_response.status_code == 200

        data = status_response.json()

        assert data["total_count"] == 3
        assert data["success_count"] == 2
        assert data["failure_count"] == 1
        assert data["completed_count"] == 3
        assert data["status"] == "completed_with_errors"

        certificates = data["certificates"]

        assert len(certificates) == 3

        failed_certificate = next(
            certificate
            for certificate in certificates
            if certificate["recipient_name"]
            == "Failed User"
        )

        assert failed_certificate["status"] == "failed"

        assert (
            failed_certificate["error_message"]
            == "Simulated certificate generation failure"
        )


def test_download_generated_certificate():
    response = client.post(
        "/api/v1/generation-jobs",
        json={
            "event_name": "Download Test Event",
            "recipients": [
                {
                    "name": "Download User",
                    "email": "download@example.com",
                    "course_name": "Python Fundamentals",
                }
            ],
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/v1/generation-jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "completed"

    certificate_id = (
        data["certificates"][0]["id"]
    )

    download_response = client.get(
        f"/api/v1/certificates/{certificate_id}/download"
    )

    assert download_response.status_code == 200

    assert (
        download_response.headers["content-type"]
        == "application/pdf"
    )

    assert len(download_response.content) > 0