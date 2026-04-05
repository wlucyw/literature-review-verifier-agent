import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_verify_sample_input() -> None:
    sample = json.loads(Path("data/samples/sample_input.json").read_text(encoding="utf-8-sig"))
    response = client.post("/verify", json=sample)
    assert response.status_code == 200
    payload = response.json()
    assert payload["review_text"]
    assert len(payload["item_results"]) >= 2
    assert "ai_writing_check" in payload
