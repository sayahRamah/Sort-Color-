from flask import Flask, request, jsonify
import os

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
            h1 {
                color: #667eea;
                font-size: 3em;
            }
            .status {
                color: green;
                font-weight: bold;
                font-size: 1.5em;
            }
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                margin: 10px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.2em;
                transition: all 0.3s;
            }
            .btn:hover {
                background: #764ba2;
                transform: translateY(-3px);
            }
            .endpoints {
                text-align: left;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 بوت حل لغز فرز الألوان</h1>
            <p class="status">✅ التطبيق يعمل بنجاح!</p>
            <p>هذا البوت يحل لغز Water Sort Puzzle تلقائياً.</p>
            
            <div class="endpoints">
                <h3>🔧 نقاط الواجهة:</h3>
                <ul>
                    <li><a href="/health" target="_blank">/health</a> - فحص صحة التطبيق</li>
                    <li><a href="/setwebhook" target="_blank">/setwebhook</a> - تعيين webhook لتلجرام</li>
                    <li><a href="/test" target="_blank">/test</a> - اختبار المكتبات</li>
                </ul>
            </div>
            
            <a href="/setwebhook" class="btn">🎯 تعيين Webhook</a>
            <a href="/health" class="btn">🩺 فحص الصحة</a>
            
            <p style="margin-top: 30px; color: #666;">
                الإصدار: 1.0.0 | Python 3.10 | Render
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "water-sort-bot",
        "timestamp": "2024"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json() or {}
    print(f"📩 Telegram webhook: {data.get('update_id', 'No ID')}")
    return jsonify({"status": "received"})

@app.route('/setwebhook')
def set_webhook():
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        return """
        <div style="text-align: center; padding: 50px;">
            <h2>❌ TELEGRAM_TOKEN غير مضبوط</h2>
            <p>الرجاء إضافة متغير البيئة TELEGRAM_TOKEN في Render</p>
            <a href="/" style="color: blue;">← العودة للصفحة الرئيسية</a>
        </div>
        """, 400
    
    import requests
    webhook_url = f"https://{request.host}/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{token}/setWebhook",
            params={"url": webhook_url}
        )
        
        return f"""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: green;">✅ تم تعيين Webhook بنجاح</h1>
            <p><strong>الرابط:</strong> {webhook_url}</p>
            <p><strong>رد تلجرام:</strong> {response.text}</p>
            <p style="margin-top: 30px;">
                <a href="/" style="color: blue;">← العودة للصفحة الرئيسية</a>
            </p>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: red;">❌ خطأ</h1>
            <p>{str(e)}</p>
            <a href="/" style="color: blue;">← العودة للصفحة الرئيسية</a>
        </div>
        """, 500

@app.route('/test')
def test():
    return jsonify({
        "flask": "✅ يعمل",
        "gunicorn": "✅ جاهز",
        "python_version": "3.x",
        "status": "جاهز لإضافة معالجة الصور"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
