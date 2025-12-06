from flask import Flask, request, jsonify
import os
import logging
import json
from datetime import datetime
import pytz
import traceback

from config import TELEGRAM_TOKEN, ADMIN_USER_ID
from database import db
from languages import LANGUAGES
from colors import COLOR_SYSTEM, get_color_emoji
from keyboards import (
    get_language_keyboard,
    get_bottles_keyboard,
    get_empty_bottles_keyboard,
    get_color_keyboard,
    get_more_bottles_keyboard,
    get_all_colors_keyboard
)

app = Flask(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """إرسال رسالة لتلجرام"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set")
        return None
    
    try:
        import requests
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

def send_to_admin(message):
    """إرسال رسالة للمالك"""
    if not ADMIN_USER_ID:
        return
    
    send_telegram_message(ADMIN_USER_ID, message)

def notify_new_user(user_data):
    """إشعار المالك بمستخدم جديد"""
    try:
        time_str = datetime.fromisoformat(
            user_data['first_seen'].replace('Z', '+00:00')
        ).strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
👤 *مستخدم جديد بدأ البوت*

🆔 المعرف: `{user_data['user_id']}`
👤 الاسم: {user_data['first_name']}
📛 المستخدم: @{user_data.get('username', 'N/A')}
🌍 اللغة: {LANGUAGES.get(user_data.get('language', 'ar'), {}).get('name', 'Unknown')}
🕐 الوقت: {time_str}

📊 الإحصائيات:
• المستخدمون النشطون: {len(db.users)}
• البدءات اليوم: {db.get_daily_stats()['new_today']}
"""
        send_to_admin(message)
    except Exception as e:
        logger.error(f"Error notifying admin: {e}")

def update_session(chat_id, updates):
    """تحديث جلسة المستخدم"""
    session = db.get_session(chat_id) or {}
    session.update(updates)
    db.save_session(chat_id, session)
    return session

def get_bottle_display(bottle_colors):
    """عرض محتويات الزجاجة"""
    display = []
    for color_id in bottle_colors:
        emoji = get_color_emoji(color_id)
        display.append(emoji)
    
    # إكمال حتى 4
    while len(display) < 4:
        display.append('▫️')
    
    return ' '.join(display)

@app.route('/')
def home():
    stats = db.get_daily_stats()
    return f"""
    <html>
    <head>
        <title>🤖 Water Sort Puzzle Bot</title>
        <style>
            body {{ font-family: Arial; text-align: center; padding: 50px; }}
            .stats {{ background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px; }}
        </style>
    </head>
    <body>
        <h1>🤖 بوت حل لغز فرز الألوان</h1>
        <p>🌍 متعدد اللغات | 🎮 واجهة أزرار ذكية</p>
        
        <div class="stats">
            <h3>📊 الإحصائيات</h3>
            <p>👥 إجمالي المستخدمين: {stats['total_users']}</p>
            <p>👤 النشطون اليوم: {stats['active_today']}</p>
            <p>🆕 الجدد اليوم: {stats['new_today']}</p>
        </div>
        
        <p>📱 افتح تلجرام وأرسل <code>/start</code></p>
        <p>👑 المطور: @Messilorian</p>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة webhook من تلجرام"""
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "TELEGRAM_TOKEN not set"}), 400
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {json.dumps(data, ensure_ascii=False)[:200]}...")
        
        # معالجة callback queries (أزرار الإنلاين)
        if 'callback_query' in data:
            return handle_callback_query(data['callback_query'])
        
        # معالجة الرسائل العادية
        if 'message' in data:
            return handle_message(data['message'])
        
        return jsonify({"status": "no message"})
    
    except Exception as e:
        logger.error(f"Error in webhook: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

def handle_callback_query(callback):
    """معالجة ضغطات الأزرار"""
    try:
        import requests
        
        chat_id = str(callback['message']['chat']['id'])
        message_id = callback['message']['message_id']
        user_id = callback['from']['id']
        username = callback['from'].get('username', '')
        first_name = callback['from'].get('first_name', '')
        callback_data = callback.get('data', '')
        
        # إجابة على callback أولاً
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery',
            json={'callback_query_id': callback['id']}
        )
        
        logger.info(f"Callback: {callback_data} from {user_id}")
        
        # الحصول على الجلسة
        session = db.get_session(chat_id) or {}
        language = session.get('language', 'ar')
        lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
        
        # معالجة أنواع الأزرار المختلفة
        if callback_data.startswith('lang_'):
            # اختيار اللغة
            language = callback_data.split('_')[1]
            
            # تتبع المستخدم
            user_data = db.track_user_start(user_id, username, first_name, language)
            if user_data.get('start_count', 0) == 1:
                notify_new_user(user_data)
            
            # حفظ اللغة في الجلسة
            session = update_session(chat_id, {
                'language': language,
                'step': 'select_bottles',
                'user_id': user_id
            })
            
            # إرسال رسالة اختيار الزجاجات
            lang_data = LANGUAGES.get(language, LANGUAGES['ar'])
            send_telegram_message(
                chat_id,
                f"{lang_data['flag']} *{lang_data['select_bottles']}*",
                get_bottles_keyboard(language)
            )
        
        elif callback_data.startswith('bottles_'):
            # اختيار عدد الزجاجات
            if callback_data == 'more_bottles':
                send_telegram_message(
                    chat_id,
                    lang_data['select_bottles'],
                    get_more_bottles_keyboard(language)
                )
                return jsonify({"status": "more_bottles"})
            
            num_bottles = int(callback_data.split('_')[1])
            
            session = update_session(chat_id, {
                'total_bottles': num_bottles,
                'step': 'select_empty',
                'bottles': [],
                'current_bottle': 1
            })
            
            # إرسال رسالة اختيار الزجاجات الفارغة
            send_telegram_message(
                chat_id,
                f"*{lang_data['select_empty']}*\n(0-{min(num_bottles-2, 5)})",
                get_empty_bottles_keyboard(num_bottles, language)
            )
        
        elif callback_data.startswith('empty_'):
            # اختيار عدد الزجاجات الفارغة
            empty_count = int(callback_data.split('_')[1])
            
            session = update_session(chat_id, {
                'empty_bottles': empty_count,
                'step': 'filling_bottle',
                'current_bottle_colors': [],
                'color_counters': {}
            })
            
            # بدء إدخال الزجاجة الأولى
            bottle_num = session.get('current_bottle', 1)
            send_telegram_message(
                chat_id,
                f"*{lang_data['bottle_num']} {bottle_num}:*\n{lang_data['select_color']}",
                get_color_keyboard(language, session)
            )
        
        elif callback_data.startswith('color_'):
            # اختيار لون
            color_id = callback_data.split('_')[1]
            session = db.get_session(chat_id) or {}
            
            if 'current_bottle_colors' not in session:
                session['current_bottle_colors'] = []
            
            if len(session['current_bottle_colors']) < 4:
                # إضافة اللون
                session['current_bottle_colors'].append(color_id)
                
                # تحديث العداد
                color_counters = session.get('color_counters', {})
                color_counters[color_id] = color_counters.get(color_id, 0) + 1
                session['color_counters'] = color_counters
                
                db.save_session(chat_id, session)
                
                # تحديث الرسالة
                bottle_display = get_bottle_display(session['current_bottle_colors'])
                remaining = 4 - len(session['current_bottle_colors'])
                
                message_text = f"""
*{lang_data['bottle_num']} {session.get('current_bottle', 1)}:*
{bottle_display}

{lang_data['remaining']}: {remaining} {lang_data['of']} 4
"""
                requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText',
                    json={
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'text': message_text,
                        'parse_mode': 'Markdown',
                        'reply_markup': get_color_keyboard(language, session)
                    }
                )
        
        elif callback_data == 'action_delete':
            # حذف آخر لون
            session = db.get_session(chat_id)
            if session and session.get('current_bottle_colors'):
                last_color = session['current_bottle_colors'].pop()
                
                # تحديث العداد
                if last_color in session.get('color_counters', {}):
                    session['color_counters'][last_color] -= 1
                    if session['color_counters'][last_color] <= 0:
                        del session['color_counters'][last_color]
                
                db.save_session(chat_id, session)
                
                # تحديث الرسالة
                bottle_display = get_bottle_display(session['current_bottle_colors'])
                remaining = 4 - len(session['current_bottle_colors'])
                
                message_text = f"""
*{lang_data['bottle_num']} {session.get('current_bottle', 1)}:*
{bottle_display}

{lang_data['remaining']}: {remaining} {lang_data['of']} 4
"""
                requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText',
                    json={
                        'chat_id': chat_id,
                        'message_id': message_id,
                        'text': message_text,
                        'parse_mode': 'Markdown',
                        'reply_markup': get_color_keyboard(language, session)
                    }
                )
        
        elif callback_data == 'action_clear':
            # مسح الزجاجة الحالية
            session = db.get_session(chat_id)
            if session:
                session['current_bottle_colors'] = []
                db.save_session(chat_id, session)
                
                send_telegram_message(
                    chat_id,
                    f"*{lang_data['bottle_num']} {session.get('current_bottle', 1)}:*\n{lang_data['select_color']}",
                    get_color_keyboard(language, session)
                )
        
        elif callback_data == 'action_done':
            # إنهاء الزجاجة الحالية
            session = db.get_session(chat_id)
            if session and len(session.get('current_bottle_colors', [])) == 4:
                # حفظ الزجاجة
                if 'bottles' not in session:
                    session['bottles'] = []
                
                session['bottles'].append(session['current_bottle_colors'].copy())
                session['current_bottle_colors'] = []
                current_bottle = session.get('current_bottle', 1) + 1
                session['current_bottle'] = current_bottle
                
                total_bottles = session.get('total_bottles', 0)
                
                if current_bottle <= total_bottles:
                    # الانتقال للزجاجة التالية
                    db.save_session(chat_id, session)
                    
                    send_telegram_message(
                        chat_id,
                        f"✅ *{lang_data['success']}*\n\n*{lang_data['bottle_num']} {current_bottle}:*\n{lang_data['select_color']}",
                        get_color_keyboard(language, session)
                    )
                else:
                    # تم إدخال جميع الزجاجات
                    db.save_session(chat_id, session)
                    
                    # عرض ملخص اللغز
                    summary = f"📊 *{lang_data['solution_found'].split('!')[0]}!*\n\n"
                    for i, bottle in enumerate(session['bottles'], 1):
                        bottle_display = get_bottle_display(bottle)
                        summary += f"{i}. {bottle_display}\n"
                    
                    summary += f"\n🔍 {lang_data['solving']}"
                    
                    send_telegram_message(chat_id, summary)
                    
                    # هنا سنضيف خوارزمية الحل لاحقاً
                    # مؤقتاً نرسل رسالة تجريبية
                    import time
                    time.sleep(2)
                    
                    send_telegram_message(
                        chat_id,
                        f"🎉 *{lang_data['solution_found']}*\n\n⏱️ *12 {lang_data['steps']}*\n\n1. صب 🔴 من #1 → #3\n2. صب 🔵 من #2 → #5\n...\n\n{lang_data['next_game']}: /start",
                        get_color_keyboard(language, session)
                    )
        
        elif callback_data.startswith('colors_page_'):
            # التنقل بين صفحات الألوان
            page = int(callback_data.split('_')[2])
            send_telegram_message(
                chat_id,
                f"🎨 *{lang_data['all_colors']}*",
                get_all_colors_keyboard(language, page)
            )
        
        elif callback_data == 'action_all_colors':
            # عرض كل الألوان
            send_telegram_message(
                chat_id,
                f"🎨 *{lang_data['all_colors']}*",
                get_all_colors_keyboard(language, 0)
            )
        
        elif callback_data in ['back_bottles', 'back_to_bottles', 'back_to_quick_colors']:
            # العودة للخلف
            session = db.get_session(chat_id)
            if session:
                if 'step' in session:
                    if session['step'] == 'select_empty':
                        # العودة لاختيار عدد الزجاجات
                        session['step'] = 'select_bottles'
                        db.save_session(chat_id, session)
                        
                        send_telegram_message(
                            chat_id,
                            f"{lang_data['flag']} *{lang_data['select_bottles']}*",
                            get_bottles_keyboard(language)
                        )
        
        return jsonify({"status": "callback_processed"})
    
    except Exception as e:
        logger.error(f"Error in callback: {e}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

def handle_message(message):
    """معالجة الرسائل النصية"""
    chat_id = str(message['chat']['id'])
    user_id = message['from']['id']
    username = message['from'].get('username', '')
    first_name = message['from'].get('first_name', '')
    text = message.get('text', '').strip()
    
    if text == '/start':
        # عرض لوحة اختيار اللغة
        send_telegram_message(
            chat_id,
            "🌍 *اختر لغتك / Choose your language:*",
            get_language_keyboard()
        )
    
    elif text == '/stats' and str(user_id) == ADMIN_USER_ID:
        # إحصائيات للمالك
        stats = db.get_daily_stats()
        
        stats_text = f"""
📊 *إحصائيات البوت*

📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}
👥 إجمالي المستخدمين: {stats['total_users']}
👤 النشطون اليوم: {stats['active_today']}
🆕 الجدد اليوم: {stats['new_today']}

🌍 توزيع اللغات:
"""
        for lang_code, count in stats['languages'].items():
            lang_name = LANGUAGES.get(lang_code, {}).get('name', lang_code)
            flag = LANGUAGES.get(lang_code, {}).get('flag', '')
            stats_text += f"• {flag} {lang_name}: {count}\n"
        
        send_telegram_message(chat_id, stats_text)
    
    elif text == '/users' and str(user_id) == ADMIN_USER_ID:
        # قائمة المستخدمين للمالك
        stats = db.get_daily_stats()
        
        users_text = "👥 *آخر 10 مستخدمين:*\n\n"
        for i, user in enumerate(stats['recent_users'][:10], 1):
            last_seen = datetime.fromisoformat(
                user['last_seen'].replace('Z', '+00:00')
            ).strftime("%Y-%m-%d %H:%M")
            
            users_text += f"{i}. {user['first_name']} "
            if user.get('username'):
                users_text += f"(@{user['username']}) "
            
            users_text += f"\n   🆔: `{user['user_id']}` "
            users_text += f"| 🌍: {LANGUAGES.get(user.get('language', 'ar'), {}).get('name', 'ar')} "
            users_text += f"| 🕐: {last_seen}\n"
        
        send_telegram_message(chat_id, users_text)
    
    elif text == '/help':
        help_text = """
🆘 *مساعدة:*

🎮 *الأوامر:*
/start - بدء لعبة جديدة
/help - عرض هذه الرسالة

👑 *أوامر للمالك:*
/stats - عرض إحصائيات البوت
/users - عرض آخر المستخدمين

📱 *كيفية اللعب:*
1. اختر اللغة
2. اختر عدد الزجاجات
3. اختر عدد الفارغة
4. املأ الألوان باستخدام الأزرار
5. احصل على الحل
"""
        send_telegram_message(chat_id, help_text)
    
    else:
        # أي رسالة أخرى
        send_telegram_message(
            chat_id,
            "💡 أرسل /start لبدء لعبة جديدة أو /help للمساعدة"
        )
    
    return jsonify({"status": "message_processed"})

@app.route('/setwebhook')
def set_webhook():
    """تعيين webhook يدوياً"""
    if not TELEGRAM_TOKEN:
        return "❌ TELEGRAM_TOKEN غير مضبوط", 400
    
    import requests
    webhook_url = f"https://{request.host}/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        return f"""
        <div style="text-align:center;padding:50px;font-family:Arial">
            <h1>✅ Webhook تم تعيينه</h1>
            <p><strong>الرابط:</strong> {webhook_url}</p>
            <p><strong>الرد:</strong> {response.text}</p>
            <a href="/">🏠 العودة للصفحة الرئيسية</a>
        </div>
        """
    except Exception as e:
        return f"❌ خطأ: {e}", 500

@app.route('/admin')
def admin_dashboard():
    """لوحة تحكم المالك"""
    stats = db.get_daily_stats()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 لوحة تحكم البوت</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 20px; margin: 15px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .stat-box {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .user-list {{ max-height: 400px; overflow-y: auto; }}
            .user-item {{ border-bottom: 1px solid #eee; padding: 10px; }}
            .user-item:last-child {{ border-bottom: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 لوحة تحكم بوت فرز الألوان</h1>
            
            <div class="card">
                <h2>📊 نظرة عامة</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number">{stats['total_users']}</div>
                        <div class="stat-label">إجمالي المستخدمين</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{stats['active_today']}</div>
                        <div class="stat-label">النشطون اليوم</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{stats['new_today']}</div>
                        <div class="stat-label">الجدد اليوم</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🌍 توزيع اللغات</h2>
    """
    
    for lang_code, count in stats['languages'].items():
        lang_name = LANGUAGES.get(lang_code, {}).get('name', lang_code)
        flag = LANGUAGES.get(lang_code, {}).get('flag', '🌐')
        percentage = (count / stats['total_users'] * 100) if stats['total_users'] > 0 else 0
        
        html += f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between;">
                <span>{flag} {lang_name}</span>
                <span>{count} ({percentage:.1f}%)</span>
            </div>
            <div style="background: #e9ecef; height: 10px; border-radius: 5px; margin-top: 5px;">
                <div style="background: #007bff; width: {percentage}%; height: 100%; border-radius: 5px;"></div>
            </div>
        </div>
        """
    
    html += """
            </div>
            
            <div class="card">
                <h2>👥 آخر المستخدمين</h2>
                <div class="user-list">
    """
    
    for user in stats['recent_users'][:15]:
        last_seen = datetime.fromisoformat(
            user['last_seen'].replace('Z', '+00:00')
        ).strftime("%Y-%m-%d %H:%M")
        
        html += f"""
        <div class="user-item">
            <strong>{user['first_name']}</strong>
            <small>(@{user.get('username', 'N/A')})</small><br>
            <small>🆔: {user['user_id']} | 🌍: {LANGUAGES.get(user.get('language', 'ar'), {}).get('name', 'ar')} | 🕐: {last_seen}</small>
        </div>
        """
    
    html += """
                </div>
            </div>
            
            <div class="card">
                <h2>🔧 أدوات</h2>
                <p>
                    <a href="/setwebhook" style="color: #007bff; text-decoration: none;">🔄 تعيين Webhook</a> | 
                    <a href="/" style="color: #007bff; text-decoration: none;">🏠 الصفحة الرئيسية</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting Water Sort Bot on port {port}")
    logger.info(f"👑 Admin ID: {ADMIN_USER_ID}")
    logger.info(f"🌍 Supported languages: {len(LANGUAGES)}")
    logger.info(f"🎨 Available colors: {len(COLOR_SYSTEM)}")
    app.run(host='0.0.0.0', port=port)
