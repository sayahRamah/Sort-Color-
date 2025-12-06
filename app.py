from flask import Flask, request, jsonify
import os
import logging
import json
from collections import deque

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# تخزين الجلسات
user_sessions = {}

# نظام الألوان الكامل
COLOR_SYSTEM = {
    # الأحمر بثلاث درجات
    'R1': '🔴',      # فاتح
    'R2': '🔴🔴',    # متوسط
    'R3': '🔴🔴🔴',  # غامق
    
    # الأزرق بثلاث درجات
    'B1': '🔵',
    'B2': '🔵🔵',
    'B3': '🔵🔵🔵',
    
    # الأخضر بثلاث درجات
    'G1': '🟢',
    'G2': '🟢🟢',
    'G3': '🟢🟢🟢',
    
    # الأصفر بثلاث درجات
    'Y1': '🟡',
    'Y2': '🟡🟡',
    'Y3': '🟡🟡🟡',
    
    # البنفسجي بثلاث درجات
    'P1': '🟣',
    'P2': '🟣🟣',
    'P3': '🟣🟣🟣',
    
    # البرتقالي بثلاث درجات
    'O1': '🟠',
    'O2': '🟠🟠',
    'O3': '🟠🟠🟠',
    
    # ألوان إضافية
    'BLACK': '⚫',
    'WHITE': '⚪',
    'BROWN': '🟤',
    
    # خاص
    'EMPTY': '⬜',
    'UNKNOWN': '❓'
}

# تحويل عكسي
EMOJI_TO_CODE = {v: k for k, v in COLOR_SYSTEM.items()}

class PuzzleSolver:
    """حل اللغز مع علامات استفهام"""
    
    def __init__(self, bottles):
        self.bottles = bottles
        self.num_bottles = len(bottles)
        self.capacity = 4
    
    def is_solved(self):
        """التحقق إذا كان اللغز محلولاً"""
        for bottle in self.bottles:
            colors = [c for c in bottle if c != 'EMPTY' and c != 'UNKNOWN']
            if colors and len(set(colors)) > 1:
                return False
        return True
    
    def can_pour(self, from_idx, to_idx):
        """التحقق من إمكانية الصب"""
        if from_idx == to_idx:
            return False
        
        from_bottle = self.bottles[from_idx]
        to_bottle = self.bottles[to_idx]
        
        # العثور على أول لون غير فارغ وغير مجهول
        source_color = None
        for color in from_bottle:
            if color != 'EMPTY' and color != 'UNKNOWN':
                source_color = color
                break
        
        if not source_color:
            return False
        
        # التحقق من السعة في الزجاجة الهدف
        empty_count = sum(1 for c in to_bottle if c == 'EMPTY')
        if empty_count == 0:
            return False
        
        # العثور على لون الزجاجة الهدف
        target_color = None
        for color in to_bottle:
            if color != 'EMPTY' and color != 'UNKNOWN':
                target_color = color
                break
        
        # يمكن الصب إذا كانت فارغة أو نفس اللون
        return target_color is None or target_color == source_color
    
    def solve(self):
        """BFS للعثور على الحل"""
        if self.is_solved():
            return []
        
        initial_state = tuple(tuple(b) for b in self.bottles)
        queue = deque([(self.bottles, [])])
        visited = {initial_state}
        
        while queue:
            current_state, path = queue.popleft()
            
            solver = PuzzleSolver([list(b) for b in current_state])
            if solver.is_solved():
                return path
            
            # توليد الحركات الممكنة
            for from_idx in range(solver.num_bottles):
                for to_idx in range(solver.num_bottles):
                    if solver.can_pour(from_idx, to_idx):
                        new_state = [list(b) for b in current_state]
                        
                        # تنفيذ الصب
                        source_color = None
                        for i in range(solver.capacity):
                            if new_state[from_idx][i] != 'EMPTY' and new_state[from_idx][i] != 'UNKNOWN':
                                source_color = new_state[from_idx][i]
                                new_state[from_idx][i] = 'EMPTY'
                                break
                        
                        # إضافة إلى الهدف
                        for i in range(solver.capacity-1, -1, -1):
                            if new_state[to_idx][i] == 'EMPTY':
                                new_state[to_idx][i] = source_color
                                break
                        
                        state_tuple = tuple(tuple(b) for b in new_state)
                        if state_tuple not in visited:
                            visited.add(state_tuple)
                            queue.append((state_tuple, path + [(from_idx, to_idx)]))
        
        return []

@app.route('/')
def home():
    return """
    <div style="text-align:center;padding:50px;font-family:Arial">
        <h1>🧪 بوت حل لغز فرز الألوان المتطور</h1>
        <p>🎨 <strong>نظام الدرجات اللونية + علامات استفهام</strong></p>
        <p>✅ يعمل 100% - بدون مشاكل صور</p>
        <p>📱 افتح تلجرام وأرسل <code>/start</code></p>
    </div>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    if not TELEGRAM_TOKEN:
        return jsonify({"error": "No token"}), 400
    
    import requests
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "no message"})
    
    message = data['message']
    chat_id = str(message['chat']['id'])
    text = message.get('text', '').strip()
    
    def send_message(text, keyboard=None):
        message_data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        if keyboard:
            message_data['reply_markup'] = keyboard
        
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            json=message_data
        )
    
    def show_color_guide():
        guide = """
🎨 *دليل الألوان المتاح:*

🔴 *الدرجات الحمراء:*
🔴   - أحمر فاتح
🔴🔴 - أحمر متوسط  
🔴🔴🔴 - أحمر غامق

🔵 *الدرجات الزرقاء:*
🔵   - أزرق فاتح
🔵🔵 - أزرق متوسط
🔵🔵🔵 - أزرق غامق

🟢 *الدرجات الخضراء:*
🟢   - أخضر فاتح
🟢🟢 - أخضر متوسط
🟢🟢🟢 - أخضر غامق

🎭 *ألوان أخرى:*
🟡 🟣 🟠 ⚫ ⚪ 🟤

⬜ *فارغ:* ⬜
❓ *غير معروف:* ❓

📝 *مثال:* `🔴,🔴🔴,❓,⬜`
        """
        send_message(guide)
    
    # تهيئة الجلسة
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            'step': 0,
            'bottles': [],
            'total_bottles': 0,
            'solution': None
        }
    
    session = user_sessions[chat_id]
    
    # معالجة الأوامر
    if text == '/start':
        session.update({
            'step': 1,
            'bottles': [],
            'total_bottles': 0,
            'solution': None
        })
        
        welcome = """
🧩 *مرحباً بكم في بوت حل لغز الألوان المتطور!*

✨ *المميزات الجديدة:*
✅ ثلاث درجات لكل لون
✅ علامات استفهام للألوان المخفية
✅ نظام حل ذكي مع ❓

📚 *دليل الألوان:* أرسل `/colors`
❓ *المساعدة:* أرسل `/help`

🔢 *الآن، كم عدد الزجاجات؟ (5-20)*
        """
        send_message(welcome)
    
    elif text == '/colors':
        show_color_guide()
    
    elif text == '/help':
        help_text = """
🆘 *مساعدة سريعة:*

🎮 *كيفية اللعب:*
1. أدخل عدد الزجاجات
2. أدخل كل زجاجة (4 خانات)
3. استخدم ❓ للون غير المعروف

📝 *التنسيق:*
`لون,لون,لون,لون`
مثال: `🔴,🔴🔴,❓,⬜`

🎨 *عرض الألوان:* `/colors`
🔄 *بدء جديد:* `/start`
        """
        send_message(help_text)
    
    elif session['step'] == 1:  # انتظار عدد الزجاجات
        try:
            num = int(text)
            if 5 <= num <= 20:
                session['total_bottles'] = num
                session['step'] = 2
                session['current_bottle'] = 1
                
                # عرض لوحة الألوان
                show_color_guide()
                send_message(f"\n✅ تم تحديد *{num} زجاجة*\n\n*الزجاجة 1:*\nأدخل 4 خانات (مثال: `🔴,🔴🔴,❓,⬜`)")
            else:
                send_message("❌ الرجاء إدخال رقم بين *5 و 20*")
        except:
            send_message("❌ الرجاء إدخال *رقم صحيح*")
    
    elif session['step'] == 2:  # استقبال الزجاجات
        try:
            # تقسيم المدخلات
            parts = [p.strip() for p in text.split(',')]
            if len(parts) != 4:
                send_message("❌ يجب إدخال *4 عناصر* مفصولة بفواصل\nمثال: `🔴,🔴🔴,❓,⬜`")
                return jsonify({"status": "invalid"})
            
            # تحقق من صحة الألوان
            valid_colors = list(COLOR_SYSTEM.values()) + ['?', '؟', '_']
            converted = []
            
            for part in parts:
                if part in ['?', '؟']:
                    converted.append('UNKNOWN')
                elif part in ['_', '⬜', 'EMPTY']:
                    converted.append('EMPTY')
                elif part in valid_colors:
                    # البحث عن الكود المناسب
                    for code, emoji in COLOR_SYSTEM.items():
                        if emoji == part:
                            converted.append(code)
                            break
                    else:
                        converted.append('UNKNOWN')
                else:
                    send_message(f"❌ لون غير معروف: `{part}`\nاستخدم `/colors` لعرض الألوان المتاحة")
                    return jsonify({"status": "invalid"})
            
            # حفظ الزجاجة
            session['bottles'].append(converted)
            
            if len(session['bottles']) < session['total_bottles']:
                next_num = len(session['bottles']) + 1
                send_message(f"✅ تم حفظ الزجاجة *{len(session['bottles'])}*\n\n*الزجاجة {next_num}:*")
            else:
                # تم جمع جميع الزجاجات
                session['step'] = 3
                
                # عرض الملخص
                summary = "📊 *ملخص اللغز:*\n\n"
                for i, bottle in enumerate(session['bottles'], 1):
                    emoji_bottle = [COLOR_SYSTEM.get(c, '❓') for c in bottle]
                    summary += f"{i}. {' | '.join(emoji_bottle)}\n"
                
                summary += "\n🔍 *جاري البحث عن الحل...* ⏳"
                send_message(summary)
                
                # محاولة الحل
                try:
                    solver = PuzzleSolver(session['bottles'])
                    solution = solver.solve()
                    
                    if solution:
                        session['solution'] = solution
                        
                        # تحويل الحل إلى خطوات مفهومة
                        steps = []
                        for step_num, (from_idx, to_idx) in enumerate(solution, 1):
                            from_bottle = session['bottles'][from_idx]
                            to_bottle = session['bottles'][to_idx]
                            
                            # العثور على اللون المراد صبه
                            color = None
                            for c in from_bottle:
                                if c != 'EMPTY' and c != 'UNKNOWN':
                                    color = COLOR_SYSTEM.get(c, '❓')
                                    break
                            
                            steps.append(f"{step_num}. صب {color} من #{from_idx+1} → #{to_idx+1}")
                        
                        # إرسال الحل
                        solution_text = f"""
🎉 *تم إيجاد حل!*

⏱️ *عدد الخطوات:* {len(solution)}

📋 *الخطوات:*
{chr(10).join(steps[:10])}
                        """
                        
                        if len(solution) > 10:
                            solution_text += f"\n📄 *وهناك {len(solution)-10} خطوات إضافية*"
                        
                        solution_text += "\n\n🔄 *لعبة جديدة:* `/start`"
                        
                        send_message(solution_text)
                    else:
                        send_message("❌ *لم أتمكن من إيجاد حل* لهذا اللغز.\nتحقق من المدخلات وحاول مرة أخرى.")
                
                except Exception as e:
                    logger.error(f"Error solving: {e}")
                    send_message("⚠️ حدث خطأ أثناء البحث عن الحل. جرب إدخال اللغز مرة أخرى.")
                
        except Exception as e:
            logger.error(f"Error processing bottle: {e}")
            send_message("❌ حدث خطأ. تأكد من التنسيق:\n`🔴,🔴🔴,❓,⬜`")
    
    else:
        send_message("💡 أرسل `/start` للبدء أو `/help` للمساعدة")
    
    return jsonify({"status": "processed"})

@app.route('/setwebhook')
def set_webhook():
    if not TELEGRAM_TOKEN:
        return "TELEGRAM_TOKEN not set", 400
    
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

@app.route('/colors_demo')
def colors_demo():
    """عرض جميع الألوان"""
    html = "<h1>🎨 نظام الألوان</h1><div style='font-size: 24px; line-height: 2;'>"
    
    for code, emoji in COLOR_SYSTEM.items():
        html += f"<div>{emoji} → {code}</div>"
    
    html += "</div>"
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting Advanced Water Sort Bot on port {port}")
    app.run(host='0.0.0.0', port=port)
