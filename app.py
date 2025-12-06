from flask import Flask, request, jsonify
import os
import sys
import logging

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

@app.route('/')
def home():
    has_token = "✅" if TELEGRAM_TOKEN else "❌"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Water Sort Bot</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: #f0f0f0;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{ color: #333; }}
            .btn {{
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                margin: 10px;
                border-radius: 5px;
                text-decoration: none;
            }}
            .token-status {{ font-weight: bold; }}
            .success {{ color: green; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 بوت حل لغز فرز الألوان</h1>
            
            <div class="token-status">
                TELEGRAM_TOKEN: {has_token}
                {'' if TELEGRAM_TOKEN else '<p class="error">❌ الرجاء إضافة TELEGRAM_TOKEN في Render</p>'}
            </div>
            
            <p class="success">✅ التطبيق يعمل بنجاح!</p>
            
            <div style="margin: 20px 0;">
                <a href="/setwebhook" class="btn">🎯 تعيين Webhook</a>
                <a href="/health" class="btn">🩺 فحص الصحة</a>
                <a href="/test" class="btn">🧪 اختبار المكتبات</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: left;">
                <h3>📋 خطوات التشغيل:</h3>
                <ol>
                    <li>إضافة TELEGRAM_TOKEN في Render Environment</li>
                    <li>فتح /setwebhook لتعيين Webhook</li>
                    <li>فتح البوت في تلجرام وإرسال /start</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy" if TELEGRAM_TOKEN else "missing_token",
        "has_token": bool(TELEGRAM_TOKEN),
        "service": "water-sort-bot"
    })

@app.route('/test')
def test():
    """اختبار المكتبات"""
    import json
    results = {
        "flask": "✅",
        "requests": "❌",
        "telegram_bot": "❌",
        "python": sys.version.split()[0],
        "has_token": bool(TELEGRAM_TOKEN)
    }
    
    try:
        import requests
        results["requests"] = "✅"
    except:
        pass
    
    try:
        import telegram
        results["telegram_bot"] = "✅"
    except:
        pass
    
    return jsonify(results)

@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة رسائل تلجرام"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set")
        return jsonify({"error": "Token not set"}), 400
    
    try:
        data = request.get_json()
        logger.info(f"📩 Received: {data}")
        
        if not data:
            return jsonify({"status": "no data"})
        
        # معالجة رسالة المستخدم
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # الرد على /start
            if text == '/start':
                reply = {
                    'chat_id': chat_id,
                    'text': "🎮 *مرحباً بك في بوت حل لغز فرز الألوان!*\n\nأرسل لي صورة للغز (سكرين شوت) وسأحله لك.\n\n📸 *كيفية الاستخدام:*\n1. التقط صورة للغز\n2. أرسلها للبوت\n3. انتظر الحل",
                    'parse_mode': 'Markdown'
                }
                send_telegram_message('sendMessage', reply)
                logger.info(f"✅ Replied to /start for chat {chat_id}")
            
            # الرد على أي نص آخر
            elif text:
                reply = {
                    'chat_id': chat_id,
                    'text': "📸 أرسل لي صورة للغز (سكرين شوت) وسأحله لك.\n\nيمكنك استخدام /start لعرض التعليمات.",
                    'parse_mode': 'Markdown'
                }
                send_telegram_message('sendMessage', reply)
        
        return jsonify({"status": "processed"})
        
    except Exception as e:
        logger.error(f"❌ Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

def send_telegram_message(method, data):
    """إرسال رسالة لتلجرام"""
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    response = requests.post(url, json=data)
    return response.json()

@app.route('/setwebhook')
def set_webhook():
    """تعيين webhook"""
    if not TELEGRAM_TOKEN:
        return """
        <div style="text-align:center;padding:50px">
            <h2 class="error">❌ TELEGRAM_TOKEN غير مضبوط</h2>
            <p>أضف هذا المتغير في Render Environment:</p>
            <code style="background:#f0f0f0;padding:10px;display:block;margin:10px">
                TELEGRAM_TOKEN = توكن_البوت_الخاص_بك
            </code>
            <p><a href="/" class="btn">العودة</a></p>
        </div>
        """, 400
    
    try:
        import requests
        webhook_url = f"https://{request.host}/webhook"
        
        # تعيين Webhook
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        
        result = response.json()
        
        if result.get('ok'):
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:green">✅ تم تعيين Webhook بنجاح!</h2>
                <p><strong>الرابط:</strong> {webhook_url}</p>
                <p><strong>الحالة:</strong> {result.get('description', 'Success')}</p>
                <p>الآن افتح البوت في تلجرام وأرسل <code>/start</code></p>
                <p><a href="/" class="btn">🏠 الرئيسية</a></p>
            </div>
            """
        else:
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:orange">⚠️ مشكلة في تعيين Webhook</h2>
                <p>الخطأ: {result.get('description', 'Unknown error')}</p>
                <p><a href="/" class="btn">العودة</a></p>
            </div>
            """
            
    except ImportError:
        return """
        <div style="text-align:center;padding:50px">
            <h2 class="error">❌ مكتبة requests غير مثبتة</h2>
            <p>تأكد من وجودها في requirements.txt</p>
            <p><a href="/test">اختبار المكتبات</a></p>
        </div>
        """, 500

@app.route('/send_test_message')
def send_test_message():
    """إرسال رسالة تجريبية"""
    if not TELEGRAM_TOKEN:
        return "Token not set", 400
    
    try:
        import requests
        # الحصول على chat_id (يجب أن تكون قد أرسلت /start أولاً)
        # هذا للاختبار فقط
        return "Test endpoint - تحتاج chat_id للاختبار"
    except:
        return "Requests not installed", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting bot on port {port}")
    logger.info(f"🔑 TELEGRAM_TOKEN: {'Set' if TELEGRAM_TOKEN else 'Not set'}")
    app.run(host='0.0.0.0', port=port)
