from flask import Flask, request, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Water Sort Bot</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                color: #333;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                max-width: 800px;
                margin: 0 auto;
            }
            h1 { color: #667eea; }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 12px 24px;
                margin: 10px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
            }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 بوت حل لغز فرز الألوان</h1>
            <p class="success">✅ التطبيق يعمل بنجاح!</p>
            <p>ارسل /start في تلجرام للبدء.</p>
            
            <div style="margin: 30px 0;">
                <a href="/setwebhook" class="btn">🎯 تعيين Webhook</a>
                <a href="/health" class="btn">🩺 فحص الصحة</a>
                <a href="/test" class="btn">🧪 اختبار المكتبات</a>
            </div>
            
            <div style="text-align: left; background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h3>📊 حالة الخدمة:</h3>
                <ul>
                    <li>✅ Flask: جاهز</li>
                    <li>✅ Gunicorn: يعمل</li>
                    <li>📡 Webhook: <a href="/setwebhook">تحقق الآن</a></li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "water-sort-bot",
        "python_version": sys.version.split()[0]
    })

@app.route('/test')
def test():
    """اختبار المكتبات المثبتة"""
    results = {
        "flask": "✅",
        "gunicorn": "✅",
        "python": sys.version.split()[0]
    }
    
    # اختبار requests
    try:
        import requests
        results["requests"] = "✅"
    except ImportError:
        results["requests"] = "❌ غير مثبت"
    
    # اختبار Pillow
    try:
        from PIL import Image
        results["pillow"] = "✅"
    except ImportError:
        results["pillow"] = "❌ غير مثبت"
    
    # اختبار python-telegram-bot
    try:
        import telegram
        results["telegram_bot"] = "✅"
    except ImportError:
        results["telegram_bot"] = "❌ غير مثبت"
    
    return jsonify(results)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram"""
    data = request.get_json() or {}
    print(f"📩 Telegram webhook received: {data.get('update_id', 'No ID')}")
    return jsonify({"status": "received", "update_id": data.get('update_id')})

@app.route('/setwebhook')
def set_webhook():
    """تعيين webhook لتلجرام"""
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token:
        return """
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: red;">❌ TELEGRAM_TOKEN غير مضبوط</h2>
            <p>الرجاء إضافة متغير البيئة في Render:</p>
            <p style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                TELEGRAM_TOKEN = توكن_البوت_الخاص_بك
            </p>
            <a href="/" style="color: blue;">← العودة للصفحة الرئيسية</a>
        </div>
        """, 400
    
    try:
        import requests
    except ImportError:
        return """
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: red;">❌ مكتبة requests غير مثبتة</h2>
            <p>الرجاء تحديث requirements.txt لإضافة:</p>
            <p style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                requests==2.31.0
            </p>
            <a href="/test" style="color: blue;">← اختبار المكتبات</a>
        </div>
        """, 500
    
    webhook_url = f"https://{request.host}/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{token}/setWebhook",
            params={"url": webhook_url}
        )
        
        result = response.json() if response.text else {"text": response.text}
        
        return f"""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: green;">✅ تم تعيين Webhook</h1>
            <p><strong>الرابط:</strong> {webhook_url}</p>
            <p><strong>رد تلجرام:</strong> {result}</p>
            <div style="margin-top: 30px;">
                <a href="/" class="btn">🏠 الرئيسية</a>
                <a href="/test" class="btn">🧪 اختبار المكتبات</a>
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: red;">❌ خطأ في تعيين Webhook</h1>
            <p>{str(e)}</p>
            <a href="/" class="btn">← العودة</a>
        </div>
        """, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Water Sort Bot on port {port}")
    print(f"🐍 Python version: {sys.version}")
    app.run(host='0.0.0.0', port=port)
