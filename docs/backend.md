# Backend Architecture & Operations Guide

## Overview
This document dives deeper into the FastAPI backend, OCR/LLM pipeline, and operational concerns (configuration, logging, security, and testing).

## Module Map
```
backend/app/
├── main.py                 # FastAPI app bootstrap
├── api/v1/router.py        # /api/v1 endpoints
├── core/
│   ├── config.py           # Pydantic BaseSettings + defaults
│   ├── logging_config.py   # Rotating file + console logging
│   └── security.py         # Face/lower-band masking helpers
├── models/ocr.py           # Pydantic schemas
└── services/
    ├── ocr_service.py      # EasyOCR pipeline + heuristics
    └── llm_service.py      # Ollama prompt + error handling
```

## Configuration Strategy
- Backend no longer reads `.env` automatically; supply environment variables via shell, Docker, or CI/CD secrets.
- `BACKEND_CONFIG_DEFAULTS` in `core/config.py` documents recommended keys, including `LLM_ENABLED`.
- Required variables: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `LLM_ENABLED`, `MAX_FILE_SIZE_MB`, `PII_MASKING_ENABLED`, `LOG_LEVEL`, `LOG_FILE`, `LOG_TO_CONSOLE`.

Sample export script:
```bash
export APP_ENV=development
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:3b
export LOG_TO_CONSOLE=true
export LLM_ENABLED=true
```

## Request Lifecycle
1. **Upload** – `POST /api/v1/extract-id` validates MIME type + size.
2. **OCR** – `ocr_service.process_id_card`
   - Preprocess image (resize + contrast)
   - EasyOCR (lazy-loaded, GPU auto-detect)
   - Extract heuristics (TH/EN name, DOB, religion, address)
   - Optional PII masking via `security.mask_sensitive_regions`
3. **LLM Cleanup (optional)** – `llm_service.clean_data_with_llm`
   - Per-request decision: `use_llm` query param overrides `LLM_ENABLED`
   - Calls `is_ollama_available()` before invoking Ollama; if unavailable and caller forced LLM, FastAPI returns 503
   - Raises `LLMServiceError` on failure (HTTP 502)
4. **Response** – Wrap with `ExtractIdResponse` including metadata & debug info (`raw_text`, `raw_text_count`, และรายงาน `llm_model` เป็น `disabled`/`unavailable` เมื่อไม่ได้เรียก)

## Logging
- `setup_logging(log_file, log_level, enable_console)` configures rotating file handler + optional console handler.
- Default log path `logs/backend.log` (created automatically).
- OCR service logs detected hardware; router logs per-request metrics; LLM service logs request counts and failures.

## Security & Privacy
- `mask_sensitive_regions` blurs faces via Haar cascade and lower ID band.
- Controlled by `PII_MASKING_ENABLED` env variable.
- Metadata (`OCRMetadata.is_masked`) stored in responses for audit trails.

## Testing Coverage
- Health check + content-type validation
- Oversized upload (expects 413)
- Per-request LLM disable path (ensures raw data + metadata returned)
- Ollama unavailable (expects 503 when `use_llm=true`)
- LLM processing failure (expects 502)
- Debug payload snapshots (ensures `raw_text_count`/`llm_model` reflect fallback states)
- TODO: add direct assertion for masking toggle metadata once masking exposed via dependency injection/test doubles

Run tests:
```bash
cd backend
pytest -vv
```

## Operational Tips
- Restart backend after changing environment variables (settings cached via `lru_cache`).
- Monitor `logs/backend.log` plus console logs (if enabled) for per-request details.
- If GPU not detected, ensure drivers + permissions exist; fallback CPU path always available.
- For production, pair with Docker/Docker Compose to run FastAPI, Ollama, and frontend together.
