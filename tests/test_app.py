"""Tests for the Mailcow Alias Generator Flask app."""

import base64
import json
from types import SimpleNamespace

import pytest
from altcha import solve_challenge_v1
from werkzeug.security import generate_password_hash

import app as app_module


TEST_CONFIG = {
    "mailcow_url": "https://mail.test",
    "api_key": "TEST_KEY",
    "domains": ["example.com", "example2.com"],
    "default_domain": "example.com",
    "sogo_visible": True,
    "altcha_enabled": False,
    "altcha_provider": "local",
    "altcha_hmac_key": "k" * 32,
    "users": {
        "alice": {
            "password": generate_password_hash("hashed-pass", method="pbkdf2:sha256"),
            "default_redirect": "alice@example.com",
            "description": "Alice",
        },
        "bob": {  # legacy plaintext, still accepted
            "password": "plain-pass",
            "default_redirect": "bob@example.com",
            "description": "Bob",
        },
    },
}


@pytest.fixture
def client(monkeypatch):
    app_module.app.config["TESTING"] = True
    app_module.limiter.enabled = False  # disabled by default; one test re-enables it
    monkeypatch.setattr(app_module, "load_config", lambda: TEST_CONFIG)
    return app_module.app.test_client()


# --- password_matches -------------------------------------------------------

def test_password_matches_hashed():
    h = generate_password_hash("secret", method="pbkdf2:sha256")
    assert app_module.password_matches(h, "secret") is True
    assert app_module.password_matches(h, "wrong") is False


def test_password_matches_legacy_plaintext():
    assert app_module.password_matches("plain", "plain") is True
    assert app_module.password_matches("plain", "nope") is False


def test_password_matches_empty():
    assert app_module.password_matches(None, "x") is False
    assert app_module.password_matches("x", None) is False


# --- authenticate_user ------------------------------------------------------

def test_authenticate_user_hashed_and_legacy():
    assert app_module.authenticate_user("hashed-pass", TEST_CONFIG)["user_id"] == "alice"
    assert app_module.authenticate_user("plain-pass", TEST_CONFIG)["user_id"] == "bob"
    assert app_module.authenticate_user("bad", TEST_CONFIG) is None


# --- /api/config ------------------------------------------------------------

def test_config_local_provider(client):
    data = client.get("/api/config").get_json()
    assert data["altcha_provider"] == "local"
    assert data["altcha_challenge_url"] == "/api/altcha/challenge"
    assert data["domains"] == ["example.com", "example2.com"]
    assert data["multi_user_enabled"] is True
    assert data["version"] == app_module.__version__


def test_config_gatecha_provider(client, monkeypatch):
    cfg = dict(TEST_CONFIG, altcha_enabled=True, altcha_provider="gatecha",
               gatecha_url="https://gate.test/", gatecha_api_key="gk_abc")
    monkeypatch.setattr(app_module, "load_config", lambda: cfg)
    data = client.get("/api/config").get_json()
    assert data["altcha_provider"] == "gatecha"
    assert data["altcha_challenge_url"] == "https://gate.test/api/v1/challenge?apiKey=gk_abc"


# --- /api/create-alias ------------------------------------------------------

def test_create_alias_missing_fields(client):
    r = client.post("/api/create-alias", json={"alias": "", "redirectTo": ""})
    assert r.status_code == 400


def test_create_alias_disallowed_domain(client):
    r = client.post("/api/create-alias",
                    json={"alias": "x@notallowed.com", "redirectTo": "me@example.com"})
    assert r.status_code == 400
    assert "allowed domains" in r.get_json()["error"]


def test_create_alias_success(client, monkeypatch):
    monkeypatch.setattr(app_module, "create_mailcow_alias",
                        lambda alias, redirect, config: (True, "Alias created successfully"))
    r = client.post("/api/create-alias",
                    json={"alias": "svc1234@example.com", "redirectTo": "me@example.com"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["success"] is True
    assert body["alias"] == "svc1234@example.com"


def test_create_alias_does_not_leak_exception(client, monkeypatch):
    # On failure, the client must get a clean message, never a stack trace.
    def boom(alias, redirect, config):
        return False, "Unexpected error while creating the alias"
    monkeypatch.setattr(app_module, "create_mailcow_alias", boom)
    r = client.post("/api/create-alias",
                    json={"alias": "svc@example.com", "redirectTo": "me@example.com"})
    assert r.status_code == 400
    assert "Traceback" not in str(r.get_json())


# --- verify_altcha_solution provider dispatch -------------------------------

def test_verify_altcha_dispatches_to_gatecha(monkeypatch):
    called = {}

    def fake_gatecha(payload, config):
        called["p"] = payload
        return True, "ok"

    monkeypatch.setattr(app_module, "verify_altcha_via_gatecha", fake_gatecha)
    ok, _ = app_module.verify_altcha_solution("PAYLOAD", {"altcha_provider": "gatecha"})
    assert ok is True and called["p"] == "PAYLOAD"


# --- local ALTCHA provider --------------------------------------------------
# These exercise the real altcha library rather than a mock: the widget speaks
# the v1 protocol, so a library upgrade that changes the v1 wire format or the
# verify semantics must fail here rather than only in the Docker smoke test.

LOCAL_CONFIG = {"altcha_provider": "local", "altcha_hmac_key": "k" * 32}


def solve(challenge):
    """Solve a challenge the way the browser widget does, returning the payload."""
    solution = solve_challenge_v1(
        challenge.challenge, challenge.salt, challenge.algorithm,
        app_module.ALTCHA_MAX_NUMBER, 0,
    )
    assert solution is not None, "challenge was not solvable within max_number"
    return {
        "algorithm": challenge.algorithm,
        "challenge": challenge.challenge,
        "salt": challenge.salt,
        "signature": challenge.signature,
        "number": solution.number,
    }


def encode(payload):
    return base64.b64encode(json.dumps(payload).encode()).decode()


def test_create_altcha_challenge_local():
    challenge, error = app_module.create_altcha_challenge(LOCAL_CONFIG)
    assert error is None
    # The fields /api/altcha/challenge serialises must all be present.
    assert challenge.algorithm == "SHA-256"
    assert challenge.challenge and challenge.salt and challenge.signature


def test_create_altcha_challenge_without_key():
    challenge, error = app_module.create_altcha_challenge({"altcha_provider": "local"})
    assert challenge is None and error == "ALTCHA not configured"


def test_verify_altcha_local_round_trip():
    challenge, _ = app_module.create_altcha_challenge(LOCAL_CONFIG)
    ok, message = app_module.verify_altcha_solution(encode(solve(challenge)), LOCAL_CONFIG)
    assert ok is True, message


def test_verify_altcha_rejects_wrong_hmac_key():
    challenge, _ = app_module.create_altcha_challenge(LOCAL_CONFIG)
    payload = encode(solve(challenge))
    ok, _ = app_module.verify_altcha_solution(payload, dict(LOCAL_CONFIG, altcha_hmac_key="x" * 32))
    assert ok is False


def test_verify_altcha_rejects_tampered_number():
    challenge, _ = app_module.create_altcha_challenge(LOCAL_CONFIG)
    payload = solve(challenge)
    payload["number"] += 1
    ok, _ = app_module.verify_altcha_solution(encode(payload), LOCAL_CONFIG)
    assert ok is False


def test_verify_altcha_rejects_garbage_payload():
    ok, _ = app_module.verify_altcha_solution("not-base64-json", LOCAL_CONFIG)
    assert ok is False


# --- /api/altcha/challenge --------------------------------------------------

def test_altcha_challenge_endpoint_serves_solvable_challenge(client, monkeypatch):
    cfg = dict(TEST_CONFIG, altcha_enabled=True)
    monkeypatch.setattr(app_module, "load_config", lambda: cfg)

    data = client.get("/api/altcha/challenge").get_json()
    assert set(data) == {"algorithm", "challenge", "salt", "signature"}

    # What the endpoint serves must round-trip through the verifier.
    served = SimpleNamespace(**data)
    ok, message = app_module.verify_altcha_solution(encode(solve(served)), cfg)
    assert ok is True, message


def test_altcha_challenge_endpoint_disabled(client):
    # TEST_CONFIG has altcha_enabled False.
    assert client.get("/api/altcha/challenge").status_code == 400


def test_altcha_challenge_endpoint_rejected_in_gatecha_mode(client, monkeypatch):
    cfg = dict(TEST_CONFIG, altcha_enabled=True, altcha_provider="gatecha",
               gatecha_url="https://gate.test/", gatecha_api_key="gk_abc")
    monkeypatch.setattr(app_module, "load_config", lambda: cfg)
    assert client.get("/api/altcha/challenge").status_code == 400


# --- /api/auth --------------------------------------------------------------

def test_auth_success(client):
    r = client.post("/api/auth", json={"password": "plain-pass"})
    assert r.status_code == 200
    assert r.get_json()["user"]["id"] == "bob"


def test_auth_wrong_password(client):
    r = client.post("/api/auth", json={"password": "nope"})
    assert r.status_code == 401


# --- rate limiting ----------------------------------------------------------

def test_auth_rate_limited(client):
    app_module.limiter.enabled = True
    try:
        responses = [client.post("/api/auth", json={"password": "nope"}) for _ in range(12)]
        statuses = [r.status_code for r in responses]
        assert 429 in statuses, statuses
        # The 429 body must be JSON (custom handler), so the frontend can parse it.
        throttled = next(r for r in responses if r.status_code == 429)
        assert "error" in throttled.get_json()
    finally:
        app_module.limiter.enabled = False
        app_module.limiter.reset()
