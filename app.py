from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Water Sort Bot",
        "message": "التطبيق يعمل بنجاح!",
        "endpoints": ["/health", "/webhook", "/setwebhook"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json() or {}
    print(f"📩 Telegram webhook received: {data.get('update_id')}")
    return jsonify({"status": "ok"})

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        return "❌ TELEGRAM_TOKEN not set", 400
    
    import requests
    webhook_url = f"https://{request.host}/webhook"
    
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{token}/setWebhook",
            params={"url": webhook_url}
        )
        return f"""
        <h1>✅ Webhook Set Successfully</h1>
        <p>URL: {webhook_url}</p>
        <p>Response: {response.text}</p>
        <a href="/">Back to Home</a>
        """
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@app.route('/test')
def test():
    try:
        # اختبار الاستيرادات الأساسية
        from PIL import Image
        return jsonify({
            "Pillow": "✅ OK",
            "Flask": "✅ OK",
            "version": "1.0"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
