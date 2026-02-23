import easyocr
import cv2
import numpy as np
import re
import difflib
import torch

def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return True
    return False

print("กำลังโหลดโมเดล EasyOCR (Optimized Mode)...")
device_type = get_device()
reader = easyocr.Reader(['th', 'en'], gpu=device_type)
print("โหลดโมเดล EasyOCR สำเร็จ!")

def preprocess_image(img):
    """ ปรับแต่งภาพขั้นสูงสำหรับบัตรประชาชนไทยที่มีโฮโลแกรม """
    # 1. ขยายภาพ 2 เท่า เพื่อให้สระไม่จม
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 2. แปลงเป็น Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. ใช้ CLAHE เพื่อเกลี่ยแสงที่สะท้อนไม่เท่ากันบนบัตร (ลดแสงแฟลช/เงา)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 4. ใช้ Bilateral Filter เพื่อเบลอลายน้ำทิ้ง แต่ขอบตัวอักษรยังคมกริบ
    denoised = cv2.bilateralFilter(enhanced, 11, 17, 17)
    
    return denoised

def auto_correct_thai_word(word: str, dictionary: list, cutoff: float = 0.6) -> str:
    """ ฟังก์ชันซ่อมคำผิดอัตโนมัติ (ไม่ต้องพึ่ง AI) """
    matches = difflib.get_close_matches(word, dictionary, n=1, cutoff=cutoff)
    return matches[0] if matches else word

def extract_information(raw_text_list):
    data = {
        "id_number": None,
        "name_th": None,
        "name_en": None,
        "religion": None
    }
    
    full_text_no_spaces = "".join(raw_text_list).replace(" ", "")
    
    # 1. ดึงเลขบัตร
    id_match = re.search(r'\d{13}', full_text_no_spaces)
    if id_match:
        data["id_number"] = id_match.group()
        
    for i, text in enumerate(raw_text_list):
        text_clean = text.strip()
        
        # 2. ดึงชื่อไทย (ป้องกันสระ/วรรณยุกต์เพี้ยนในคำนำหน้า)
        prefix_dict = ["นาย", "นาง", "นางสาว", "ชื่อตัวและชื่อสกุล"]
        matched_prefix = auto_correct_thai_word(text_clean.split()[0], prefix_dict, cutoff=0.7)
        
        if matched_prefix in ["นาย", "นาง", "นางสาว"] or "ชื่อตัว" in text_clean:
            if i + 1 < len(raw_text_list):
                raw_name = raw_text_list[i+1].strip()
                # ลบอักขระขยะที่ EasyOCR มักจะอ่านพลาดมา
                clean_name = re.sub(r'[!@#$%\^&*()_+=\[\]{};\'"\\|<>/?~]', '', raw_name)
                data["name_th"] = clean_name
            break
            
    # 3. ดึงชื่ออังกฤษ
    for i, text in enumerate(raw_text_list):
        if text.lower().strip() in ["mr.", "miss", "mrs.", "mr", "mrs"]:
            en_name_parts = [text.strip()]  
            for j in range(i+1, min(i+5, len(raw_text_list))):
                word = raw_text_list[j].strip()
                if word.lower() in ["last name", "name"]:
                    continue
                if re.match(r'^[a-zA-Z\s\.]+$', word): 
                    en_name_parts.append(word)
            data["name_en"] = " ".join(en_name_parts)
            break
            
    for text in raw_text_list:
        if "ศาสนา" in text:
            # สมมติว่าพบบรรทัดศาสนา ให้หาคำที่ใกล้เคียงที่สุดจากลิสต์
            religions = ["พุทธ", "อิสลาม", "คริสต์", "ฮินดู"]
            data["religion"] = auto_correct_thai_word(text.replace("ศาสนา", "").strip(), religions, cutoff=0.4)
            break

    return data

def process_id_card(image_bytes: bytes, enable_masking: bool = False) -> dict:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    processed_img = preprocess_image(img)
    
    # จูนพารามิเตอร์ EasyOCR 
    raw_text_list = reader.readtext(
        processed_img, 
        detail=0, 
        paragraph=False, # ห้ามจัดกลุ่ม paragraph เพราะภาษาไทยจะโดนหั่นผิด
        mag_ratio=1.5,   # ขยายภาพในระบบประสาทเทียมอีก 1.5 เท่า
        contrast_ths=0.1,# จับตัวอักษรจางๆ
        adjust_contrast=0.5 # เพิ่ม Contrast อัตโนมัติ
    )
    
    extracted_data = extract_information(raw_text_list)
    
    # ถ้าในอนาคตเขียนระบบ Masking ไว้ ค่อยมาแทรก Logic ตรงนี้ว่า 
    # if enable_masking: 
    #     ทำเซนเซอร์รูปภาพ
    
    return {"raw_text": raw_text_list, "extracted_data": extracted_data}