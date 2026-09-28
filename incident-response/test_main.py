import json

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)

    async def fake_evidence(endpoint):
        return {"endpoint": endpoint, "logs": {"entries": []}, "traces": {"traces": []}}

    monkeypatch.setattr(main, "collect_evidence", fake_evidence)
    monkeypatch.setattr(
        main,
        "run_copilot",
        lambda prompt: {"status": "completed", "response": "Test notification received; no incident to fix."},
    )
    with TestClient(main.app) as test_client:
        yield test_client


def test_test_alert_is_saved_and_returned(client, tmp_path):
    response = client.post(
        "/alerts",
        json={
            "alerts": [
                {
                    "status": "firing",
                    "labels": {"alertname": "ResponderTest", "test": "true"},
                    "annotations": {"summary": "Test notification; no incident to fix"},
                }
            ]
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "completed"
    assert result["response"] == "Test notification received; no incident to fix."

    record = json.loads((tmp_path / f"{result['incident_id']}.json").read_text(encoding="utf-8"))
    assert record["endpoint"] == "/api/orders/{order_id}"
    assert record["evidence"]["logs"]["entries"] == []
    assert client.get(f"/incidents/{result['incident_id']}").json() == record


def test_alert_secrets_are_redacted(client, monkeypatch):
    def fake_run_copilot(prompt):
        assert "super-secret" not in prompt
        return {"status": "completed", "response": "redacted"}

    monkeypatch.setattr(main, "run_copilot", fake_run_copilot)
    response = client.post(
        "/alerts",
        json={"alerts": [{"status": "firing", "labels": {"api_token": "super-secret"}}]},
    )
    assert response.status_code == 200
    record = client.get(f"/incidents/{response.json()['incident_id']}").json()
    assert record["alerts"][0]["labels"]["api_token"] == "[REDACTED]"


def test_alert_endpoint_rejects_invalid_payload(client):
    assert client.post("/alerts", json={"not_alerts": []}).status_code == 400
    assert client.post("/alerts", content="not-json").status_code == 400
