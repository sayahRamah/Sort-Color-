#!/usr/bin/env python3
import logging
from config import TELEGRAM_TOKEN
from bot.handlers import (
    start_command,
    handle_photo,
    handle_callback_query,
    handle_text,
    manual_input_command
)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """الدالة الرئيسية لتشغيل البوت محلياً"""
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    # إنشاء التطبيق
    application = Application.builder().token(TEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('manual', manual_input_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # تشغيل البوت
    print("🤖 البوت يعمل... اضغط Ctrl+C لإيقافه")
    application.run_polling()

if __name__ == '__main__':
    main()
