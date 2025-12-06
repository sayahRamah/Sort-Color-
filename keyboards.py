from languages import LANGUAGES
from colors import QUICK_COLORS, COLOR_SYSTEM

def get_language_keyboard():
    """لوحة اختيار اللغة"""
    keyboard = []
    
    # صفين
    row1 = []
    row2 = []
    
    for i, (lang_code, lang_data) in enumerate(LANGUAGES.items()):
        button = {
            'text': f"{lang_data['flag']} {lang_data['name']}",
            'callback_data': f"lang_{lang_code}"
        }
        
        if i < 2:
            row1.append(button)
        else:
            row2.append(button)
    
    if row1:
        keyboard.append(row1)
    if row2:
        keyboard.append(row2)
    
    return {'inline_keyboard': keyboard}

def get_bottles_keyboard(language):
    """لوحة اختيار عدد الزجاجات"""
    lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
    
    keyboard = []
    # صفوف من 4 أزرار
    buttons = []
    for i in range(5, 17):  # من 5 إلى 16
        buttons.append({
            'text': str(i),
            'callback_data': f"bottles_{i}"
        })
        if len(buttons) == 4:
            keyboard.append(buttons)
            buttons = []
    
    if buttons:
        keyboard.append(buttons)
    
    # زر للخيارات الأخرى
    keyboard.append([
        {'text': '17-20', 'callback_data': 'more_bottles'}
    ])
    
    return {'inline_keyboard': keyboard}

def get_empty_bottles_keyboard(total_bottles, language):
    """لوحة اختيار الزجاجات الفارغة"""
    lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
    
    max_empty = min(total_bottles - 2, 5)  # على الأقل زجاجتان فارغتان
    
    keyboard = []
    row = []
    for i in range(max_empty + 1):
        row.append({
            'text': str(i),
            'callback_data': f"empty_{i}"
        })
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # زر الرجوع
    keyboard.append([
        {'text': lang_data['back'], 'callback_data': 'back_bottles'}
    ])
    
    return {'inline_keyboard': keyboard}

def get_color_keyboard(language, session_data=None):
    """لوحة أزرار الألوان"""
    lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
    
    keyboard = []
    
    # الألوان السريعة (4 صفوف)
    for i in range(0, len(QUICK_COLORS), 4):
        row = []
        for emoji in QUICK_COLORS[i:i+4]:
            # البحث عن معرف اللون
            color_id = None
            for cid, data in COLOR_SYSTEM.items():
                if data['emoji'] == emoji:
                    color_id = cid
                    break
            
            if color_id:
                row.append({
                    'text': emoji,
                    'callback_data': f"color_{color_id}"
                })
        
        if row:
            keyboard.append(row)
    
    # أزرار التحكم
    control_row = [
        {'text': '⬜', 'callback_data': 'color_EMPTY'},
        {'text': lang_data['delete_last'], 'callback_data': 'action_delete'},
        {'text': lang_data['clear_bottle'], 'callback_data': 'action_clear'}
    ]
    
    # إذا كانت الزجاجة مكتملة
    if session_data and len(session_data.get('current_bottle_colors', [])) == 4:
        control_row.append({'text': lang_data['done'], 'callback_data': 'action_done'})
    
    keyboard.append(control_row)
    
    # زر عرض المزيد
    keyboard.append([
        {'text': lang_data['all_colors'], 'callback_data': 'action_all_colors'}
    ])
    
    return {'inline_keyboard': keyboard}

def get_more_bottles_keyboard(language):
    """لوحة للأعداد الكبيرة من الزجاجات"""
    lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
    
    keyboard = [
        [
            {'text': '17', 'callback_data': 'bottles_17'},
            {'text': '18', 'callback_data': 'bottles_18'},
            {'text': '19', 'callback_data': 'bottles_19'},
            {'text': '20', 'callback_data': 'bottles_20'}
        ],
        [
            {'text': lang_data['back'], 'callback_data': 'back_to_bottles'}
        ]
    ]
    
    return {'inline_keyboard': keyboard}

def get_all_colors_keyboard(language, page=0):
    """لوحة عرض كل الألوان (مقسمة إلى صفحات)"""
    lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
    
    # استبعاد الألوان الخاصة
    normal_colors = [cid for cid in COLOR_SYSTEM.keys() 
                     if cid not in ['EMPTY', 'UNKNOWN']]
    
    items_per_page = 16
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    
    current_colors = normal_colors[start_idx:end_idx]
    
    keyboard = []
    row = []
    
    for color_id in current_colors:
        color_data = COLOR_SYSTEM[color_id]
        row.append({
            'text': color_data['emoji'],
            'callback_data': f"color_{color_id}"
        })
        
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # أزرار التنقل بين الصفحات
    nav_row = []
    total_pages = (len(normal_colors) + items_per_page - 1) // items_per_page
    
    if page > 0:
        nav_row.append({
            'text': '◀️',
            'callback_data': f"colors_page_{page-1}"
        })
    
    nav_row.append({
        'text': f"{page+1}/{total_pages}",
        'callback_data': 'colors_info'
    })
    
    if page < total_pages - 1:
        nav_row.append({
            'text': '▶️',
            'callback_data': f"colors_page_{page+1}"
        })
    
    keyboard.append(nav_row)
    
    # زر العودة
    keyboard.append([
        {'text': lang_data['back'], 'callback_data': 'back_to_quick_colors'}
    ])
    
    return {'inline_keyboard': keyboard}
