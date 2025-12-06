from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
import pytz

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '5730502448')

# تخزين بسيط
user_stats = {}
user_sessions = {}

def send_to_admin(message):
    """إرسال رسالة للمالك"""
    if not TELEGRAM_TOKEN or not ADMIN_USER_ID:
        return
    
    try:
        import requests
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {
            'chat_id': ADMIN_USER_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, json=data, timeout=5)
    except:
        pass

def track_user_start(user_id, username, first_name):
    """تتبع بدء مستخدم جديد"""
    now = datetime.now(pytz.UTC)
    user_key = str(user_id)
    
    if user_key not in user_stats:
        user_stats[user_key] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'first_seen': now.isoformat(),
            'start_count': 1
        }
        
        # إرسال إشعار للمالك
        time_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        admin_msg = f"""
👤 *مستخدم جديد*
🆔: `{user_id}`
👤: {first_name}
📛: @{username if username else 'N/A'}
🕐: {time_str}
📊: إجمالي المستخدمين: {len(user_stats)}
        """
        send_to_admin(admin_msg)
    else:
        user_stats[user_key]['start_count'] += 1

@app.route('/')
def home():
    return """
    <div style="text-align:center;padding:50px">
        <h1>🤖 Water Sort Bot</h1>
        <p>✅ يعمل | 📊 المتتبعين: """ + str(len(user_stats)) + """</p>
        <p>👑 المالك: @Messilorian</p>
    </div>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "No token"}), 400
    
    import requests
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "no data"})
    
    message = data['message']
    chat_id = str(message['chat']['id'])
    user_id = message['from']['id']
    username = message['from'].get('username', '')
    first_name = message['from'].get('first_name', '')
    text = message.get('text', '').strip()
    
    def send_msg(text_content):
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json={'chat_id': chat_id, 'text': text_content, 'parse_mode': 'Markdown'}
        )
    
    if text == '/start':
        # تتبع المستخدم
        track_user_start(user_id, username, first_name)
        
        # لوحة اختيار اللغة المبسطة
        keyboard = {
            'inline_keyboard': [
                [{'text': '🇸🇦 العربية', 'callback_data': 'lang_ar'}],
                [{'text': '🇺🇸 English', 'callback_data': 'lang_en'}],
                [{'text': 'بدون ألوان - تجريبي', 'callback_data': 'lang_simple'}]
            ]
        }
        
        welcome = "🌍 اختر اللغة / Choose language"
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': welcome,
                'reply_markup': keyboard
            }
        )
    
    elif text == '/stats' and str(user_id) == ADMIN_USER_ID:
        stats_msg = f"""
📊 *الإحصائيات*
👥 المستخدمون: {len(user_stats)}
🕐 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        send_msg(stats_msg)
    
    return jsonify({"status": "ok"})

@app.route('/setwebhook')
def set_webhook():
    if not TELEGRAM_TOKEN:
        return "❌ TELEGRAM_TOKEN غير مضبوط", 400
    
    import requests
    webhook_url = f"https://{request.host}/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        return f"✅ Webhook set: {webhook_url}<br>Response: {response.text}"
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route('/admin')
def admin_page():
    """صفحة إدارة مبسطة"""
    html = f"""
    <html>
    <head><title>🤖 إدارة البوت</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>إحصائيات البوت</h1>
        <p>👥 إجمالي المستخدمين: {len(user_stats)}</p>
        <h3>آخر 5 مستخدمين:</h3>
    """
    
    users = list(user_stats.values())[-5:]
    for user in reversed(users):
        time = datetime.fromisoformat(user['first_seen'].replace('Z', '+00:00'))
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:5px;">
            👤 {user['first_name']} 
            <small>(@{user.get('username', 'N/A')})</small><br>
            🆔: {user['user_id']} | 🕐: {time.strftime('%Y-%m-%d %H:%M')}
        </div>
        """
    
    html += """
        <br>
        <a href="/">🏠 الرئيسية</a> | 
        <a href="/setwebhook">🔗 تعيين Webhook</a>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting bot on port {port}")
    logger.info(f"👑 Admin: {ADMIN_USER_ID}")
    app.run(host='0.0.0.0', port=port)
