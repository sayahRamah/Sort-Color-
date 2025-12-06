import os
import tempfile
from datetime import datetime
from PIL import Image
import cv2
import numpy as np

def create_temp_file(extension='.jpg'):
    """إنشاء ملف مؤقت"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)
    return os.path.join(temp_dir, f'temp_{timestamp}{extension}')

def cleanup_temp_files(max_age_minutes=10):
    """تنظيف الملفات المؤقتة القديمة"""
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        return
    
    current_time = datetime.now().timestamp()
    for filename in os.listdir(temp_dir):
        filepath = os.path.join(temp_dir, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > max_age_minutes * 60:
                os.remove(filepath)

def resize_image(image_path, max_size=(1024, 1024)):
    """تغيير حجم الصورة للحفاظ على الذاكرة"""
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        resized_path = create_temp_file('.jpg')
        img.save(resized_path, 'JPEG', quality=85)
        return resized_path
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_path

def rgb_to_emoji(color_name):
    """تحويل اسم اللون إلى إيموجي"""
    from config import COLOR_PALETTE
    return COLOR_PALETTE.get(color_name, ('❓', '#808080'))[0]

def emoji_to_rgb(emoji):
    """تحويل الإيموجي إلى لون RGB"""
    from config import COLOR_PALETTE
    for color_name, (color_emoji, color_hex) in COLOR_PALETTE.items():
        if color_emoji == emoji:
            return color_hex
    return '#808080'  # رمادي إذا لم يوجد

def format_move_description(step_num, from_bottle, to_bottle, color):
    """تنسيق وصف الخطوة"""
    return f"الخطوة {step_num}: صب اللون {color} من الزجاجة #{from_bottle + 1} إلى الزجاجة #{to_bottle + 1}"
