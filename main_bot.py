# =================================================================
# main_bot.py (الكود المعدل بالكامل)
# =================================================================
import telegram
# *** التعديل هنا: استيراد 'filters' بشكل منفصل ***
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import filters 
import os
import time

# استيراد الوظائف من الملفات الأخرى
from solver import solve_puzzle, state_to_tuple 
from image_processor import recognize_shapes_and_state 
from visualizer import draw_puzzle_state 
from manual_entry import (
    get_mapping_table_text_simplified, 
    parse_single_bottle_correction,
    parse_manual_input 
)

MAX_CAPACITY = 4
# -----------------
TOKEN = os.getenv('TOKEN') 
# -----------------

def start(update: Update, context: CallbackContext) -> None:
    """الرد على أمر /start."""
    update.message.reply_text(
        '👋 مرحباً! أنا هنا لحل ألغاز فرز الألوان (أدعم 50 لونًا!).\n\n'
        '**الخيار 1 (المُفضل):** أرسل صورة واضحة للغز.\n'
        '**الخيار 2:** إذا فشل التحليل، يمكنك التصحيح أو الإدخال اليدوي الكامل.',
        parse_mode=telegram.ParseMode.MARKDOWN
    )

def send_solution_steps(initial_state, chat_id, context):
    """حل اللغز وإرسال الصور خطوة بخطوة."""
    
    solution_path_with_states = solve_puzzle(initial_state) 
    
    if solution_path_with_states is None:
        context.bot.send_message(chat_id, "❌ لم أتمكن من إيجاد حل لهذا اللغز.")
        return
    
    context.bot.send_message(chat_id, f"✅ تم إيجاد الحل في **{len(solution_path_with_states)} خطوة!** سأرسل لك كل خطوة الآن.", parse_mode=telegram.ParseMode.MARKDOWN)

    initial_image_bytes = draw_puzzle_state(initial_state)
    context.bot.send_photo(chat_id, initial_image_bytes, caption="الحالة الأولية المؤكدة:")
    time.sleep(1)

    for k, (move, state_tuple) in enumerate(solution_path_with_states):
        current_state = [list(bottle) for bottle in state_tuple]
        image_bytes = draw_puzzle_state(current_state, k + 1, move)
        caption = f"الخطوة {k+1}: صب من الزجاجة #{move[0]+1} إلى الزجاجة #{move[1]+1}"
        
        context.bot.send_photo(chat_id, image_bytes, caption=caption)
        time.sleep(2) 

    context.bot.send_message(chat_id, "🥳 تهانينا! لقد تم حل اللغز بالكامل!")


def send_confirmation_image(state, chat_id, context):
    """إرسال الصورة البيانية للتأكيد النهائي."""
    image_bytes = draw_puzzle_state(state)
    
    keyboard = [[InlineKeyboardButton("✅ نعم، ابدأ الحل", callback_data='confirm_YES'),
                 InlineKeyboardButton("❌ لا، أخطأت", callback_data='confirm_NO')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
        chat_id, 
        image_bytes, 
        caption="تم تحديث الزجاجات. هل هذا الرسم يطابق اللغز الآن؟", 
        reply_markup=reply_markup
    )


def handle_photo(update: Update, context: CallbackContext) -> None:
    """معالجة الصور المرسلة."""
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, "⏳ جاري تحليل الصورة...")

    try:
        photo_file = update.message.photo[-1].get_file()
        file_path = f"/tmp/puzzle_{chat_id}.jpg"
        photo_file.download(file_path)
        
        initial_state = recognize_shapes_and_state(file_path)
        
        if initial_state is None:
            context.bot.send_message(chat_id, "⚠️ فشل التحليل. يرجى محاولة الإدخال اليدوي.")
            return
            
        initial_state_tuple = state_to_tuple(initial_state)
        context.user_data['initial_state'] = initial_state_tuple
        context.user_data['state_status'] = 'awaiting_confirmation'

        send_confirmation_image(initial_state, chat_id, context)

    except Exception as e:
        print(f"حدث خطأ في handle_photo: {e}")
        context.bot.send_message(chat_id, f"❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")

def handle_text_input(update: Update, context: CallbackContext) -> None:
    """معالجة الأوامر النصية للتصحيح أو الإدخال اليدوي الكامل."""
    chat_id = update.message.chat_id
    input_text = update.message.text
    
    # 1. معالجة أمر التصحيح المباشر: تصحيح 5:A1,B2,C3,D4
    if input_text.lower().startswith("تصحيح"):
        if 'initial_state' not in context.user_data or context.user_data.get('state_status') != 'awaiting_correction':
             context.bot.send_message(chat_id, "❌ لا يوجد تحليل بصري خاطئ حالياً لتصحيحه. يرجى إرسال صورة أولاً.")
             return
             
        bottle_index, new_shapes, error = parse_single_bottle_correction(input_text)
        
        if error:
            context.bot.send_message(chat_id, f"❌ خطأ في الإدخال: {error}")
            return
            
        initial_state_tuple = context.user_data.get('initial_state')
        initial_state = [list(bottle) for bottle in initial_state_tuple]
        
        new_shapes_processed = list(reversed(new_shapes[:MAX_CAPACITY])) 
        
        if 0 <= bottle_index < len(initial_state):
            initial_state[bottle_index] = new_shapes_processed
            
            context.user_data['initial_state'] = state_to_tuple(initial_state)
            context.user_data['state_status'] = 'awaiting_confirmation'
            
            send_confirmation_image(initial_state, chat_id, context)
            
        else:
             context.bot.send_message(chat_id, f"رقم الزجاجة خارج النطاق.")
        return

    # 2. معالجة الإدخال اليدوي الكامل
    elif context.user_data.get('state_status') == 'awaiting_manual_input_full':
        initial_state, error = parse_manual_input(input_text)
        
        if initial_state is None:
            context.bot.send_message(chat_id, f"❌ فشل تحليل المدخلات. الخطأ: {error}")
            return
            
        context.user_data['initial_state'] = state_to_tuple(initial_state)
        context.user_data['state_status'] = 'awaiting_confirmation'
        context.bot.send_message(chat_id, "✅ تم قبول الإدخال اليدوي! جاري التحقق النهائي...")

        send_confirmation_image(initial_state, chat_id, context)
        return
        
    else:
        context.bot.send_message(chat_id, "أرسل صورة أو استخدم أمر /start.")

def button_callback(update: Update, context: CallbackContext) -> None:
    """معالجة ضغط الأزرار."""
    query = update.callback_query
    query.answer() 
    chat_id = query.message.chat_id
    data = query.data
    
    if data.startswith('confirm_'):
        initial_state_tuple = context.user_data.get('initial_state')
        if not initial_state_tuple: return query.edit_message_text("❌ انتهت صلاحية هذه العملية.")
        initial_state = [list(bottle) for bottle in initial_state_tuple]

        action = data.split('_')[1]
        
        if action == 'YES':
            query.edit_message_text("✅ تم التأكيد. جاري البحث عن الحل...")
            context.user_data['state_status'] = 'solving'
            send_solution_steps(initial_state, chat_id, context)

        elif action == 'NO':
            context.user_data['state_status'] = 'awaiting_correction'
            
            manual_keyboard = [
                [InlineKeyboardButton("عرض جدول الأكواد (A1-J5)", callback_data='manual_SHOW')],
                [InlineKeyboardButton("أدخل اللغز كاملاً يدوياً", callback_data='manual_FULL')]
            ]
            manual_markup = InlineKeyboardMarkup(manual_keyboard)
            
            query.edit_message_text(
                "😔 آسف للخطأ. يرجى اتباع أحد الخيارات:\n\n"
                "**1. التصحيح المباشر:** أرسل أمر بالصيغة: `تصحيح رقم_الزجاجة:A1,B2,...` (الألوان من الأعلى إلى الأسفل).\n"
                "**2. الإدخال الكامل:** اضغط على الزر أدناه.",
                reply_markup=manual_markup, parse_mode=telegram.ParseMode.MARKDOWN
            )

    elif data == 'manual_SHOW':
         query.edit_message_text(get_mapping_table_text_simplified(), parse_mode=telegram.ParseMode.MARKDOWN)
    
    elif data == 'manual_FULL':
         context.user_data['state_status'] = 'awaiting_manual_input_full'
         query.edit_message_text("الرجاء إرسال حالة اللغز بالكامل بالصيغة: `A1B2C3D4-E5F1G2H3-...`\n\n**ملاحظة:** كل لون هو رمزان (حرف ورقم) ولا يوجد فواصل بين الألوان في نفس الزجاجة.")


def main():
    """الدالة الرئيسية لتشغيل البوت."""
    if not TOKEN:
        print("🚨 خطأ: لم يتم العثور على توكن البوت. يجب تعيين متغير البيئة 'TOKEN'.")
        return

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    
    # *** التعديل هنا: استخدام filters.PHOTO ***
    dp.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # *** التعديل هنا: استخدام filters.TEXT و filters.COMMAND ***
    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    dp.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 البوت يعمل الآن ويستمع لتيليجرام...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # لتجنب خطأ الاستيراد الدوري
    import manual_entry
    main()
