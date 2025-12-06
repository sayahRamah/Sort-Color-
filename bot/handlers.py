from telegram import Update
from telegram.ext import ContextTypes
import os
from core.image_processor import ImageProcessor
from core.puzzle import PuzzleState
from core.solver import PuzzleSolver
from core.visualizer import PuzzleVisualizer
from utils.helpers import create_temp_file, resize_image, format_move_description
from utils.validators import validate_puzzle_state
from .keyboards import get_main_menu_keyboard, get_confirmation_keyboard, get_solution_controls_keyboard
from .states import UserState, UserSession

# تخزين الجلسات في الذاكرة (في الإنتاج استخدم قاعدة بيانات)
user_sessions = {}

def get_user_session(user_id):
    """الحصول على جلسة المستخدم أو إنشاء جديدة"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    return user_sessions[user_id]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر /start"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    session.reset()
    
    welcome_text = """
    🎮 **مرحباً بك في بوت حل لغز فرز الألوان!**
    
    **كيفية الاستخدام:**
    1. 📸 أرسل لي صورة للغز (سكرين شوت من اللعبة)
    2. 👀 سأرسم اللغز لك للتأكيد
    3. ✅ اضغط "نعم" لبدء الحل
    4. 📊 سأعرض لك الحل خطوة بخطوة
    
    **ملاحظات:**
    • اللغز يمكن أن يحتوي على 5-20 زجاجة
    • كل لون يظهر 4 مرات في اللغز
    • الألوان تحت علامة ❓ غير مرئية حتى تظهر
    
    **أرسل لي صورة الآن!** 📸
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
    session.state = UserState.WAITING_FOR_IMAGE

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الصور المرسلة"""
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    if session.state != UserState.WAITING_FOR_IMAGE:
        await update.message.reply_text("❌ الرجاء استخدام /start أولاً")
        return
    
    await update.message.reply_text("🔍 جاري تحليل الصورة...")
    
    try:
        # تحميل الصورة
        photo_file = await update.message.photo[-1].get_file()
        temp_path = create_temp_file('.jpg')
        await photo_file.download_to_drive(temp_path)
        
        # تغيير حجم الصورة للحفاظ على الذاكرة
        resized_path = resize_image(temp_path)
        
        # معالجة الصورة
        processor = ImageProcessor()
        puzzle_data = processor.process_image(resized_path)
        
        # التحقق من الحالة
        is_valid, message = validate_puzzle_state(puzzle_data)
        if not is_valid:
            await update.message.reply_text(f"❌ {message}\nالرجاء إرسال صورة أوضح.")
            os.remove(resized_path)
            return
        
        # حفظ الحالة
        session.puzzle_state = PuzzleState(puzzle_data)
        session.puzzle_image_path = resized_path
        session.state = UserState.IMAGE_RECEIVED
        
        # إنشاء صورة التأكيد
        visualizer = PuzzleVisualizer()
        confirm_image = visualizer.create_puzzle_image(puzzle_data, "هل هذه حالة اللغز الصحيحة؟")
        
        # حفظ الصورة مؤقتاً
        confirm_path = create_temp_file('.jpg')
        confirm_image.save(confirm_path, 'JPEG', quality=90)
        
        # إرسال الصورة للموافقة
        with open(confirm_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="**هل هذه حالة اللغز الصحيحة؟**\n\nإذا كانت الألوان غير صحيحة، يمكنك:\n1. إرسال صورة أوضح\n2. استخدام الإدخال اليدوي (/manual)",
                reply_markup=get_confirmation_keyboard(),
                parse_mode='Markdown'
            )
        
        session.state = UserState.CONFIRMING_PUZZLE
        
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ في معالجة الصورة: {str(e)}")
        session.state = UserState.WAITING_FOR_IMAGE

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة استدعاءات الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    if query.data == 'confirm_solve':
        if session.state == UserState.CONFIRMING_PUZZLE and session.puzzle_state:
            await query.edit_message_caption("⏳ جاري البحث عن الحل...")
            
            # حل اللغز
            solver = PuzzleSolver(session.puzzle_state)
            solution_path = solver.solve()
            
            if not solution_path:
                await query.edit_message_caption("❌ لم أتمكن من إيجاد حل لهذا اللغز.")
                session.reset()
                return
            
            session.solution = solver.get_solution_steps()
            session.state = UserState.SHOWING_SOLUTION
            session.current_step = 0
            
            # إرسال أول خطوة
            await send_solution_step(update, context, session)
            
        else:
            await query.edit_message_caption("❌ لم أجد حالة لغز. الرجاء إرسال صورة أولاً.")
    
    elif query.data == 'retry':
        await query.edit_message_caption("🔄 الرجاء إرسال صورة جديدة للغز.")
        session.state = UserState.WAITING_FOR_IMAGE
    
    elif query.data == 'next_step':
        if session.state == UserState.SHOWING_SOLUTION:
            session.current_step += 1
            if session.current_step < len(session.solution):
                await send_solution_step(update, context, session)
            else:
                await query.edit_message_caption("🎉 **تم حل اللغز بالكامل!**\n\nاستخدم /start للعبة جديدة.")
                session.reset()
    
    elif query.data == 'stop_solution':
        await query.edit_message_caption("⏹️ توقفت عن عرض الحل.\nاستخدم /start للعبة جديدة.")
        session.reset()
    
    elif query.data == 'help':
        help_text = """
        **🆘 المساعدة:**
        
        **مشكلة في الصور:**
        1. تأكد أن الصورة واضحة والزجابات مرئية
        2. حاول التقاط سكرين شوت مباشر من اللعبة
        3. تجنب الصور المظلمة أو المشوشة
        
        **الإدخال اليدوي:**
        استخدم /manual لإدخال اللغز يدوياً
        
        **مشاكل أخرى:**
        تواصل مع المطور @your_username
        
        **أوامر البوت:**
        /start - بدء محادثة جديدة
        /help - عرض هذه الرسالة
        /manual - الإدخال اليدوي للغز
        """
        await query.edit_message_caption(help_text, parse_mode='Markdown')
    
    elif query.data == 'info':
        info_text = """
        **ℹ️ معلومات عن البوت:**
        
        **المميزات:**
        ✅ حل تلقائي للغز فرز الألوان
        ✅ دعم 5-20 زجاجة
        ✅ دعم 4-15 لون مختلف
        ✅ عرض خطوات الحل مع الصور
        ✅ مجاني بالكامل
        
        **كيف يعمل:**
        1. يحلل صورة اللغز باستخدام الذكاء الاصطناعي
        2. يستخدم خوارزمية BFS لإيجاد أقصر حل
        3. يعرض النتائج خطوة بخطوة
        
        **المطور:** @your_username
        """
        await query.edit_message_caption(info_text, parse_mode='Markdown')
    
    elif query.data == 'new_game':
        await query.edit_message_caption("🎮 أرسل لي صورة للغز الجديد! 📸")
        session.reset()
        session.state = UserState.WAITING_FOR_IMAGE

async def send_solution_step(update, context, session):
    """إرسال خطوة من الحل"""
    step_info = session.solution[session.current_step]
    
    # إنشاء صورة الخطوة
    visualizer = PuzzleVisualizer()
    step_image = visualizer.create_solution_step_image(
        step_info,
        step_info['state_before']
    )
    
    # حفظ الصورة مؤقتاً
    step_path = create_temp_file('.jpg')
    step_image.save(step_path, 'JPEG', quality=90)
    
    # إعداد النص
    step_num = session.current_step + 1
    total_steps = len(session.solution)
    progress = f"({step_num}/{total_steps})"
    
    description = format_move_description(
        step_num,
        step_info['from'],
        step_info['to'],
        step_info['color']
    )
    
    caption = f"**{description}**\n\n{progress}"
    
    # إرسال الصورة
    with open(step_path, 'rb') as photo:
        if session.current_step == 0:
            # أول رسالة
            message = await update.callback_query.message.reply_photo(
                photo=photo,
                caption=caption,
                reply_markup=get_solution_controls_keyboard(),
                parse_mode='Markdown'
            )
            session.last_message_id = message.message_id
        else:
            # تحديث الرسالة السابقة
            await context.bot.edit_message_media(
                chat_id=update.effective_chat.id,
                message_id=session.last_message_id,
                media=InputMediaPhoto(photo)
            )
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id,
                message_id=session.last_message_id,
                caption=caption,
                reply_markup=get_solution_controls_keyboard(),
                parse_mode='Markdown'
            )

async def manual_input_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الإدخال اليدوي للغز"""
    await update.message.reply_text(
        "📝 **الإدخال اليدوي للغز:**\n\n"
        "أرسل اللغز بالتنسيق التالي:\n"
        "```\n"
        "الزجاجة 1: 🔴,🔴,🔵,🔵\n"
        "الزجاجة 2: 🟢,🟢,🟡,🟡\n"
        "الزجاجة 3: ⬜,⬜,⬜,⬜\n"
        "```\n\n"
        "استخدم ⬜ للفراغات",
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النصوص"""
    text = update.message.text.strip()
    
    if text.startswith('/'):
        return
    
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    
    # يمكن إضافة منطق الإدخال اليدوي هنا لاحقاً
    await update.message.reply_text(
        "📸 الرجاء إرسال صورة للغز أو استخدام /start",
        reply_markup=get_main_menu_keyboard()
    )
