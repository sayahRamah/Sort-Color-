from flask import Flask, request, jsonify
import os
import sys
import logging
import tempfile
import uuid

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# إنشاء مجلد temp إذا لم يكن موجوداً
TEMP_DIR = 'temp'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
    logger.info(f"📁 Created temp directory: {TEMP_DIR}")

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
            .info-box {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                text-align: left;
                margin: 20px 0;
            }}
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
            <p>📸 <strong>ميزة جديدة:</strong> البوت يستقبل الصور الآن!</p>
            
            <div style="margin: 20px 0;">
                <a href="/setwebhook" class="btn">🎯 تعيين Webhook</a>
                <a href="/health" class="btn">🩺 فحص الصحة</a>
                <a href="/test" class="btn">🧪 اختبار المكتبات</a>
            </div>
            
            <div class="info-box">
                <h3>📋 حالة البوت:</h3>
                <ul>
                    <li>✅ يستقبل /start ويرد</li>
                    <li>✅ يستقبل الصور ويحفظها</li>
                    <li>⏳ جاري تطوير تحليل الصور</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3>🚀 كيفية الاختبار:</h3>
                <ol>
                    <li>افتح البوت في تلجرام</li>
                    <li>أرسل /start</li>
                    <li>أرسل صورة للغز</li>
                    <li>سيتلقى البوت الصورة ويخزنها</li>
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
        "service": "water-sort-bot",
        "features": {
            "receive_photos": True,
            "process_photos": "in_progress",
            "solve_puzzle": "coming_soon"
        }
    })

@app.route('/test')
def test():
    """اختبار المكتبات المثبتة"""
    results = {
        "flask": "✅",
        "python": sys.version.split()[0],
        "has_token": bool(TELEGRAM_TOKEN)
    }
    
    # اختبار requests
    try:
        import requests
        results["requests"] = "✅"
        results["requests_version"] = requests.__version__
    except ImportError as e:
        results["requests"] = f"❌ {str(e)}"
    
    # اختبار Pillow
    try:
        from PIL import Image, __version__ as pillow_version
        results["pillow"] = f"✅ v{pillow_version}"
        
        # اختبار إنشاء صورة
        test_image = Image.new('RGB', (10, 10), color='red')
        results["pillow_test"] = "✅ يمكن إنشاء صور"
    except ImportError as e:
        results["pillow"] = f"❌ {str(e)}"
        results["pillow_test"] = "❌ فشل"
    
    # اختبار telegram
    try:
        import telegram
        results["telegram_bot"] = "✅"
    except ImportError as e:
        results["telegram_bot"] = f"❌ {str(e)}"
    
    return jsonify(results)

def send_telegram_message(method, data):
    """إرسال رسالة لتلجرام"""
    if not TELEGRAM_TOKEN:
        logger.error("Cannot send message: TELEGRAM_TOKEN not set")
        return None
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Error sending telegram message: {e}")
        return None

def download_telegram_photo(file_id):
    """تحميل صورة من تلجرام"""
    try:
        import requests
        
        # الحصول على معلومات الملف
        file_info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
        file_info_response = requests.post(file_info_url, json={'file_id': file_id})
        file_info = file_info_response.json()
        
        if not file_info.get('ok'):
            logger.error(f"Failed to get file info: {file_info}")
            return None
        
        file_path = file_info['result']['file_path']
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        # تحميل الصورة
        photo_response = requests.get(file_url, timeout=30)
        
        if photo_response.status_code == 200:
            # حفظ الصورة مؤقتاً
            filename = f"{TEMP_DIR}/{uuid.uuid4()}.jpg"
            with open(filename, 'wb') as f:
                f.write(photo_response.content)
            
            logger.info(f"📸 Photo saved: {filename} ({len(photo_response.content)} bytes)")
            return filename
        else:
            logger.error(f"Failed to download photo: {photo_response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error downloading photo: {e}")
        return None

def analyze_image(image_path):
    """تحليل الصورة (نسخة أولية)"""
    try:
        from PIL import Image
        import os
        
        # فتح الصورة
        img = Image.open(image_path)
        
        # معلومات أساسية
        info = {
            "filename": os.path.basename(image_path),
            "size": os.path.getsize(image_path),
            "dimensions": img.size,
            "format": img.format,
            "mode": img.mode,
            "analysis": "جاري تطوير التحليل المتقدم..."
        }
        
        # إغلاق الصورة
        img.close()
        
        return {"success": True, "info": info}
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"success": False, "error": str(e)}

@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة رسائل تلجرام"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set")
        return jsonify({"error": "Token not set"}), 400
    
    try:
        data = request.get_json()
        logger.info(f"📩 Received update_id: {data.get('update_id')}")
        
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
                    'text': """🎮 *مرحباً بك في بوت حل لغز فرز الألوان!*

📸 *كيفية الاستخدام:*
1. التقط صورة للغز (سكرين شوت)
2. أرسلها للبوت
3. سأقوم بتحليلها وإيجاد الحل

🔧 *الميزات المتوفرة:*
✅ استقبال الصور
✅ حفظ الصور مؤقتاً
⏳ جاري تطوير تحليل الصور

*أرسل لي صورة الآن!* 🎯""",
                    'parse_mode': 'Markdown'
                }
                send_telegram_message('sendMessage', reply)
                logger.info(f"✅ Replied to /start for chat {chat_id}")
            
            # الرد على أي نص آخر
            elif text:
                reply = {
                    'chat_id': chat_id,
                    'text': "📸 *أرسل لي صورة للغز (سكرين شوت) وسأحله لك.*\n\nاستخدم /start لعرض التعليمات الكاملة.",
                    'parse_mode': 'Markdown'
                }
                send_telegram_message('sendMessage', reply)
            
            # معالجة الصور
            elif 'photo' in message:
                logger.info(f"📸 Processing photo from chat {chat_id}")
                
                # إرسال رسالة "جاري المعالجة"
                processing_msg = {
                    'chat_id': chat_id,
                    'text': "🔄 *جاري معالجة الصورة...*\n\nمن فضلك انتظر قليلاً ⏳",
                    'parse_mode': 'Markdown'
                }
                send_telegram_message('sendMessage', processing_msg)
                
                # اختيار الصورة الأعلى جودة (آخر عنصر)
                photos = message['photo']
                best_photo = photos[-1]
                file_id = best_photo['file_id']
                
                # تحميل الصورة
                downloaded_file = download_telegram_photo(file_id)
                
                if downloaded_file:
                    # تحليل الصورة
                    analysis_result = analyze_image(downloaded_file)
                    
                    if analysis_result['success']:
                        info = analysis_result['info']
                        
                        # إرسال نتيجة التحليل
                        reply_text = f"""✅ *تم استقبال الصورة بنجاح!*

📊 *معلومات الصورة:*
• الحجم: {info['size']:,} بايت
• الأبعاد: {info['dimensions'][0]} × {info['dimensions'][1]}
• النوع: {info['format']}

🔍 *حالة التحليل:*
{info['analysis']}

🎯 *المرحلة القادمة:* تطوير خوارزمية التعرف على الألوان والزجاجات."""
                        
                        reply = {
                            'chat_id': chat_id,
                            'text': reply_text,
                            'parse_mode': 'Markdown'
                        }
                        send_telegram_message('sendMessage', reply)
                        
                        # إرسال رسالة تشجيعية
                        encouragement = {
                            'chat_id': chat_id,
                            'text': "🎉 *عمل رائع!*\n\nالبوت الآن يتعلم التعرف على الألوان في الصور. جرب إرسال صور مختلفة لمساعدته على التعلم! 🧠",
                            'parse_mode': 'Markdown'
                        }
                        send_telegram_message('sendMessage', encouragement)
                        
                    else:
                        # في حالة فشل التحليل
                        reply = {
                            'chat_id': chat_id,
                            'text': f"❌ *حدث خطأ في تحليل الصورة*\n\nالخطأ: {analysis_result['error']}\n\nحاول بإرسال صورة أوضح.",
                            'parse_mode': 'Markdown'
                        }
                        send_telegram_message('sendMessage', reply)
                else:
                    # في حالة فشل التحميل
                    reply = {
                        'chat_id': chat_id,
                        'text': "❌ *تعذر تحميل الصورة*\n\nحاول مرة أخرى أو أرسل صورة مختلفة.",
                        'parse_mode': 'Markdown'
                    }
                    send_telegram_message('sendMessage', reply)
        
        return jsonify({"status": "processed"})
        
    except Exception as e:
        logger.error(f"❌ Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/setwebhook')
def set_webhook():
    """تعيين webhook"""
    if not TELEGRAM_TOKEN:
        return """
        <div style="text-align:center;padding:50px">
            <h2 style="color:red">❌ TELEGRAM_TOKEN غير مضبوط</h2>
            <p>أضف هذا المتغير في Render Environment:</p>
            <code style="background:#f0f0f0;padding:10px;display:block;margin:10px">
                TELEGRAM_TOKEN = توكن_البوت_الخاص_بك
            </code>
            <p><a href="/" style="color:blue">← العودة للصفحة الرئيسية</a></p>
        </div>
        """, 400
    
    try:
        import requests
        webhook_url = f"https://{request.host}/webhook"
        
        # تعيين Webhook
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": webhook_url},
            timeout=10
        )
        
        result = response.json()
        
        if result.get('ok'):
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:green">✅ تم تعيين Webhook بنجاح!</h2>
                <p><strong>الرابط:</strong> {webhook_url}</p>
                <p><strong>الحالة:</strong> {result.get('description', 'Success')}</p>
                <p>✅ البوت جاهز لاستقبال الرسائل والصور</p>
                <div style="margin:20px">
                    <a href="/" style="background:#4CAF50;color:white;padding:10px20px;text-decoration:none">🏠 الرئيسية</a>
                </div>
            </div>
            """
        else:
            return f"""
            <div style="text-align:center;padding:50px">
                <h2 style="color:orange">⚠️ مشكلة في تعيين Webhook</h2>
                <p>الخطأ: {result.get('description', 'Unknown error')}</p>
                <p><a href="/" style="color:blue">← العودة</a></p>
            </div>
            """
            
    except ImportError:
        return """
        <div style="text-align:center;padding:50px">
            <h2 style="color:red">❌ مكتبة requests غير مثبتة</h2>
            <p>تأكد من وجودها في requirements.txt</p>
            <p><a href="/test" style="color:blue">← اختبار المكتبات</a></p>
        </div>
        """, 500
    except Exception as e:
        return f"""
        <div style="text-align:center;padding:50px">
            <h2 style="color:red">❌ خطأ</h2>
            <p>{str(e)}</p>
            <p><a href="/" style="color:blue">← العودة</a></p>
        </div>
        """, 500

@app.route('/cleanup')
def cleanup_temp():
    """تنظيف الملفات المؤقتة"""
    import glob
    import time
    
    files = glob.glob(f"{TEMP_DIR}/*")
    deleted_count = 0
    
    current_time = time.time()
    for file in files:
        file_age = current_time - os.path.getmtime(file)
        if file_age > 3600:  # حذف الملفات الأقدم من ساعة
            os.remove(file)
            deleted_count += 1
    
    return jsonify({
        "deleted_files": deleted_count,
        "remaining_files": len(glob.glob(f"{TEMP_DIR}/*"))
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting Water Sort Bot on port {port}")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"🔑 TELEGRAM_TOKEN: {'✅ Set' if TELEGRAM_TOKEN else '❌ Not set'}")
    app.run(host='0.0.0.0', port=port)
