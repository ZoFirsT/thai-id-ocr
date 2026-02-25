from PIL import Image, ImageDraw, ImageFont
import random
import os

def generate_thai_id(count=20):
    # สร้างโฟลเดอร์สำหรับเก็บรูปใน backend/dataset
    output_dir = "dataset"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    first_names = ["สมชาย", "วิชัย", "ธนัชชา", "อัญชลี", "กิตติ", "นงลักษณ์"]
    last_names = ["ใจดี", "มั่งคั่ง", "สาลีกงชัย", "รักไทย", "มั่นคง"]

    print(f"กำลังเริ่มสร้างบัตรประชาชนจำลองจำนวน {count} ใบ...")

    for i in range(count):
        # 1. สร้างพื้นหลังบัตรสีฟ้าอ่อน
        img = Image.new('RGB', (600, 380), color=(210, 240, 255))
        d = ImageDraw.Draw(img)

        # 2. สุ่มข้อมูล
        id_num = "".join([str(random.randint(0, 9)) for _ in range(13)])
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # 3. โหลดฟอนต์ (ถ้าไม่มีไฟล์ .ttf จะใช้ฟอนต์พื้นฐานซึ่งอาจไม่ชัด)
        try:
            # แนะนำให้เอาไฟล์ THSarabunNew.ttf มาวางไว้ในโฟลเดอร์ backend
            font = ImageFont.truetype("THSarabunNew.ttf", 40)
            font_small = ImageFont.truetype("THSarabunNew.ttf", 30)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 4. วาดข้อมูลลงบัตร
        d.text((40, 30), "Thai National ID Card", fill=(0, 50, 150), font=font_small)
        d.text((40, 100), f"เลขประจำตัวประชาชน: {id_num}", fill=(0, 0, 0), font=font)
        d.text((40, 180), f"ชื่อ: {name}", fill=(0, 0, 0), font=font)

        # 5. วาดกรอบรูปถ่าย
        d.rectangle([430, 80, 560, 280], outline=(150, 150, 150), width=3)

        # 6. บันทึกรูป
        filename = f"id_card_{i:03d}.png"
        img.save(os.path.join(output_dir, filename))
        
    print(f"🚀 สร้างบัตรเสร็จแล้ว {count} ใบ ที่โฟลเดอร์: {output_dir}")

if __name__ == "__main__":
    generate_thai_id(50)