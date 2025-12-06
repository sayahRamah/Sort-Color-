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
                background: #f0f0f0;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 0 auto;
            }
            h1 { color: #333; }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                margin: 10px;
                border-radius: 5px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 بوت حل لغز فرز الألوان</h1>
            <p style="color: green; font-weight: bold;">✅ التطبيق يعمل بنجاح!</p>
            <p>المرحلة 1: التطبيق الأساسي يعمل</p>
            <p>المرحلة 2: معالجة الصور (قريباً)</p>
            
            <div style="margin: 20px 0;">
                <a href="/setwebhook" class="btn">🎯 تعيين Webhook</a>
                <a href="/health" class="btn">🩺 فحص الصحة</a>
                <a href="/test" class="btn">🧪 اختبار المكتبات</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>الإصدار:</strong> 1.0.0 (بدون معالجة صور)</p>
                <p><strong>الحالة:</strong> جاهز لاستقبال رسائل تلجرام</p>
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
        "stage": "1 - الأساسيات"
    })

@app.route('/test')
def test():
    """اختبار المكتبات المثبتة"""
    results = {}
    
    try:
        import flask
        results["flask"] = "✅"
    except:
        results["flask"] = "❌"
    
    try:
        import requests
        results["requests"] = "✅"
    except:
        results["requests"] = "❌"
    
    try:
        import telegram
        results["telegram_bot"] = "✅"
    except:
        results["telegram_bot"] = "❌"
    
    results["python"] = sys.version.split()[0]
    
    return jsonify(results)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint"""
    try:
        data = request.get_json() or {}
        
        # معالجة بسيطة للرسائل
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # هنا يمكنك إضافة ردود البوت
            # سنضيفها لاحقاً عندما يعمل البوت
            
        return jsonify({"status": "received"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/setwebhook')
def set_webhook():
    """تعيين webhook"""
    token = os.environ.get('TELEGRAM_TOKEN')
    
    if not token:
        return """
        <div style="text-align:center;padding:50px">
            <h2>❌ TELEGRAM_TOKEN غير مضبوط</h2>
            <p>أضف هذا المتغير في Render:</p>
            <code>TELEGRAM_TOKEN = توكن_البوت</code>
            <p><a href="/">العودة</a></p>
        </div>
        """, 400
    
    try:
        import requests
        webhook_url = f"https://{request.host}/webhook"
        
        response = requests.get(
            f"https://api.telegram.org/bot{token}/setWebhook",
            params={"url": webhook_url}
        )
        
        if response.status_code == 200:
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:green">✅ تم تعيين Webhook</h2>
                <p><strong>الرابط:</strong> {webhook_url}</p>
                <p><strong>الرد:</strong> {response.text}</p>
                <p><a href="/">العودة</a></p>
            </div>
            """
        else:
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:orange">⚠️ مشكلة في تعيين Webhook</h2>
                <p>رمز الخطأ: {response.status_code}</p>
                <p>الرد: {response.text}</p>
                <p><a href="/">العودة</a></p>
            </div>
            """
            
    except ImportError:
        return """
        <div style="text-align:center;padding:50px">
            <h2>❌ مكتبة requests غير مثبتة</h2>
            <p>تأكد من وجودها في requirements.txt</p>
            <p><a href="/test">اختبار المكتبات</a></p>
        </div>
        """, 500
    except Exception as e:
        return f"""
        <div style="text-align:center;padding:50px">
            <h2>❌ خطأ</h2>
            <p>{str(e)}</p>
            <p><a href="/">العودة</a></p>
        </div>
        """, 500

@app.route('/start', methods=['GET', 'POST'])
def start_bot():
    """محاكاة رد البوت على /start"""
    return jsonify({
        "message": "🎮 مرحباً! أنا بوت حل لغز فرز الألوان.",
        "instructions": "أرسل لي صورة للغز وسأحله لك.",
        "note": "ميزة معالجة الصور قريباً..."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
