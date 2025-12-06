from flask import Flask, request, jsonify
import logging
import os
import json

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "service": "Water Sort Puzzle Bot",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook (POST)",
            "setwebhook": "/setwebhook"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram"""
    try:
        data = request.get_json()
        logger.info(f"Received update_id: {data.get('update_id') if data else 'No data'}")
        
        # رد بسيط للتأكيد
        return jsonify({"status": "received"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """Set webhook manually"""
    try:
        token = os.environ.get('TELEGRAM_TOKEN')
        if not token:
            return "TELEGRAM_TOKEN not set", 400
        
        # الحصول على رابط التطبيق
        import requests
        webhook_url = f"https://{request.host}/webhook"
        
        response = requests.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": webhook_url}
        )
        
        result = {
            "webhook_url": webhook_url,
            "telegram_response": response.json() if response.text else response.text,
            "status_code": response.status_code
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    """Test endpoint to verify imports"""
    try:
        # اختبار جميع الاستيرادات
        import cv2
        import numpy as np
        from PIL import Image
        import telegram
        import flask
        
        return jsonify({
            "status": "success",
            "imports": {
                "opencv": cv2.__version__,
                "numpy": np.__version__,
                "pillow": Image.__version__,
                "telegram": "OK",
                "flask": "OK"
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
