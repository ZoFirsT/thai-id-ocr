import easyocr
import cv2
import numpy as np
import re

print("| กำลังโหลดโมเดล EasyOCR...")
reader = easyocr.Reader(['th', 'en'], gpu=False)
print("| โหลดโมเดล EasyOCR สำเร็จ!")

def preprocess_image(img):
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adjusted = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
    return adjusted

def extract_information(raw_text_list):
    data = {
        "id_number": None,
        "name_th": None,
        "name_en": None,
    }
    
    full_text_no_spaces = "".join(raw_text_list).replace(" ", "")
    
    # 1. ดึงเลขบัตรประชาชน
    id_match = re.search(r'\d{13}', full_text_no_spaces)
    if id_match:
        data["id_number"] = id_match.group()
        
    # 2. ดึงชื่อไทย
    for i, text in enumerate(raw_text_list):
        if ("นาย" in text or "นาง" in text) and "ชื่อตัว" in text:
            if i + 1 < len(raw_text_list):
                data["name_th"] = raw_text_list[i+1].strip()
            break
            
    for i, text in enumerate(raw_text_list):
        if text.lower().strip() in ["mr.", "miss", "mrs.", "mr", "mrs"]:
            en_name_parts = [text.strip()]  
            for j in range(i+1, min(i+5, len(raw_text_list))):
                word = raw_text_list[j].strip()
                if word.lower() in ["last name", "name"]:
                    continue
                if re.match(r'^[a-zA-Z\s]+$', word): 
                    en_name_parts.append(word)
            data["name_en"] = " ".join(en_name_parts)
            break

    return data

def process_id_card(image_bytes: bytes) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    processed_img = preprocess_image(img)
    raw_text_list = reader.readtext(processed_img, detail=0)
    extracted_data = extract_information(raw_text_list)
    return {"raw_text": raw_text_list, "extracted_data": extracted_data}
