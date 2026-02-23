import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.llm_service import LLMServiceError

client = TestClient(app)


def _stub_ocr_payload():
    return {
        "raw_text": ["นาย สมชาย", "ใจดี"],
        "extracted_data": {
            "id_number": "1234567890123",
            "name_th": "นาย สมชาย ใจดี",
            "name_en": "MR. SOMCHAI JAIDEE",
            "dob": "17 ม.ค. 2545",
            "religion": "พุทธ",
            "address": "กรุงเทพฯ",
        },
        "metadata": {"is_masked": True},
    }


def test_health_endpoint_returns_success():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "environment" in payload


def test_extract_id_rejects_invalid_content_type():
    files = {"image": ("dummy.txt", b"abc", "text/plain")}
    response = client.post("/api/v1/extract-id", files=files)
    assert response.status_code == 415
    payload = response.json()
    assert payload["detail"] == "รองรับเฉพาะไฟล์ JPEG หรือ PNG"


def test_extract_id_rejects_oversized_file(monkeypatch):
    from app.api.v1 import router

    monkeypatch.setattr(router.settings, "max_file_size_mb", 1)
    too_large = b"x" * (router.settings.max_file_size_bytes + 1)
    files = {"image": ("big.jpg", too_large, "image/jpeg")}

    response = client.post("/api/v1/extract-id", files=files)
    assert response.status_code == 413
    assert str(router.settings.max_file_size_mb) in response.json()["detail"]


def test_extract_id_returns_raw_data_when_llm_disabled(monkeypatch):
    monkeypatch.setattr("app.api.v1.router.process_id_card", lambda *args, **kwargs: _stub_ocr_payload())
    monkeypatch.setattr("app.api.v1.router.is_ollama_available", lambda: True)

    files = {"image": ("card.jpg", b"fake-bytes", "image/jpeg")}
    response = client.post("/api/v1/extract-id?use_llm=false", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id_number"] == "1234567890123"
    assert payload["debug"]["llm_model"] == "disabled"


def test_extract_id_errors_when_ollama_unavailable(monkeypatch):
    monkeypatch.setattr("app.api.v1.router.process_id_card", lambda *args, **kwargs: _stub_ocr_payload())
    monkeypatch.setattr("app.api.v1.router.is_ollama_available", lambda: False)

    files = {"image": ("card.jpg", b"fake-bytes", "image/jpeg")}
    response = client.post("/api/v1/extract-id?use_llm=true", files=files)

    assert response.status_code == 503
    assert "Ollama" in response.json()["detail"]


def test_extract_id_returns_502_when_llm_processing_fails(monkeypatch):
    monkeypatch.setattr("app.api.v1.router.process_id_card", lambda *args, **kwargs: _stub_ocr_payload())
    monkeypatch.setattr("app.api.v1.router.is_ollama_available", lambda: True)

    def _fail_llm(_):
        raise LLMServiceError("boom")

    monkeypatch.setattr("app.api.v1.router.clean_data_with_llm", _fail_llm)

    files = {"image": ("card.jpg", b"fake-bytes", "image/jpeg")}
    response = client.post("/api/v1/extract-id", files=files)

    assert response.status_code == 502
    assert "LLM" in response.json()["detail"]
