from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Optional

import easyocr
import cv2
import numpy as np
import re
import torch

from app.core.logging_config import get_logger
from app.core.security import mask_sensitive_regions

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_device() -> Dict[str, object]:
    """ตรวจสอบความพร้อมของฮาร์ดแวร์เพื่อใช้ GPU ให้มีประสิทธิภาพสูงสุด"""

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("ใช้งาน Apple Silicon GPU (MPS)")
        return {"use_gpu": True, "label": "mps"}
    if torch.cuda.is_available():
        logger.info("ใช้งาน NVIDIA GPU (CUDA)")
        return {"use_gpu": True, "label": "cuda"}

    logger.info("ไม่พบ GPU, สลับไปใช้ CPU")
    return {"use_gpu": False, "label": "cpu"}

@lru_cache(maxsize=1)
def _get_reader() -> easyocr.Reader:
    logger.info("กำลังโหลดโมเดล EasyOCR...")
    device_info = _get_device()
    reader = easyocr.Reader(['th', 'en'], gpu=device_info["use_gpu"])
    logger.info("โหลดโมเดล EasyOCR สำเร็จ")
    return reader

def preprocess_image(img):
    # ขยายภาพ 2
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ปรับ Contrast และ Brightness เพื่อลด Noise ของลายน้ำ
    adjusted = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
    return adjusted

def extract_information(raw_text_list: List[str]) -> Dict[str, Optional[str]]:
    data: Dict[str, Optional[str]] = {
        "id_number": None,
        "name_th": None,
        "name_en": None,
        "dob": None,
        "religion": None,
        "address": None,
    }

    joined_text = " ".join(raw_text_list)
    full_text_no_spaces = joined_text.replace(" ", "")

    # 1. เลขบัตรประชาชน (13 หลักติดกัน)
    id_match = re.search(r"\d{13}", full_text_no_spaces)
    if id_match:
        data["id_number"] = id_match.group()

    # 2. ชื่อไทย (ค้นหารอบ "ชื่อตัว" หรือคำนำหน้า)
    for i, text in enumerate(raw_text_list):
        if "ชื่อตัว" in text or any(prefix in text for prefix in ["นาย", "นาง", "นางสาว"]):
            if i + 1 < len(raw_text_list):
                data["name_th"] = raw_text_list[i + 1].strip()
            break

    # 3. ชื่ออังกฤษ (ค้นหาคำนำหน้าภาษาอังกฤษ)
    english_titles = {"mr", "mr.", "mrs", "mrs.", "miss", "ms", "ms."}
    for i, text in enumerate(raw_text_list):
        if text.lower().strip() in english_titles:
            en_name_parts = [text.strip()]
            for word in raw_text_list[i + 1 : i + 5]:
                cleaned = word.strip()
                if re.match(r"^[A-Za-z\s\.]+$", cleaned):
                    en_name_parts.append(cleaned)
            data["name_en"] = " ".join(en_name_parts)
            break

    # 4. วันเกิด (รองรับทั้งรูปแบบไทย/อังกฤษ)
    dob_pattern = r"(\d{1,2}\s?(?:ม\.?ค\.?|ก\.?พ\.?|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s?\d{2,4})"
    dob_match = re.search(dob_pattern, joined_text, re.IGNORECASE)
    if dob_match:
        data["dob"] = dob_match.group(0)

    # 5. ศาสนา (keyword matching)
    for text in raw_text_list:
        if "ศาสนา" in text:
            data["religion"] = text.split(":")[-1].strip()
            break
        if "พุทธ" in text or "คริสต์" in text or "อิสลาม" in text:
            data["religion"] = text.strip()
            break

    # 6. ที่อยู่ (บรรทัดยาวที่มีคำหลักเช่น "ต." "อ." "จ.")
    address_candidates = [
        text for text in raw_text_list if any(token in text for token in ["ต.", "อ.", "จ.", "แขวง", "เขต"])
    ]
    if address_candidates:
        data["address"] = " ".join(address_candidates)

    return data


def process_id_card(image_bytes: bytes, enable_masking: bool = True) -> dict:
    logger.info("เริ่มประมวลผลภาพบัตร")
    if not image_bytes:
        raise ValueError("ไม่พบข้อมูลรูปภาพ")

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("ไม่สามารถอ่านไฟล์รูปภาพได้")

    processed_img = preprocess_image(img)
    reader = _get_reader()
    device_info = _get_device()
    raw_text_list = reader.readtext(processed_img, detail=0)
    extracted_data = extract_information(raw_text_list)

    metadata = {"is_masked": False}
    if enable_masking:
        _, is_masked = mask_sensitive_regions(img)
        metadata["is_masked"] = is_masked

    logger.info(
        "OCR สำเร็จ",
        extra={
            "raw_text_count": len(raw_text_list),
            "device": device_info["label"],
            "is_masked": metadata["is_masked"],
        },
    )

    return {
        "raw_text": raw_text_list,
        "extracted_data": extracted_data,
        "metadata": metadata,
    }