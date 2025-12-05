# =================================================================
# manual_entry.py (50 لونًا)
# =================================================================
import random
import hashlib

# تعيينات الألوان (A1-J5) = 50 لونًا
COLOR_MAPPING_SIMPLIFIED = {}
color_id = 1
# نستخدم حروف A-J (10 حروف) و أرقام 1-5 (5 أرقام) = 50 تركيبة
letters = "ABCDEFGHIJ" 
numbers = "12345"

for l in letters:
    for n in numbers:
        COLOR_MAPPING_SIMPLIFIED[l + n] = color_id
        color_id += 1

# الرموز الخاصة
COLOR_MAPPING_SIMPLIFIED['?'] = 99
COLOR_MAPPING_SIMPLIFIED['Q'] = 99
COLOR_MAPPING_SIMPLIFIED['E'] = 0

def get_mapping_table_text_simplified():
    """ينشئ جدول نصي لتبسيط الإدخال اليدوي للألوان."""
    header = "رمز الإدخال | الرقم المخصص (ID)"
    separator = "---|---"
    rows = []
    
    # عرض جزء من الأكواد لتوجيه المستخدم
    for code, value in list(COLOR_MAPPING_SIMPLIFIED.items())[:15]: 
        if value > 0 and value < 99:
             rows.append(f"`{code}` | {value}")
    
    rows.append("... (إجمالي 50 لونًا)")
    rows.append("`?` | إشارة استفهام/مجهول (ID 99)")
             
    return "الرجاء استخدام الأكواد المختصرة التالية (بدون فواصل):\n" + header + "\n" + separator + "\n" + "\n".join(rows)

def parse_manual_input(input_text):
    """
    تحويل النص المدخل من المستخدم (مثال: A1,B2,C3-D4,E5,F1) إلى قائمة قوائم رقمية.
    """
    try:
        bottle_strings = input_text.upper().replace(' ', '').split('-')
        parsed_state = []
        
        for bottle_str in bottle_strings:
            bottle_state = []
            # كل رمز مكون من حرف ورقم (طول 2)
            symbols = [bottle_str[i:i+2] for i in range(0, len(bottle_str), 2)]
            
            for symbol in [s for s in symbols if s]:
                if symbol in COLOR_MAPPING_SIMPLIFIED:
                    bottle_state.append(COLOR_MAPPING_SIMPLIFIED[symbol])
                else:
                    raise ValueError(f"رمز لون غير صالح: {symbol}. (الأكواد المتوقعة هي A1-J5)")
            
            # يتم عكس القائمة (لأن الإدخال يكون من الأعلى للأدنى في هذه الدالة)
            bottle_state.reverse() 
            parsed_state.append(bottle_state)
            
        return parsed_state

    except Exception as e:
        return None, str(e)

def parse_single_bottle_correction(input_text):
    """
    تحليل إدخال التصحيح: "تصحيح 5: A1,B2,C3,D4"
    المدخلات: رقم_الزجاجة:اللون1,اللون2,اللون3,اللون4 (من الأعلى إلى الأسفل)
    """
    try:
        if not input_text.lower().startswith("تصحيح"):
            return None, None, "يجب أن تبدأ الرسالة بكلمة 'تصحيح'."
            
        # تقسيم النص
        parts = input_text.replace(':', ' ').replace(',', ' ').upper().split()
        
        if len(parts) < 3: 
             return None, None, "صيغة الإدخال غير صحيحة. استخدم: تصحيح رقم_الزجاجة:A1,B2,C3,D4"

        bottle_index = int(parts[1]) - 1 
        
        new_shapes = []
        # كل لون هو رمز مكون من حرف ورقم (طول 2)
        symbols = [p for p in parts[2:] if p]
        
        for symbol in symbols:
            if symbol in COLOR_MAPPING_SIMPLIFIED:
                new_shapes.append(COLOR_MAPPING_SIMPLIFIED[symbol])
            else:
                return None, None, f"رمز لون غير صالح: {symbol}"
                
        return bottle_index, new_shapes, None
        
    except ValueError:
        return None, None, "الرجاء التأكد من أن رقم الزجاجة رقم صحيح."
    except Exception:
        return None, None, "صيغة الإدخال غير صحيحة. استخدم: تصحيح رقم_الزجاجة:A1,B2,C3,D4"
