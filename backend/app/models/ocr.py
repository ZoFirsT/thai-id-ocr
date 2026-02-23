from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OCRMetadata(BaseModel):
    is_masked: bool = False
    process_time_ms: int = 0


class OCRData(BaseModel):
    id_number: Optional[str] = None
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    dob: Optional[str] = None
    religion: Optional[str] = None
    address: Optional[str] = None
    metadata: OCRMetadata = Field(default_factory=OCRMetadata)


class DebugInfo(BaseModel):
    raw_text_count: int = 0
    llm_model: str = "unknown"


class ExtractIdResponse(BaseModel):
    status: str = "success"
    request_id: str
    timestamp: datetime
    data: OCRData
    debug: DebugInfo

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat().replace("+00:00", "Z")
        }
