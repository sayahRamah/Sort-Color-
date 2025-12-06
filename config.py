import os
from dotenv import load_dotenv

load_dotenv()

# إعدادات تلجرام
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('RENDER_WEBHOOK_URL') + '/webhook'

# إعدادات التطبيق
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# إعدادات اللغز
MIN_BOTTLES = 5
MAX_BOTTLES = 20
MIN_COLORS = 4
MAX_COLORS = 15
BOTTLE_CAPACITY = 4
COLOR_REPETITION = 4  # كل لون يظهر 4 مرات

# إعدادات الأداء
MAX_SOLUTION_STEPS = 100
MAX_PROCESSING_TIME = 30  # ثانية
MAX_IMAGE_SIZE = (1024, 1024)

# مسارات الملفات
TEMP_DIR = 'temp'
os.makedirs(TEMP_DIR, exist_ok=True)

# الألوان المتاحة مع رموز إيموجي
COLOR_PALETTE = {
    'RED': ('🔴', '#FF0000'),
    'ORANGE': ('🟠', '#FF8800'),
    'YELLOW': ('🟡', '#FFFF00'),
    'GREEN': ('🟢', '#00FF00'),
    'BLUE': ('🔵', '#0000FF'),
    'PURPLE': ('🟣', '#8800FF'),
    'PINK': ('🩷', '#FF66B2'),
    'BROWN': ('🟤', '#A52A2A'),
    'BLACK': ('⚫', '#000000'),
    'WHITE': ('⚪', '#FFFFFF'),
    'CYAN': ('💎', '#00FFFF'),
    'MAGENTA': ('💜', '#FF00FF'),
    'LIME': ('💚', '#00FF00'),
    'TEAL': ('💠', '#008080'),
    'LAVENDER': ('🌸', '#E6E6FA'),
}

# تجميع الألوان المتقاربة
COLOR_CLUSTERS = {
    'RED': ['#FF0000', '#CC0000', '#990000', '#FF6666', '#FF3333'],
    'ORANGE': ['#FF8800', '#FF6600', '#FF5500', '#FFAA00', '#FF7700'],
    'YELLOW': ['#FFFF00', '#CCCC00', '#FFFF66', '#FFFF33', '#FFEE00'],
    'GREEN': ['#00FF00', '#00CC00', '#00AA00', '#66FF66', '#33FF33'],
    'BLUE': ['#0000FF', '#0000CC', '#000099', '#6666FF', '#3333FF'],
    'PURPLE': ['#8800FF', '#6600CC', '#AA00FF', '#CC66FF', '#9933FF'],
}
