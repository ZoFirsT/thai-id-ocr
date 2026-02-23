from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Final
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.ocr import DebugInfo, ExtractIdResponse, OCRData, OCRMetadata
from app.services.llm_service import (
    LLMServiceError,
    clean_data_with_llm,
    is_ollama_available,
)
from app.services.ocr_service import process_id_card

settings = get_settings()
logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES: Final[set[str]] = {"image/jpeg", "image/png", "image/jpg"}

router = APIRouter(prefix=settings.api_v1_prefix, tags=["Thai ID OCR"])


@router.post("/extract-id", response_model=ExtractIdResponse)
async def extract_id(
    image: UploadFile = File(...),
    use_llm: bool | None = None,
) -> ExtractIdResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="รองรับเฉพาะไฟล์ JPEG หรือ PNG",
        )

    image_bytes = await image.read()
    if len(image_bytes) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"ไฟล์มีขนาดเกิน {settings.max_file_size_mb}MB",
        )

    request_id = str(uuid4())
    started = time.perf_counter()

    try:
        ocr_payload = process_id_card(
            image_bytes, enable_masking=settings.pii_masking_enabled
        )
    except ValueError as exc:  # ภาพไม่ถูกต้อง
        logger.warning("Invalid image received", extra={"request_id": request_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # OCR ขัดข้อง
        logger.exception("OCR pipeline failed", extra={"request_id": request_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OCR processing error") from exc

    raw_text = ocr_payload["raw_text"]
    ocr_meta = ocr_payload.get("metadata", {})

    llm_requested = settings.llm_enabled if use_llm is None else use_llm
    llm_should_run = llm_requested and is_ollama_available()

    if llm_requested and not llm_should_run:
        if use_llm is True:
            logger.error(
                "LLM requested explicitly but Ollama is unreachable",
                extra={"request_id": request_id},
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ไม่พบ Ollama service โปรดตรวจสอบการติดตั้ง/พอร์ต",
            )
        logger.warning(
            "Ollama unavailable, falling back to raw OCR extraction",
            extra={"request_id": request_id},
        )

    if llm_should_run:
        try:
            ai_cleaned_data = clean_data_with_llm(raw_text)
            llm_model = settings.ollama_model
        except LLMServiceError as exc:
            logger.exception("LLM processing failed", extra={"request_id": request_id})
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    else:
        logger.info(
            "LLM disabled for this request, returning raw OCR extraction",
            extra={"request_id": request_id},
        )
        ai_cleaned_data = ocr_payload.get("extracted_data", {})
        llm_model = "disabled" if not llm_requested else "unavailable"

    process_time_ms = int((time.perf_counter() - started) * 1000)
    metadata = OCRMetadata(
        is_masked=bool(ocr_meta.get("is_masked", False)),
        process_time_ms=process_time_ms,
    )

    ocr_data = OCRData(**ai_cleaned_data, metadata=metadata)

    response = ExtractIdResponse(
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        data=ocr_data,
        debug=DebugInfo(
            raw_text_count=len(raw_text),
            llm_model=llm_model,
        ),
    )
    logger.info(
        "Processed Thai ID successfully",
        extra={
            "request_id": request_id,
            "process_time_ms": process_time_ms,
            "raw_text_count": len(raw_text),
        },
    )
    return response
