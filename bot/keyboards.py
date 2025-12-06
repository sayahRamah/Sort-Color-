from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    """لوحة المفاتيح الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("🆘 المساعدة", callback_data='help'),
         InlineKeyboardButton("ℹ️ معلومات", callback_data='info')],
        [InlineKeyboardButton("🎮 حل لغز جديد", callback_data='new_game')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard():
    """لوحة تأكيد اللغز"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، ابدأ الحل", callback_data='confirm_solve')],
        [InlineKeyboardButton("❌ لا، أعد المحاولة", callback_data='retry')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_solution_controls_keyboard():
    """أزرار التحكم بعرض الحل"""
    keyboard = [
        [InlineKeyboardButton("⏭️ التالي", callback_data='next_step'),
         InlineKeyboardButton("⏹️ إيقاف", callback_data='stop_solution')],
        [InlineKeyboardButton("📋 كل الخطوات", callback_data='all_steps')]
    ]
    return InlineKeyboardMarkup(keyboard)
