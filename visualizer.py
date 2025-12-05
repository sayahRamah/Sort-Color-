# =================================================================
# visualizer.py (50 لونًا مميزًا)
# =================================================================
from PIL import Image, ImageDraw, ImageFont
import io
import os
import hashlib
from manual_entry import COLOR_MAPPING_SIMPLIFIED # استيراد القاموس

MAX_CAPACITY = 4
BOTTLE_WIDTH = 60
SHAPE_HEIGHT = 45 
PADDING = 20
FONT_SIZE = 16

# إنشاء قاموس عكسي للوصول إلى رمز الإدخال من الرقم
REVERSED_MAPPING = {v: k for k, v in COLOR_MAPPING_SIMPLIFIED.items()}

# توليد 50 لون Hex فريد بناءً على الرقم ID
COLOR_MAP = {}
for i in range(1, 51):
    # استخدام تجزئة بسيطة لتوليد لون فريد من الرقم
    # هذا يضمن أن الألوان ستكون مختلفة ومستقرة في كل مرة تشغيل
    hex_color = hashlib.sha1(str(i).encode()).hexdigest()[:6]
    COLOR_MAP[i] = '#' + hex_color

# إضافة الألوان الخاصة
COLOR_MAP[99] = "#808080"  # رمادي للرمز ؟
COLOR_MAP[0] = "#F0F0F0"   # فارغ

def get_color_from_id(shape_id):
    """يسترجع اللون بناءً على الرقم ID."""
    return COLOR_MAP.get(shape_id, 'black') 

def draw_puzzle_state(state, step_number=None, move=None):
    """تحويل الحالة الرقمية إلى صورة PNG."""
    NUM_BOTTLES = len(state)
    IMG_WIDTH = NUM_BOTTLES * (BOTTLE_WIDTH + PADDING) + PADDING
    IMG_HEIGHT = (PADDING * 2) + SHAPE_HEIGHT * MAX_CAPACITY + 50 

    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color='#F0F0F0') 
    draw = ImageDraw.Draw(img)
    
    try:
        # إذا لم يكن ملف الخط موجودًا، سيتم تحميل الافتراضي
        font = ImageFont.load_default() 
    except IOError:
        font = ImageFont.load_default()

    y_bottom = IMG_HEIGHT - PADDING - 10 
    
    for i, bottle in enumerate(state):
        x_start = i * (BOTTLE_WIDTH + PADDING) + PADDING
        
        # 1. رسم شكل الزجاجة
        draw.line([x_start, y_bottom, x_start, y_bottom - SHAPE_HEIGHT * MAX_CAPACITY], fill='black', width=3)
        draw.line([x_start + BOTTLE_WIDTH, y_bottom, x_start + BOTTLE_WIDTH, y_bottom - SHAPE_HEIGHT * MAX_CAPACITY], fill='black', width=3)
        draw.line([x_start, y_bottom, x_start + BOTTLE_WIDTH, y_bottom], fill='black', width=3)

        # 2. رسم الأشكال الملونة
        for j, shape_id in enumerate(bottle):
            color = get_color_from_id(shape_id) 
            
            y_shape_start = y_bottom - (j + 1) * SHAPE_HEIGHT
            y_shape_end = y_bottom - j * SHAPE_HEIGHT
            
            draw.rectangle(
                [x_start + 3, y_shape_start, x_start + BOTTLE_WIDTH - 3, y_shape_end],
                fill=color, outline='black'
            )
            
            if shape_id == 99:
                 draw.text((x_start + 15, y_shape_start + 10), "?", fill='white', font=font)

        # 3. كتابة رقم الزجاجة
        draw.text((x_start + BOTTLE_WIDTH / 2 - 5, y_bottom + 10), 
                  f"#{i+1}", fill='black', font=font)

    # 4. إضافة شرح الحركة
    if step_number is not None and move:
        source, target = move
        caption = f"الخطوة {step_number}: صب من الزجاجة #{source+1} إلى الزجاجة #{target+1}"
        draw.text((PADDING, 10), caption, fill='blue', font=font)
        
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
