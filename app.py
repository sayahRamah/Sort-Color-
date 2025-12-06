from flask import Flask, request
import logging
import os

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>🤖 Water Sort Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f0f0f0;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }
                h1 {
                    color: #333;
                }
                .status {
                    color: green;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 بوت حل لغز فرز الألوان</h1>
                <p class="status">✅ التطبيق يعمل بنجاح!</p>
                <p>هذا البوت يحل لغز Water Sort Puzzle تلقائياً.</p>
                <p>افتح تلجرام وابحث عن البوت للبدء.</p>
                <hr>
                <p>الإصدار: 1.0.0</p>
                <p>المطور: Water Sort Bot Team</p>
            </div>
        </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة webhook من تلجرام"""
    try:
        data = request.get_json()
        if data:
            logger.info(f"Received update: {data}")
            return 'OK'
        return 'No data', 400
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return 'Error', 500

@app.route('/health')
def health():
    """فحص صحة التطبيق"""
    return {'status': 'healthy', 'service': 'water-sort-bot'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
