"""Integration tests: signup -> login -> upload flow.

Uses FastAPI TestClient with mocked AI service to avoid external API calls.
"""

import json
from unittest.mock import patch

import pytest


MOCK_ANALYSIS_RESULT = {
    "ats_score": 78,
    "ats_explanation": "Good resume structure",
    "match_score": 72,
    "match_explanation": "Decent match",
    "detected_role": "Software Engineer",
    "detected_explanation": ["Python", "FastAPI"],
    "skills_score": 80,
    "keyword_score": 70,
    "experience_score": 75,
    "project_score": 65,
    "matched_keywords": ["Python", "FastAPI", "REST"],
    "missing_keywords": ["Kubernetes", "AWS"],
    "suggestions": ["Add cloud experience", "Quantify achievements"],
    "weak_points": ["No certifications listed"],
    "summary": "Strong backend developer resume",
}

SIMPLE_RESUME_CONTENT = b"John Doe\nSoftware Engineer\nPython, FastAPI, Docker"


class TestSignupLoginUploadFlow:
    """End-to-end test: create account, log in, analyze a resume."""

    def test_signup(self, client):
        resp = client.post(
            "/auth/signup",
            data={
                "username": "integrationuser",
                "email": "integration@test.com",
                "password": "testpassword123",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body
        assert body["user"]["email"] == "integration@test.com"
        assert body["user"]["username"] == "integrationuser"

    def test_login(self, client):
        # Create user first
        client.post(
            "/auth/signup",
            data={
                "username": "loginuser",
                "email": "login@test.com",
                "password": "testpassword123",
            },
        )
        # Now login
        resp = client.post(
            "/auth/login",
            data={"email": "login@test.com", "password": "testpassword123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "token" in body
        assert body["user"]["email"] == "login@test.com"

    def test_login_wrong_password(self, client):
        client.post(
            "/auth/signup",
            data={
                "username": "wrongpwuser",
                "email": "wrongpw@test.com",
                "password": "correctpassword",
            },
        )
        resp = client.post(
            "/auth/login",
            data={"email": "wrongpw@test.com", "password": "incorrectpassword"},
        )
        assert resp.status_code == 401

    @patch("main.analyze_resume", return_value=MOCK_ANALYSIS_RESULT)
    def test_upload_with_auth(self, mock_analyze, client):
        # Signup and get token
        signup_resp = client.post(
            "/auth/signup",
            data={
                "username": "uploaduser",
                "email": "upload@test.com",
                "password": "testpassword123",
            },
        )
        token = signup_resp.json()["token"]

        # Upload resume
        resp = client.post(
            "/upload",
            files={"file": ("resume.txt", SIMPLE_RESUME_CONTENT, "text/plain")},
            data={"job_description": "Looking for a Python developer"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["ats_score"] == 78
        assert body["detected_role"] == "Software Engineer"
        mock_analyze.assert_called_once()

    def test_upload_without_auth_fails(self, client):
        resp = client.post(
            "/upload",
            files={"file": ("resume.txt", SIMPLE_RESUME_CONTENT, "text/plain")},
            data={"job_description": "Python developer needed"},
        )
        assert resp.status_code == 401

    @patch("main.analyze_resume", return_value=MOCK_ANALYSIS_RESULT)
    def test_history_after_upload(self, mock_analyze, client):
        # Signup
        signup_resp = client.post(
            "/auth/signup",
            data={
                "username": "histuser",
                "email": "hist@test.com",
                "password": "testpassword123",
            },
        )
        token = signup_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload
        client.post(
            "/upload",
            files={"file": ("resume.txt", SIMPLE_RESUME_CONTENT, "text/plain")},
            data={"job_description": "Python dev role"},
            headers=headers,
        )

        # Check history
        resp = client.get("/history", headers=headers)
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) >= 1
        assert entries[0]["filename"] == "resume.txt"
        assert entries[0]["ats_score"] == 78

    def test_get_me(self, client):
        signup_resp = client.post(
            "/auth/signup",
            data={
                "username": "meuser",
                "email": "me@test.com",
                "password": "testpassword123",
            },
        )
        token = signup_resp.json()["token"]

        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@test.com"

    def test_get_me_no_auth(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_get_me_expired_token(self, client):
        """Expired JWT should return 401 on /auth/me."""
        import os
        from datetime import datetime, timedelta, timezone

        import jwt

        expired_token = jwt.encode(
            {
                "sub": "fake-id",
                "email": "expired@test.com",
                "exp": datetime.now(timezone.utc) - timedelta(days=1),
                "iat": datetime.now(timezone.utc) - timedelta(days=2),
            },
            os.environ.get("JWT_SECRET", "test-secret-key-for-testing"),
            algorithm="HS256",
        )
        resp = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert resp.status_code == 401
