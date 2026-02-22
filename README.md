# 🇹🇭 Thai ID Card OCR API

> FastAPI + EasyOCR + Ollama (Qwen2.5) สำหรับอ่านและจัดระเบียบข้อมูลจากบัตรประชาชนไทยแบบ **Local-first** ไม่ต้องส่งข้อมูลออกนอกเครื่อง

## ✨ ภาพรวมโปรเจกต์
- ใช้ **EasyOCR** อ่านตัวอักษรไทย/อังกฤษจากรูปถ่ายบัตร
- ส่งผลลัพธ์ดิบให้ **Ollama (Qwen2.5)** เพื่อแก้คำผิดและจัดเป็น JSON ที่พร้อมใช้งาน
- มี REST API ผ่าน **FastAPI** พร้อม Swagger UI ให้ลองยิงทันที
- เหมาะสำหรับระบบ On-Premise / Edge ที่ต้องการความเป็นส่วนตัวของข้อมูลระดับสูง

## 🧱 โครงสร้างระบบ (High-level Flow)
```
Image Upload → FastAPI → EasyOCR → Raw Text
                           ↓
                      Ollama (Qwen2.5)
                           ↓
                        Clean JSON
```

## ✅ คุณสมบัติหลัก
1. รองรับไฟล์ภาพนามสกุลยอดนิยม (.jpg, .jpeg, .png)
2. มี Field สำคัญ: เลขบัตร, ชื่อ-นามสกุล (TH/EN), วันเกิด, ศาสนา, ที่อยู่
3. มี `debug.raw_text` สำหรับตรวจสอบผล OCR แบบไม่ผ่าน LLM
4. ออกแบบให้ Deploy ง่ายบนเครื่องส่วนตัวหรือ VM ใดๆ ที่มี Python 3.10+

## � โครงสร้างโฟลเดอร์ (ย่อ)
```
thai-id-ocr/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── services/
│   │   │   ├── ocr_service.py   # EasyOCR, image preprocessing
│   │   │   └── llm_service.py   # เชื่อมต่อ Ollama / Qwen2.5
│   └── requirements.txt
└── frontend/                    # (เตรียมสำหรับ UI ในอนาคต)
```

## 🔧 ความต้องการระบบ
- Python 3.10 หรือใหม่กว่า
- pip / virtualenv
- [Ollama](https://ollama.com) ที่ติดตั้งโมเดล **qwen2.5** (รันในเครื่อง)
- RAM 4GB+, แนะนำ 8GB+ เพื่อรองรับ EasyOCR

## 🚀 Quick Start

### 1) ติดตั้งและเตรียม Ollama + โมเดล Qwen2.5
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5
ollama run qwen2.5   # ให้โมเดลเริ่มฟังที่พอร์ต 11434 (ค่าเริ่มต้น)
```

### 2) ติดตั้งโค้ด FastAPI
```bash
git clone https://github.com/ZoFirsT/thai-id-ocr.git
cd thai-id-ocr/backend

# (แนะนำ) สร้าง Virtual Env
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API Base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

> 💡 หาก Ollama ไม่รันอยู่ที่ `http://localhost:11434` สามารถแก้ URL หรือชื่อโมเดลใน `app/services/llm_service.py`

## 📡 API Usage
- Method: `POST`
- Endpoint: `/api/v1/extract-id`
- Content-Type: `multipart/form-data`
- Field: `image` (แนบไฟล์บัตรประชาชน)

### ตัวอย่าง cURL
```bash
curl -X POST http://localhost:8000/api/v1/extract-id \
  -F "image=@/path/to/thai-id-card.jpg"
```

### ตัวอย่าง Response
```json
{
  "status": "success",
  "message": "Processed: thai-id-card.jpg",
  "data": {
    "id_number": "1234567890123",
    "name_th": "นาย สมชาย ใจดี",
    "name_en": "MR. SOMCHAI JAIDEE",
    "dob": "17 ม.ค. 2545",
    "religion": "พุทธ",
    "address": "123 หมู่ 4 แขวงบางรัก เขตบางรัก กรุงเทพฯ 10500"
  },
  "debug": {
    "raw_text": ["นาย", "สมชาย", "..."]
  }
}
```

## ⚙️ การปรับแต่ง
| รายการ | ไฟล์/ตำแหน่ง | คำอธิบาย |
| --- | --- | --- |
| พอร์ต FastAPI | `uvicorn app.main:app --reload --host 0.0.0.0 --port 9000` | ปรับเวลาใช้งานจริง/หลัง Reverse Proxy |
| ปรับโมเดล LLM | `app/services/llm_service.py` (`MODEL_NAME`, `OLLAMA_URL`) | รองรับโมเดลอื่นใน Ollama ได้ทันที |
| ตัวเลือก EasyOCR | `app/services/ocr_service.py` | สามารถเปิด GPU (`gpu=True`) หรือเพิ่มภาษา |

## 🧪 การทดสอบอย่างง่าย
1. เปิด `http://localhost:8000/docs`
2. เลือก `POST /api/v1/extract-id`
3. แนบรูปภาพจริงหรือ mockup เพื่อดูค่าที่ระบบอ่านได้

## 🩺 Troubleshooting
| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
| --- | --- | --- |
| API ตอบ `LLM Error` | Ollama ไม่ได้รัน / URL ผิด | ตรวจสอบ `ollama list`, ดู log ที่เทอร์มินัลที่รันโมเดล |
| อ่านตัวอักษรเพี้ยนมาก | ภาพเบลอ/มืด หรือยังไม่ Preprocess | ปรับภาพให้คมชัดขึ้น หรือเพิ่มขั้นตอน preprocess ใน `ocr_service.py` |
| Import EasyOCR ไม่ได้ | ระบบขาด libopencv (โดยเฉพาะบน Linux) | ติดตั้ง `libgl1`, `ffmpeg` หรือรันใน Docker/venv ที่มี lib ครบ |

## 🤝 Contributing
1. Fork โปรเจกต์
2. สร้าง branch ใหม่ (`feat/...` หรือ `fix/...`)
3. เพิ่ม/อัปเดตเทส + README หากจำเป็น
4. ส่ง Pull Request พร้อมรายละเอียดการเปลี่ยนแปลง

## 📜 License
ยังไม่กำหนด (TBD) – หากต้องการใช้งานในเชิงพาณิชย์ โปรดระบุใน Issue เพื่อพูดคุยรายละเอียด

---

หากมีคำถาม/ข้อเสนอแนะเกี่ยวกับ Thai ID OCR โปรดเปิด Issue หรือ PR ได้เลย 🙌