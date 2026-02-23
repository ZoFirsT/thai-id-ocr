# Thai ID Card OCR Platform

ระบบอ่านข้อมูลบัตรประชาชนไทยแบบ **Local-first** ที่ประกอบด้วย FastAPI (Backend), EasyOCR/OpenCV (OCR Pipeline), Ollama Qwen2.5 (LLM Cleaning) และ Next.js (Frontend อยู่ระหว่างพัฒนา)

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Key Features](#key-features)
3. [Repository Layout](#repository-layout)
4. [System Requirements](#system-requirements)
5. [Configuration](#configuration)
6. [Local Development](#local-development)
7. [API Contract](#api-contract)
8. [Testing](#testing)
9. [Logging & Security](#logging--security)
10. [Troubleshooting](#troubleshooting)
11. [Documentation](#documentation)
12. [Contributing & License](#contributing--license)

## Architecture Overview
```
[ Next.js Frontend ] --(REST)--> [ FastAPI Backend ]
                                  |-> EasyOCR + OpenCV  (preprocess + raw text)
                                  |-> Ollama (Qwen2.5)  (LLM cleanup)
                                  |-> PII Masking (face + ID band blur)
```

### Components
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (UI สำหรับอัปโหลดและดูผลลัพธ์)
- **Backend**: FastAPI พร้อม router/services/models ที่แยกชัดเจน
- **OCR Engine**: EasyOCR + OpenCV พร้อมตรวจจับ GPU (Apple MPS / CUDA / CPU)
- **LLM Engine**: Ollama hosting Qwen2.5 (สามารถเปลี่ยนโมเดลผ่าน env)
- **Security**: Face & lower-band masking, metadata บอกสถานะการปกปิดข้อมูล

## Key Features
1. รองรับ `.jpg`, `.jpeg`, `.png` พร้อมตรวจขนาดไฟล์ (`MAX_FILE_SIZE_MB`)
2. คืนข้อมูลสำคัญครบชุด (เลขบัตร, TH/EN name, DOB, religion, address) + `metadata`/`debug`
3. logging มีทั้ง rotating file และ console (ควบคุมด้วย `LOG_TO_CONSOLE`)
4. มี toggle สำหรับ PII masking (`PII_MASKING_ENABLED`)
5. โครงสร้างโค้ดรองรับการขยายและการทดสอบอัตโนมัติ

## Repository Layout
```
thai-id-ocr/
├── README.md
├── backend/
│   ├── app/
│   │   ├── api/v1/router.py        # REST endpoints
│   │   ├── core/                   # config, logging, security
│   │   ├── models/ocr.py           # Pydantic schemas
│   │   └── services/               # OCR + LLM orchestration
│   ├── requirements.txt
│   └── tests/
└── frontend/                       # Next.js scaffold (อยู่ระหว่างเติม UI)
```

## System Requirements
- Python 3.10+
- Node.js 20+ (สำหรับ frontend)
- [Ollama](https://ollama.com) พร้อมโมเดล `qwen2.5`
- RAM 8GB+ (แนะนำ 16GB หากเปิด GPU OCR)

## Configuration
Backend **ไม่อ่าน** `.env` อัตโนมัติอีกต่อไป ต้องตั้งค่าผ่าน Environment Variables เองเท่านั้น

| Variable | Default | Description |
| --- | --- | --- |
| `APP_ENV` | `development` | Label ของ environment ปัจจุบัน |
| `API_V1_PREFIX` | `/api/v1` | Base path ของ API router |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | ที่อยู่ Ollama instance |
| `OLLAMA_MODEL` | `qwen2.5` | ชื่อโมเดลที่จะเรียกใช้ |
| `LLM_ENABLED` | `true` | เปิด/ปิดการใช้งาน LLM (ใช้เฉพาะผล EasyOCR เมื่อปิด) |
| `MAX_FILE_SIZE_MB` | `8` | จำกัดขนาดไฟล์อัปโหลด |
| `PII_MASKING_ENABLED` | `true` | เปิด/ปิดการเบลอใบหน้า/แถบ |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `LOG_FILE` | `logs/backend.log` | Path สำหรับเก็บ log file |
| `LOG_TO_CONSOLE` | `true` | เปิด/ปิด console handler |

Frontend (Next.js) ใช้ตัวแปร prefix `NEXT_PUBLIC_...`

| Variable | Default |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` |
| `NEXT_PUBLIC_MAX_UPLOAD_MB` | `8` |

> สามารถสร้างไฟล์ `.env` เฉพาะบนเครื่องและ export เอง เช่น `export OLLAMA_BASE_URL=http://localhost:9000`

## Local Development

### 1) เตรียม Ollama
```bash
ollama pull qwen2.5
ollama run qwen2.5   # ดีฟอลต์พอร์ต 11434
```

### 2) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# ตัวอย่าง env
export OLLAMA_BASE_URL=http://localhost:11434
export LOG_TO_CONSOLE=true

uvicorn app.main:app --reload
```
- Base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Log file: `logs/backend.log`

### 3) Frontend (WIP)
```bash
cd frontend
npm install
npm run dev
```
เปิด http://localhost:3000 เพื่อดู UI ตัวอย่าง

## API Contract
- Method: `POST`
- Endpoint: `/api/v1/extract-id`
- Content-Type: `multipart/form-data`
- Field: `image`
- Optional Query: `use_llm=true|false` (default = true). ถ้า `true` แต่ Ollama ไม่พร้อม ระบบจะตอบ `503` ทันที แทนที่จะรอกระบวนการ OCR เสร็จ

```json
{
  "status": "success",
  "request_id": "uuidv4",
  "timestamp": "2024-02-23T00:00:00Z",
  "data": {
    "id_number": "1234567890123",
    "name_th": "นาย สมชาย ใจดี",
    "name_en": "MR. SOMCHAI JAIDEE",
    "dob": "17 ม.ค. 2545",
    "religion": "พุทธ",
    "address": "123 ...",
    "metadata": {
      "is_masked": true,
      "process_time_ms": 512
    }
  },
  "debug": {
    "raw_text_count": 37,
    "llm_model": "qwen2.5"
  }
}
```

## Testing
```bash
cd backend
pytest -vv
```
ปัจจุบันมี smoke tests สำหรับ health check และ content-type validation (กำลังเพิ่มกรณีไฟล์เกิน, masking toggle, LLM failure)

## Logging & Security
- `setup_logging` ตั้ง rotating file handler และ console handler (กำหนดได้ผ่าน env)
- Log file อยู่ที่ `logs/backend.log`
- `PII_MASKING_ENABLED=false` จะข้ามขั้นตอนเบลอ แต่ metadata จะบอกสถานะ
- OCR service log ว่าใช้ device ประเภทใด (`cpu`, `mps`, `cuda`)

## Troubleshooting
| อาการ | สาเหตุ | แนวทางแก้ |
| --- | --- | --- |
| `LLM processing failed` | Ollama ไม่รันหรือ URL/โมเดลผิด | ตรวจ `ollama list`, ทดสอบด้วย `curl $OLLAMA_BASE_URL/api/tags` |
| HTTP 503 (Ollama unavailable) | สั่ง `use_llm=true` แต่ backend ต่อ Ollama ไม่ได้ | ตรวจสอบบริการ Ollama, พอร์ต 11434, หรือปิด LLM (env หรือ `use_llm=false`) |
| HTTP 415 | Content-Type ไม่ใช่ภาพ | ส่ง `.jpg/.jpeg/.png` เท่านั้น |
| HTTP 413 | ไฟล์ใหญ่เกิน | ปรับ `MAX_FILE_SIZE_MB` แล้ว restart |
| ตัวสะกดเพี้ยน | ภาพเบลอหรือมี glare | ถ่ายใหม่/เพิ่ม preprocess ใน `ocr_service.py` |

## Documentation
- [docs/backend.md](docs/backend.md) — สรุปสถาปัตยกรรม backend, ขั้นตอน OCR/LLM, logging, security, และแนวทางทดสอบ
- [docs/frontend.md](docs/frontend.md) — โรดแมป UI, โครงสร้างคอมโพเนนต์, แนวคิด state และสไตล์สำหรับ Next.js

## Contributing & License
1. Fork repo และสร้าง branch (`feat/...`, `fix/...`)
2. เพิ่มหรืออัปเดตเทส + README หากมี breaking change
3. ส่ง PR พร้อมรายละเอียดและผลเทส

โครงการยังไม่ระบุ License หากต้องการใช้เชิงพาณิชย์ กรุณาเปิด Issue เพื่อพูดคุยเพิ่มเติม
