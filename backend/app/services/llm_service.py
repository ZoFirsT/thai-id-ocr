from __future__ import annotations

import json
from typing import List

import requests

from app.core.config import get_settings
from app.core.logging_config import get_logger


class LLMServiceError(RuntimeError):
    """Raised when the LLM service cannot return a valid response."""


settings = get_settings()
logger = get_logger(__name__)


PROMPT_TEMPLATE = """
คุณคือ AI ผู้เชี่ยวชาญด้านการตรวจสอบและแก้ไขข้อมูลบัตรประชาชนไทย
นี่คือข้อความดิบที่ได้จากระบบ OCR ซึ่งอาจมีคำสะกดผิด หรืออ่านสระ/พยัญชนะผิดเพี้ยน:

{raw_text}

หน้าที่ของคุณคือ:
1. สกัดข้อมูลสำคัญออกมา
2. แก้ไขตัวสะกดภาษาไทยที่เพี้ยนให้ถูกต้องตามความน่าจะเป็น (เช่น 'ธนัชชำ' ควรเป็น 'ธนัชชา', 'วนทบุร' ควรเป็น 'นนทบุรี', 'wทธ' ควรเป็น 'พุทธ')
3. จัดรูปแบบข้อมูลให้เป็น JSON format เท่านั้น

ใช้ Key ต่อไปนี้ในการสร้าง JSON:
- id_number (เลขบัตร 13 หลัก ติดกัน)
- name_th (ชื่อและนามสกุลภาษาไทย)
- name_en (ชื่อและนามสกุลภาษาอังกฤษ)
- dob (วันเกิด เช่น 17 ม.ค. 2545 / 17 Mar. 2002)
- religion (ศาสนา)
- address (ที่อยู่ทั้งหมดรวมกัน)

ห้ามมีข้อความอธิบายใดๆ ทั้งสิ้น คืนค่ากลับมาเป็น JSON เท่านั้น
""".strip()


def is_ollama_available(timeout: int = 3) -> bool:
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.warning("Ollama health check failed", exc_info=False)
        return False


def clean_data_with_llm(raw_text_list: List[str]) -> dict:
    logger.info("Sending OCR text to LLM", extra={"raw_text_count": len(raw_text_list)})

    prompt = PROMPT_TEMPLATE.format(raw_text="\n".join(raw_text_list))
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        response = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        cleaned_data = json.loads(result["response"])
    except (requests.RequestException, KeyError, json.JSONDecodeError) as exc:
        logger.exception("LLM request failed")
        raise LLMServiceError("ไม่สามารถประมวลผลด้วย LLM ได้") from exc

    logger.info("LLM returned structured JSON")
    return cleaned_data
