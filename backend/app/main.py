from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.services.ocr_service import process_id_card 
from app.services.llm_service import clean_data_with_llm

app = FastAPI(title="Thai ID Card OCR API (AI Powered)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "success", "message": "API with LLM is running!"}

@app.post("/api/v1/extract-id")
async def extract_id_card(image: UploadFile = File(...)):
    image_bytes = await image.read()
    try:
        # 1. ให้ EasyOCR อ่านภาพ (ได้เป็น Raw Text)
        ocr_result = process_id_card(image_bytes)
        raw_text = ocr_result["raw_text"]
        
        # 2. ส่ง Raw Text ไปให้ LLM (Ollama) แก้คำผิดและจัดฟอร์แมต JSON
        ai_cleaned_data = clean_data_with_llm(raw_text)
        
        return {
            "status": "success",
            "message": f"Processed: {image.filename}",
            "data": ai_cleaned_data,
            "debug": {
                "raw_text": raw_text
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
