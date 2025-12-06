def validate_bottle_count(count):
    """التحقق من عدد الزجاجات"""
    from config import MIN_BOTTLES, MAX_BOTTLES
    return MIN_BOTTLES <= count <= MAX_BOTTLES

def validate_color_count(count):
    """التحقق من عدد الألوان"""
    from config import MIN_COLORS, MAX_COLORS
    return MIN_COLORS <= count <= MAX_COLORS

def validate_puzzle_state(state):
    """التحقق من حالة اللغز"""
    if not state or not isinstance(state, list):
        return False, "الحالة غير صالحة"
    
    total_slots = len(state) * 4  # افتراض سعة 4
    color_counts = {}
    
    for bottle in state:
        if len(bottle) > 4:
            return False, "زجاجة تحتوي على أكثر من 4 ألوان"
        
        for color in bottle:
            if color and color != 'EMPTY':
                color_counts[color] = color_counts.get(color, 0) + 1
    
    # التحقق من أن كل لون يظهر 4 مرات
    for color, count in color_counts.items():
        if count != 4:
            return False, f"اللون {color} يظهر {count} مرات بدلاً من 4"
    
    return True, "الحالة صالحة"

def calculate_empty_bottles(state):
    """حساب عدد الزجاجات الفارغة"""
    empty_count = 0
    for bottle in state:
        if all(color == 'EMPTY' or color is None for color in bottle):
            empty_count += 1
    return empty_count
