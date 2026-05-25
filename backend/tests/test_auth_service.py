"""Tests for auth_service: password hashing, JWT tokens, validation."""

import time
import pytest
from fastapi import HTTPException

from auth_service import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
    validate_signup,
    signup_user,
    authenticate_user,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "mysecretpassword"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------

class TestJWT:
    def test_create_and_verify_roundtrip(self):
        token = create_token("user-123", "test@example.com")
        payload = verify_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"

    def test_invalid_token_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not-a-valid-token")
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises(self):
        token = create_token("user-1", "a@b.com")
        tampered = token[:-4] + "XXXX"
        with pytest.raises(HTTPException) as exc_info:
            verify_token(tampered)
        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# Signup validation
# ---------------------------------------------------------------------------

class TestValidateSignup:
    def test_valid_input_passes(self):
        validate_signup("testuser", "test@example.com", "password123")

    def test_short_username_fails(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_signup("ab", "test@example.com", "password123")
        assert exc_info.value.status_code == 400

    def test_long_username_fails(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_signup("a" * 31, "test@example.com", "password123")
        assert exc_info.value.status_code == 400

    def test_invalid_username_chars_fails(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_signup("user name!", "test@example.com", "password123")
        assert exc_info.value.status_code == 400

    def test_invalid_email_fails(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_signup("testuser", "not-an-email", "password123")
        assert exc_info.value.status_code == 400

    def test_short_password_fails(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_signup("testuser", "test@example.com", "short")
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Signup + Authenticate (integration with DB)
# ---------------------------------------------------------------------------

class TestSignupAndAuth:
    def test_signup_creates_user(self, db_session):
        user = signup_user(db_session, "newuser", "new@test.com", "password123")
        assert user.username == "newuser"
        assert user.email == "new@test.com"
        assert user.password_hash is not None
        assert user.password_hash != "password123"

    def test_duplicate_email_fails(self, db_session):
        signup_user(db_session, "user1", "dup@test.com", "password123")
        with pytest.raises(HTTPException) as exc_info:
            signup_user(db_session, "user2", "dup@test.com", "password123")
        assert exc_info.value.status_code == 409

    def test_duplicate_username_fails(self, db_session):
        signup_user(db_session, "dupname", "a@test.com", "password123")
        with pytest.raises(HTTPException) as exc_info:
            signup_user(db_session, "dupname", "b@test.com", "password123")
        assert exc_info.value.status_code == 409

    def test_authenticate_valid(self, db_session):
        signup_user(db_session, "authuser", "auth@test.com", "password123")
        user = authenticate_user(db_session, "auth@test.com", "password123")
        assert user.email == "auth@test.com"

    def test_authenticate_wrong_password(self, db_session):
        signup_user(db_session, "authuser2", "auth2@test.com", "password123")
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(db_session, "auth2@test.com", "wrongpassword")
        assert exc_info.value.status_code == 401

    def test_authenticate_nonexistent_email(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(db_session, "nobody@test.com", "password123")
        assert exc_info.value.status_code == 401
