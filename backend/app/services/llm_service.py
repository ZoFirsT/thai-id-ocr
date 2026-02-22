import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5"

def clean_data_with_llm(raw_text_list: list) -> dict:
    print("| กำลังส่งข้อมูลให้ LLM วิเคราะห์และแก้ไขคำผิด...")
    
    # แปลง List เป็น String เพื่อส่งให้ AI
    raw_text_str = "\n".join(raw_text_list)
    
    prompt = f"""
    คุณคือ AI ผู้เชี่ยวชาญด้านการตรวจสอบและแก้ไขข้อมูลบัตรประชาชนไทย
    นี่คือข้อความดิบที่ได้จากระบบ OCR ซึ่งอาจมีคำสะกดผิด หรืออ่านสระ/พยัญชนะผิดเพี้ยน:
    
    {raw_text_str}

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
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json" # บังคับให้ออกมาเป็น JSON
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # แปลงข้อความ JSON ที่ได้จาก AI กลับเป็น Dictionary
        cleaned_data = json.loads(result["response"])
        return cleaned_data
    except Exception as e:
        print(f"| LLM Error: {e}")
        return {"error": "ไม่สามารถประมวลผลด้วย LLM ได้", "details": str(e)}
