import re

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import User


@pytest.mark.django_db
def test_signup_creates_authenticated_user(client):
    response = client.post(
        "/api/v1/auth/signup/",
        {
            "username": "new-owner",
            "email": "owner@example.com",
            "first_name": "New",
            "last_name": "Owner",
            "password": "Strong-farm-pass-2026!",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    assert response.json()["username"] == "new-owner"
    assert User.objects.filter(username="new-owner").exists()
    assert client.get("/api/v1/auth/me/").status_code == 200


@pytest.mark.django_db
def test_password_reset_request_does_not_reveal_unknown_email(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    response = client.post(
        "/api/v1/auth/password-reset/",
        {"email": "unknown@example.com"},
        content_type="application/json",
    )

    assert response.status_code == 204
    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_password_reset_changes_password(client, user, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user.email = "owner@example.com"
    user.save(update_fields=["email"])

    request_response = client.post(
        "/api/v1/auth/password-reset/",
        {"email": user.email},
        content_type="application/json",
    )
    assert request_response.status_code == 204
    assert len(mail.outbox) == 1
    assert re.search(r"/reset-password/[^/]+/[^\s]+", mail.outbox[0].body)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    response = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "password": "A-new-farm-pass-2026!"},
        content_type="application/json",
    )

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.check_password("A-new-farm-pass-2026!")
    assert not default_token_generator.check_token(user, token)
